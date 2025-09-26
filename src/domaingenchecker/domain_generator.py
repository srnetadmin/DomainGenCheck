"""
Advanced domain name variation generator for typosquatting detection.
"""

import logging
import random
import string
from typing import Dict, Generator, List, Set
from urllib.parse import urlparse

import tldextract

from .config import GeneratorConfig


logger = logging.getLogger(__name__)


class DomainGenerator:
    """Advanced domain variation generator using multiple typosquatting techniques."""
    
    # QWERTY keyboard layout for realistic typos
    KEYBOARD_LAYOUT = {
        'q': ['w', 'a'],
        'w': ['q', 'e', 's'],
        'e': ['w', 'r', 'd'],
        'r': ['e', 't', 'f'],
        't': ['r', 'y', 'g'],
        'y': ['t', 'u', 'h'],
        'u': ['y', 'i', 'j'],
        'i': ['u', 'o', 'k'],
        'o': ['i', 'p', 'l'],
        'p': ['o', 'l'],
        'a': ['q', 's', 'z'],
        's': ['a', 'd', 'w', 'z', 'x'],
        'd': ['s', 'f', 'e', 'x', 'c'],
        'f': ['d', 'g', 'r', 'c', 'v'],
        'g': ['f', 'h', 't', 'v', 'b'],
        'h': ['g', 'j', 'y', 'b', 'n'],
        'j': ['h', 'k', 'u', 'n', 'm'],
        'k': ['j', 'l', 'i', 'm'],
        'l': ['k', 'o', 'p'],
        'z': ['a', 's', 'x'],
        'x': ['z', 'c', 's', 'd'],
        'c': ['x', 'v', 'd', 'f'],
        'v': ['c', 'b', 'f', 'g'],
        'b': ['v', 'n', 'g', 'h'],
        'n': ['b', 'm', 'h', 'j'],
        'm': ['n', 'j', 'k']
    }
    
    # Visual similarity mappings (characters that look similar)
    VISUAL_CONFUSABLES = {
        'a': ['@', '4'],
        'e': ['3'],
        'g': ['9'],
        'i': ['1', 'l', '!'],
        'l': ['1', 'i', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7'],
        'rn': ['m'],
        'm': ['rn'],
        'cl': ['d'],
        'vv': ['w'],
        'nn': ['m']
    }
    
    # IDN confusable characters (simplified set)
    IDN_CONFUSABLES = {
        'a': ['а', 'α', 'ɑ'],  # Cyrillic/Greek lookalikes
        'e': ['е', 'ε'],
        'i': ['і', 'ι'],
        'o': ['о', 'ο', 'σ'],
        'p': ['р', 'ρ'],
        'c': ['с', 'ϲ'],
        'x': ['х', 'χ'],
        'y': ['у', 'γ'],
    }
    
    # Common subdomain prefixes for variations
    SUBDOMAIN_PREFIXES = [
        'www', 'mail', 'email', 'webmail', 'ftp', 'cpanel', 'whm',
        'admin', 'administrator', 'root', 'api', 'secure', 'ssl',
        'shop', 'store', 'payment', 'pay', 'billing', 'account',
        'login', 'signin', 'auth', 'support', 'help', 'service',
        'mobile', 'm', 'app', 'apps', 'download', 'updates'
    ]
    
    def __init__(self, config: GeneratorConfig, tlds: Set[str]):
        """Initialize the domain generator.
        
        Args:
            config: Generator configuration
            tlds: Set of valid TLDs to use
        """
        self.config = config
        self.tlds = tlds
        logger.info(f"Initialized DomainGenerator with {len(tlds)} TLDs")
    
    def generate_variations(self, domains: List[str]) -> Generator[str, None, None]:
        """Generate domain variations for a list of input domains.
        
        Args:
            domains: List of input domains
            
        Yields:
            Generated domain variations
        """
        for domain in domains:
            yield from self.generate_domain_variations(domain)
    
    def generate_domain_variations(self, domain: str) -> Generator[str, None, None]:
        """Generate variations for a single domain.
        
        Args:
            domain: Input domain
            
        Yields:
            Domain variations
        """
        # Parse the domain
        domain = self._clean_domain(domain)
        extracted = tldextract.extract(domain)
        
        if not extracted.domain:
            logger.warning(f"Could not extract domain from: {domain}")
            return
        
        base_domain = extracted.domain
        original_tld = extracted.suffix
        
        logger.debug(f"Generating variations for: {base_domain}.{original_tld}")
        
        # Keep track of generated domains to avoid duplicates
        seen_domains = set()
        variation_count = 0
        
        # Generate variations using different techniques
        techniques = [
            (self.config.enable_character_omission, self._generate_omission_variants),
            (self.config.enable_character_repetition, self._generate_repetition_variants),
            (self.config.enable_character_substitution, self._generate_substitution_variants),
            (self.config.enable_keyboard_typos, self._generate_keyboard_variants),
            (self.config.enable_visual_similarity, self._generate_visual_variants),
            (self.config.enable_idn_confusables, self._generate_idn_variants),
            (self.config.enable_subdomain_variations, self._generate_subdomain_variants),
        ]
        
        for enabled, technique_func in techniques:
            if not enabled or variation_count >= self.config.max_variants_per_domain:
                continue
                
            try:
                for variant_domain in technique_func(base_domain):
                    if variation_count >= self.config.max_variants_per_domain:
                        break
                    
                    # Generate with different TLD combinations
                    for tld in self._get_relevant_tlds(original_tld):
                        full_domain = f"{variant_domain}.{tld}"
                        
                        if (full_domain not in seen_domains and 
                            self._is_valid_domain_name(full_domain) and
                            full_domain != domain):
                            
                            seen_domains.add(full_domain)
                            variation_count += 1
                            yield full_domain
                            
                            if variation_count >= self.config.max_variants_per_domain:
                                break
                                
            except Exception as e:
                logger.error(f"Error in technique {technique_func.__name__}: {e}")
                continue
        
        logger.debug(f"Generated {variation_count} variations for {domain}")
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize domain input."""
        domain = domain.strip().lower()
        
        # Remove protocol if present
        if '://' in domain:
            domain = urlparse(f"http://{domain}" if not domain.startswith('http') else domain).netloc
        
        # Remove www prefix for processing
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    
    def _get_relevant_tlds(self, original_tld: str) -> List[str]:
        """Get relevant TLDs for variations."""
        relevant_tlds = []
        
        # Always include original TLD
        if original_tld and original_tld in self.tlds:
            relevant_tlds.append(original_tld)
        
        # Add common TLDs
        common_tlds = {'com', 'net', 'org', 'info', 'biz'}
        for tld in common_tlds:
            if tld in self.tlds and len(tld) <= self.config.max_tld_length:
                relevant_tlds.append(tld)
        
        # Add some random TLDs for diversity
        available_tlds = [tld for tld in self.tlds if len(tld) <= self.config.max_tld_length]
        random_tlds = random.sample(
            available_tlds, 
            min(10, len(available_tlds))
        )
        relevant_tlds.extend(random_tlds)
        
        return list(set(relevant_tlds))  # Remove duplicates
    
    def _generate_omission_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate variants by omitting characters."""
        for i in range(len(domain)):
            variant = domain[:i] + domain[i+1:]
            if len(variant) > 1:  # Ensure we don't create empty domains
                yield variant
    
    def _generate_repetition_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate variants by repeating characters."""
        for i in range(len(domain)):
            # Double the character
            variant = domain[:i] + domain[i] + domain[i:]
            yield variant
            
            # Triple the character (less common but still used)
            if i < len(domain) - 1:
                variant = domain[:i] + domain[i] * 2 + domain[i:]
                yield variant
    
    def _generate_substitution_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate variants by substituting characters."""
        for i in range(len(domain)):
            char = domain[i]
            for replacement in string.ascii_lowercase:
                if replacement != char:
                    variant = domain[:i] + replacement + domain[i+1:]
                    yield variant
    
    def _generate_keyboard_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate variants based on keyboard proximity."""
        for i, char in enumerate(domain):
            if char in self.KEYBOARD_LAYOUT:
                for adjacent_char in self.KEYBOARD_LAYOUT[char]:
                    variant = domain[:i] + adjacent_char + domain[i+1:]
                    yield variant
    
    def _generate_visual_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate variants using visually similar characters."""
        # Single character substitutions
        for i, char in enumerate(domain):
            if char in self.VISUAL_CONFUSABLES:
                for confusable in self.VISUAL_CONFUSABLES[char]:
                    variant = domain[:i] + confusable + domain[i+1:]
                    yield variant
        
        # Multi-character substitutions
        for pattern, replacement in self.VISUAL_CONFUSABLES.items():
            if len(pattern) > 1 and pattern in domain:
                for repl in replacement:
                    variant = domain.replace(pattern, repl)
                    if variant != domain:
                        yield variant
    
    def _generate_idn_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate IDN confusable variants."""
        for i, char in enumerate(domain):
            if char in self.IDN_CONFUSABLES:
                for confusable in self.IDN_CONFUSABLES[char]:
                    variant = domain[:i] + confusable + domain[i+1:]
                    yield variant
    
    def _generate_subdomain_variants(self, domain: str) -> Generator[str, None, None]:
        """Generate subdomain variants."""
        for prefix in self.SUBDOMAIN_PREFIXES:
            # Add common subdomain prefixes
            yield f"{prefix}-{domain}"
            yield f"{prefix}.{domain}"
            
            # Less common but still seen patterns
            yield f"{domain}-{prefix}"
            yield f"{prefix}{domain}"
    
    def _is_valid_domain_name(self, domain: str) -> bool:
        """Validate domain name format."""
        if not domain or len(domain) > 253:
            return False
        
        # Basic domain validation
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        for part in parts:
            if not part or len(part) > 63:
                return False
            # Allow alphanumeric, hyphens, and some special chars for IDN
            if not all(c.isalnum() or c == '-' or ord(c) > 127 for c in part):
                return False
            if part.startswith('-') or part.endswith('-'):
                return False
        
        return True