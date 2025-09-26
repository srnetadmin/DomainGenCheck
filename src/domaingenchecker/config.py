"""
Configuration management for DomainGenChecker.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel, Field, validator


class OutputFormat(str, Enum):
    """Supported output formats."""
    TEXT = "text"
    JSON = "json"
    CSV = "csv"


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DNSConfig(BaseModel):
    """DNS resolution configuration."""
    timeout: float = Field(default=5.0, ge=0.1, le=30.0, description="DNS timeout in seconds")
    retries: int = Field(default=3, ge=1, le=10, description="Number of DNS retries")
    concurrent_limit: int = Field(default=100, ge=1, le=1000, description="Max concurrent DNS queries")
    rate_limit: float = Field(default=10.0, ge=0.1, description="DNS queries per second rate limit")
    nameservers: Optional[List[str]] = Field(default=None, description="Custom DNS nameservers")
    use_doh: bool = Field(default=False, description="Use DNS over HTTPS")
    
    @validator('nameservers')
    def validate_nameservers(cls, v):
        if v is not None:
            # Basic IP validation - could be enhanced
            for ns in v:
                if not (ns.count('.') == 3 and all(0 <= int(x) <= 255 for x in ns.split('.'))):
                    raise ValueError(f"Invalid nameserver format: {ns}")
        return v


class GeneratorConfig(BaseModel):
    """Domain generation configuration."""
    max_variants_per_domain: int = Field(default=50, ge=1, le=1000, description="Max variants per input domain")
    max_tld_length: int = Field(default=10, ge=2, le=20, description="Max TLD length to consider")
    enable_keyboard_typos: bool = Field(default=True, description="Enable keyboard-based typos")
    enable_visual_similarity: bool = Field(default=True, description="Enable visual similarity substitutions")
    enable_character_omission: bool = Field(default=True, description="Enable character omission")
    enable_character_repetition: bool = Field(default=True, description="Enable character repetition")
    enable_character_substitution: bool = Field(default=True, description="Enable character substitution")
    enable_subdomain_variations: bool = Field(default=True, description="Enable subdomain variations")
    enable_idn_confusables: bool = Field(default=False, description="Enable IDN confusable attacks")
    custom_tlds: Optional[Set[str]] = Field(default=None, description="Custom TLD list")
    
    @validator('custom_tlds')
    def validate_tlds(cls, v):
        if v is not None:
            # Ensure TLDs are lowercase and valid format
            return {tld.lower().strip('.') for tld in v if tld.strip()}
        return v


class OutputConfig(BaseModel):
    """Output configuration."""
    format: OutputFormat = Field(default=OutputFormat.TEXT, description="Output format")
    output_file: Optional[Path] = Field(default=None, description="Output file path")
    include_unresolved: bool = Field(default=True, description="Include unresolved domains in output")
    include_statistics: bool = Field(default=True, description="Include statistics in output")
    verbosity: int = Field(default=1, ge=0, le=3, description="Output verbosity level")
    colorize: bool = Field(default=True, description="Colorize console output")


class Config(BaseModel):
    """Main configuration class."""
    dns: DNSConfig = Field(default_factory=DNSConfig)
    generator: GeneratorConfig = Field(default_factory=GeneratorConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    # Global settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    cache_results: bool = Field(default=True, description="Enable result caching")
    cache_ttl: int = Field(default=3600, ge=60, description="Cache TTL in seconds")
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from file."""
        if config_path.suffix.lower() == '.json':
            import json
            with open(config_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    def to_file(self, config_path: Path) -> None:
        """Save configuration to file."""
        if config_path.suffix.lower() == '.json':
            import json
            with open(config_path, 'w') as f:
                json.dump(self.dict(), f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.value),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )