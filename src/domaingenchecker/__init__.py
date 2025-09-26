"""
DomainGenChecker - Advanced domain variation generation and testing tool.

A comprehensive tool for generating domain name variations using various
typosquatting techniques and testing their DNS resolution status.
"""

__version__ = "2.1.0"
__author__ = "Greg Huff"
__email__ = "srnetadmin@users.noreply.github.com"

from .domain_generator import DomainGenerator
from .dns_checker import DNSChecker
from .output_handler import OutputHandler
from .config import Config

__all__ = [
    "DomainGenerator",
    "DNSChecker", 
    "OutputHandler",
    "Config",
]