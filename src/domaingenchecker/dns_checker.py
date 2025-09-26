"""
Asynchronous DNS resolution checker with caching and rate limiting.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import dns.asyncresolver
import dns.resolver
from asyncio_throttle import Throttler

from .config import DNSConfig

logger = logging.getLogger(__name__)


class DNSStatus(Enum):
    """DNS resolution status."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class DNSResult:
    """DNS resolution result."""

    domain: str
    status: DNSStatus
    ip_addresses: List[str]
    response_time: float
    error_message: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class DNSCache:
    """Simple in-memory DNS cache with TTL support."""

    def __init__(self, ttl: int = 3600):
        """Initialize DNS cache.

        Args:
            ttl: Time to live in seconds
        """
        self.ttl = ttl
        self._cache: Dict[str, DNSResult] = {}
        self._timestamps: Dict[str, float] = {}

    def get(self, domain: str) -> Optional[DNSResult]:
        """Get cached result for domain."""
        if domain in self._cache:
            if time.time() - self._timestamps[domain] < self.ttl:
                logger.debug(f"Cache hit for {domain}")
                return self._cache[domain]
            else:
                # Expired entry
                self._remove(domain)
        return None

    def set(self, domain: str, result: DNSResult) -> None:
        """Cache result for domain."""
        self._cache[domain] = result
        self._timestamps[domain] = time.time()
        logger.debug(f"Cached result for {domain}")

    def _remove(self, domain: str) -> None:
        """Remove domain from cache."""
        self._cache.pop(domain, None)
        self._timestamps.pop(domain, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._timestamps.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


class DNSChecker:
    """Asynchronous DNS checker with advanced features."""

    def __init__(self, config: DNSConfig):
        """Initialize DNS checker.

        Args:
            config: DNS configuration
        """
        self.config = config
        self.cache = DNSCache(ttl=3600)  # 1 hour cache by default

        # Set up DNS resolver
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = config.timeout
        self.resolver.lifetime = config.timeout * config.retries

        if config.nameservers:
            self.resolver.nameservers = config.nameservers
            logger.info(f"Using custom nameservers: {config.nameservers}")

        # Rate limiting
        self.throttler = Throttler(rate_limit=config.rate_limit)

        logger.info(
            f"Initialized DNSChecker with {config.concurrent_limit} concurrent limit"
        )

    async def check_domains(
        self, domains: List[str], use_cache: bool = True
    ) -> List[DNSResult]:
        """Check DNS resolution for multiple domains concurrently.

        Args:
            domains: List of domains to check
            use_cache: Whether to use cached results

        Returns:
            List of DNS results
        """
        logger.info(f"Checking DNS for {len(domains)} domains")

        # Create semaphore to limit concurrent connections
        semaphore = asyncio.Semaphore(self.config.concurrent_limit)

        # Prepare tasks
        tasks = [
            self._check_domain_with_semaphore(domain, semaphore, use_cache)
            for domain in domains
        ]

        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        dns_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Unexpected error in DNS check: {result}")
                # Create error result for failed task
                dns_results.append(
                    DNSResult(
                        domain="unknown",
                        status=DNSStatus.ERROR,
                        ip_addresses=[],
                        response_time=0.0,
                        error_message=str(result),
                    )
                )
            else:
                dns_results.append(result)

        logger.info(f"Completed DNS checks: {len(dns_results)} results")
        return dns_results

    async def _check_domain_with_semaphore(
        self, domain: str, semaphore: asyncio.Semaphore, use_cache: bool
    ) -> DNSResult:
        """Check single domain with semaphore for concurrency control."""
        async with semaphore:
            return await self.check_domain(domain, use_cache)

    async def check_domain(self, domain: str, use_cache: bool = True) -> DNSResult:
        """Check DNS resolution for a single domain.

        Args:
            domain: Domain to check
            use_cache: Whether to use cached results

        Returns:
            DNS result
        """
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(domain)
            if cached_result:
                return cached_result

        # Rate limiting
        async with self.throttler:
            start_time = time.time()

            try:
                # Perform DNS lookup
                result = await self._resolve_domain(domain)
                response_time = time.time() - start_time

                dns_result = DNSResult(
                    domain=domain,
                    status=DNSStatus.RESOLVED if result else DNSStatus.UNRESOLVED,
                    ip_addresses=result,
                    response_time=response_time,
                )

            except asyncio.TimeoutError:
                dns_result = DNSResult(
                    domain=domain,
                    status=DNSStatus.TIMEOUT,
                    ip_addresses=[],
                    response_time=time.time() - start_time,
                    error_message="DNS query timeout",
                )

            except Exception as e:
                dns_result = DNSResult(
                    domain=domain,
                    status=DNSStatus.ERROR,
                    ip_addresses=[],
                    response_time=time.time() - start_time,
                    error_message=str(e),
                )

        # Cache the result
        if use_cache:
            self.cache.set(domain, dns_result)

        logger.debug(
            f"DNS check for {domain}: {dns_result.status.value} ({dns_result.response_time:.3f}s)"
        )
        return dns_result

    async def _resolve_domain(self, domain: str) -> List[str]:
        """Resolve domain to IP addresses.

        Args:
            domain: Domain to resolve

        Returns:
            List of IP addresses
        """
        ip_addresses = []

        # Try A records first
        try:
            answers = await self.resolver.resolve(domain, "A")
            ip_addresses.extend([str(rdata) for rdata in answers])
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            # These are expected DNS resolution failures, continue to IPv6 attempt
            pass
        except Exception as e:
            logger.debug(f"Error resolving A record for {domain}: {e}")

        # Try AAAA records (IPv6) if no A records found
        if not ip_addresses:
            try:
                answers = await self.resolver.resolve(domain, "AAAA")
                ip_addresses.extend([str(rdata) for rdata in answers])
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                # Expected DNS resolution failures for IPv6, no action needed
                pass
            except Exception as e:
                logger.debug(f"Error resolving AAAA record for {domain}: {e}")

        return ip_addresses

    async def check_domain_advanced(self, domain: str) -> Dict[str, List[str]]:
        """Perform advanced DNS checks for multiple record types.

        Args:
            domain: Domain to check

        Returns:
            Dictionary of record types and their values
        """
        record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]
        results = {}

        for record_type in record_types:
            try:
                answers = await self.resolver.resolve(domain, record_type)
                results[record_type] = [str(rdata) for rdata in answers]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                results[record_type] = []
            except Exception as e:
                logger.debug(f"Error resolving {record_type} record for {domain}: {e}")
                results[record_type] = []

        return results

    def get_statistics(self) -> Dict[str, int]:
        """Get DNS checker statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "cache_size": self.cache.size(),
            "cache_ttl": self.cache.ttl,
            "concurrent_limit": self.config.concurrent_limit,
            "timeout": self.config.timeout,
            "retries": self.config.retries,
        }

    def clear_cache(self) -> None:
        """Clear DNS cache."""
        self.cache.clear()
        logger.info("DNS cache cleared")

    async def health_check(self) -> bool:
        """Perform health check by resolving a known domain.

        Returns:
            True if DNS resolution is working
        """
        try:
            result = await self.check_domain("google.com", use_cache=False)
            return result.status == DNSStatus.RESOLVED
        except Exception as e:
            logger.error(f"DNS health check failed: {e}")
            return False
