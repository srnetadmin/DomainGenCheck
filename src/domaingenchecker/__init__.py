"""
DomainGenChecker - Advanced domain variation generation and testing tool.

A comprehensive tool for generating domain name variations using various
typosquatting techniques and testing their DNS resolution status.
"""

__version__ = "2.1.1"
__author__ = "Greg Huff"
__email__ = "srnetadmin@users.noreply.github.com"

from .config import Config
from .dns_checker import DNSChecker
from .domain_generator import DomainGenerator
from .output_handler import OutputHandler

__all__ = [
    "DomainGenerator",
    "DNSChecker",
    "OutputHandler",
    "Config",
]
