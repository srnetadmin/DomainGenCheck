"""
Command-line interface for DomainGenChecker.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Set

import click
from rich.console import Console

from . import __version__
from .config import Config, OutputFormat, LogLevel
from .domain_generator import DomainGenerator
from .dns_checker import DNSChecker
from .output_handler import OutputHandler


console = Console()
logger = logging.getLogger(__name__)


def load_tlds(tld_file: Path, max_length: int = 10) -> Set[str]:
    """Load TLDs from file.
    
    Args:
        tld_file: Path to TLD file
        max_length: Maximum TLD length
        
    Returns:
        Set of valid TLDs
    """
    tlds = set()
    try:
        with open(tld_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().lower()
                if line and not line.startswith('#') and 2 <= len(line) <= max_length:
                    tlds.add(line)
        logger.info(f"Loaded {len(tlds)} TLDs from {tld_file}")
    except FileNotFoundError:
        console.print(f"[red]Error: TLD file not found: {tld_file}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error loading TLD file: {e}[/red]")
        sys.exit(1)
    
    return tlds


def load_single_domain(domain_name: str) -> List[str]:
    """Load a single domain name.
    
    Args:
        domain_name: Domain name to process
        
    Returns:
        List containing single domain
    """
    domain = domain_name.strip().lower()
    logger.info(f"Processing single domain: {domain}")
    return [domain]


def load_domains_from_file(domains_file: Path) -> List[str]:
    """Load domains from file.
    
    Args:
        domains_file: Path to domains file
        
    Returns:
        List of domains
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: For other file reading errors
    """
    domains = []
    
    if not domains_file.exists():
        raise FileNotFoundError(f"Domains file not found: {domains_file}")
    
    try:
        with open(domains_file, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip().lower()
                if domain and not domain.startswith('#'):
                    domains.append(domain)
        logger.info(f"Loaded {len(domains)} input domains from {domains_file}")
    except Exception as e:
        raise Exception(f"Error reading domains file {domains_file}: {e}")
    
    return domains


@click.command()
@click.option('--domain', '-d', type=str, help='Single domain name to analyze')
@click.option('--file', '-f', type=click.Path(exists=True, path_type=Path), help='Path to file containing domains (one per line)')
@click.option('--tld-file', '-t', type=click.Path(exists=True, path_type=Path), 
              help='TLD file path (defaults to bundled TLDs)')
@click.option('--max-variants', '-m', default=50, type=click.IntRange(1, 1000),
              help='Maximum variants per domain (default: 50)')
@click.option('--max-tld-length', default=10, type=click.IntRange(2, 20),
              help='Maximum TLD length (default: 10)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'csv']), 
              default='text', help='Output format (default: text)')
@click.option('--concurrent', '-c', default=100, type=click.IntRange(1, 1000),
              help='Concurrent DNS queries (default: 100)')
@click.option('--rate-limit', '-r', default=10.0, type=float,
              help='DNS queries per second (default: 10.0)')
@click.option('--timeout', default=5.0, type=float,
              help='DNS timeout in seconds (default: 5.0)')
@click.option('--retries', default=3, type=click.IntRange(1, 10),
              help='DNS retries (default: 3)')
@click.option('--nameservers', multiple=True,
              help='Custom DNS nameservers (can be specified multiple times)')
@click.option('--no-cache', is_flag=True, help='Disable DNS result caching')
@click.option('--include-unresolved/--exclude-unresolved', default=True,
              help='Include unresolved domains in output (default: include)')
@click.option('--no-statistics', is_flag=True, help='Disable statistics output')
@click.option('--verbosity', '-v', default=1, type=click.IntRange(0, 3),
              help='Output verbosity (0=quiet, 1=normal, 2=verbose, 3=debug)')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              default='INFO', help='Logging level (default: INFO)')
@click.option('--config', type=click.Path(exists=True, path_type=Path),
              help='Load configuration from JSON file')
@click.option('--disable-keyboard-typos', is_flag=True, help='Disable keyboard-based typos')
@click.option('--disable-visual-similarity', is_flag=True, help='Disable visual similarity substitutions')
@click.option('--disable-character-omission', is_flag=True, help='Disable character omission')
@click.option('--disable-character-repetition', is_flag=True, help='Disable character repetition')
@click.option('--disable-character-substitution', is_flag=True, help='Disable character substitution')
@click.option('--disable-subdomain-variations', is_flag=True, help='Disable subdomain variations')
@click.option('--enable-idn-confusables', is_flag=True, help='Enable IDN confusable attacks')
@click.option('--version', is_flag=True, help='Show version and exit')
def main(
    domain: str,
    file: Path,
    tld_file: Path,
    max_variants: int,
    max_tld_length: int,
    output: Path,
    output_format: str,
    concurrent: int,
    rate_limit: float,
    timeout: float,
    retries: int,
    nameservers: tuple,
    no_cache: bool,
    include_unresolved: bool,
    no_statistics: bool,
    verbosity: int,
    no_color: bool,
    log_level: str,
    config: Path,
    disable_keyboard_typos: bool,
    disable_visual_similarity: bool,
    disable_character_omission: bool,
    disable_character_repetition: bool,
    disable_character_substitution: bool,
    disable_subdomain_variations: bool,
    enable_idn_confusables: bool,
    version: bool
) -> None:
    """DomainGenChecker v2.1 - Advanced domain variation generation and testing.
    
    Generate and test domain name variations to detect typosquatting and copycat sites.
    
    Specify input using either:
      --domain DOMAIN_NAME    Single domain to analyze (e.g., 'example.com')
      --file FILE_PATH        File containing domains, one per line
    
    Exactly one of --domain or --file must be specified.
    """
    
    # Show version and exit
    if version:
        console.print(f"DomainGenChecker v{__version__}")
        return
    
    # Load configuration
    if config:
        try:
            app_config = Config.from_file(config)
            console.print(f"[green]Loaded configuration from {config}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading config file: {e}[/red]")
            sys.exit(1)
    else:
        app_config = Config()
    
    # Override config with CLI arguments
    app_config.generator.max_variants_per_domain = max_variants
    app_config.generator.max_tld_length = max_tld_length
    app_config.generator.enable_keyboard_typos = not disable_keyboard_typos
    app_config.generator.enable_visual_similarity = not disable_visual_similarity
    app_config.generator.enable_character_omission = not disable_character_omission
    app_config.generator.enable_character_repetition = not disable_character_repetition
    app_config.generator.enable_character_substitution = not disable_character_substitution
    app_config.generator.enable_subdomain_variations = not disable_subdomain_variations
    app_config.generator.enable_idn_confusables = enable_idn_confusables
    
    app_config.dns.concurrent_limit = concurrent
    app_config.dns.rate_limit = rate_limit
    app_config.dns.timeout = timeout
    app_config.dns.retries = retries
    app_config.dns.nameservers = list(nameservers) if nameservers else None
    
    app_config.output.format = OutputFormat(output_format)
    app_config.output.output_file = output
    app_config.output.include_unresolved = include_unresolved
    app_config.output.include_statistics = not no_statistics
    app_config.output.verbosity = verbosity
    app_config.output.colorize = not no_color
    
    app_config.log_level = LogLevel(log_level)
    app_config.cache_results = not no_cache
    
    # Set up logging
    app_config.setup_logging()
    
    # Get default TLD file if not provided
    if not tld_file:
        # Look for bundled TLD file in data directory
        package_dir = Path(__file__).parent.parent.parent
        default_tld_file = package_dir / "data" / "tlds-alpha-by-domain.txt"
        if default_tld_file.exists():
            tld_file = default_tld_file
        else:
            console.print("[red]Error: No TLD file specified and default not found[/red]")
            console.print("[yellow]Please specify a TLD file with --tld-file[/yellow]")
            sys.exit(1)
    
    # Validate input arguments
    if not domain and not file:
        console.print("[red]Error: Must specify either --domain or --file[/red]")
        console.print("[yellow]Use --help for usage information[/yellow]")
        sys.exit(1)
    
    if domain and file:
        console.print("[red]Error: Cannot specify both --domain and --file[/red]")
        console.print("[yellow]Use either --domain DOMAIN or --file FILE[/yellow]")
        sys.exit(1)
    
    # Run the main application
    try:
        if domain:
            input_source = domain
            input_mode = "domain"
        else:  # file is specified
            input_source = str(file)
            input_mode = "file"
            
        asyncio.run(run_domain_check(app_config, input_source, tld_file, input_mode))
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error in main application")
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


async def run_domain_check(config: Config, input_source: str, tld_file: Path, 
                      input_mode: str = None) -> None:
    """Run the main domain checking logic.
    
    Args:
        config: Application configuration
        input_source: Either a single domain or path to domains file
        tld_file: Path to TLD file
        input_mode: Force input mode: 'domain' or 'file', or None for auto-detection
    """
    # Initialize components
    output_handler = OutputHandler(config.output)
    
    # Load input data
    try:
        if input_mode == "domain":
            # Single domain mode
            input_domains = load_single_domain(input_source)
        elif input_mode == "file":
            # File mode
            input_domains = load_domains_from_file(Path(input_source))
        else:
            # This should not happen due to validation above
            output_handler.display_error("Invalid input mode")
            return
            
        if not input_domains:
            output_handler.display_error("No valid domains found in input")
            return
    except FileNotFoundError:
        output_handler.display_error(f"File not found: {input_source}")
        return
    except Exception as e:
        output_handler.display_error(f"Error processing input: {e}")
        return
    
    valid_tlds = load_tlds(tld_file, config.generator.max_tld_length)
    if not valid_tlds:
        output_handler.display_error("No valid TLDs loaded")
        return
    
    # Initialize domain generator and DNS checker
    domain_generator = DomainGenerator(config.generator, valid_tlds)
    dns_checker = DNSChecker(config.dns)
    
    # Health check DNS resolver
    if not await dns_checker.health_check():
        output_handler.display_warning("DNS health check failed, but continuing...")
    
    # Generate domain variations
    output_handler.display_info("Generating domain variations...")
    all_variations = list(domain_generator.generate_variations(input_domains))
    
    if not all_variations:
        output_handler.display_error("No domain variations generated")
        return
    
    # Display summary
    output_handler.display_summary_header(len(input_domains), len(all_variations))
    
    # Check DNS resolution for all variations
    progress = output_handler.display_progress(len(all_variations))
    
    with progress:
        task = progress.add_task("Checking DNS resolution...", total=len(all_variations))
        
        # Process domains in batches for better memory usage
        batch_size = min(1000, len(all_variations))
        
        for i in range(0, len(all_variations), batch_size):
            batch = all_variations[i:i + batch_size]
            results = await dns_checker.check_domains(batch, use_cache=config.cache_results)
            output_handler.add_results(results)
            progress.update(task, advance=len(batch))
    
    # Generate final output
    output_handler.generate_output()
    
    # Display final statistics from DNS checker
    if config.output.verbosity >= 2:
        dns_stats = dns_checker.get_statistics()
        output_handler.display_info(f"DNS Cache: {dns_stats['cache_size']} entries")


if __name__ == '__main__':
    main()