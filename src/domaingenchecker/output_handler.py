"""
Advanced output handling with multiple formats and statistical reporting.
"""

import csv
import json
import logging
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import box

from .config import OutputConfig, OutputFormat
from .dns_checker import DNSResult, DNSStatus


logger = logging.getLogger(__name__)


class OutputHandler:
    """Advanced output handler with multiple formats and rich console output."""
    
    def __init__(self, config: OutputConfig):
        """Initialize output handler.
        
        Args:
            config: Output configuration
        """
        self.config = config
        self.console = Console(
            force_terminal=True if config.colorize else None,
            no_color=not config.colorize
        )
        self.results: List[DNSResult] = []
        self.statistics: Dict[str, Any] = {}
        self.start_time = time.time()
        
        logger.info(f"Initialized OutputHandler with format: {config.format}")
    
    def add_results(self, results: List[DNSResult]) -> None:
        """Add DNS results for processing.
        
        Args:
            results: List of DNS results
        """
        self.results.extend(results)
        logger.debug(f"Added {len(results)} results, total: {len(self.results)}")
    
    def generate_output(self) -> None:
        """Generate output based on configuration."""
        if not self.results:
            self.console.print("[yellow]No results to display[/yellow]")
            return
        
        # Calculate statistics
        self._calculate_statistics()
        
        # Generate output based on format
        if self.config.format == OutputFormat.TEXT:
            self._output_text()
        elif self.config.format == OutputFormat.JSON:
            self._output_json()
        elif self.config.format == OutputFormat.CSV:
            self._output_csv()
        
        # Display statistics if enabled
        if self.config.include_statistics:
            self._display_statistics()
    
    def _calculate_statistics(self) -> None:
        """Calculate comprehensive statistics from results."""
        total_results = len(self.results)
        if total_results == 0:
            return
        
        # Status distribution
        status_counts = Counter(result.status for result in self.results)
        
        # Response time statistics
        response_times = [r.response_time for r in self.results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Domain analysis
        resolved_domains = [r for r in self.results if r.status == DNSStatus.RESOLVED]
        unresolved_domains = [r for r in self.results if r.status == DNSStatus.UNRESOLVED]
        error_domains = [r for r in self.results if r.status == DNSStatus.ERROR]
        timeout_domains = [r for r in self.results if r.status == DNSStatus.TIMEOUT]
        
        # TLD analysis
        tld_distribution = defaultdict(int)
        for result in self.results:
            if '.' in result.domain:
                tld = result.domain.split('.')[-1]
                tld_distribution[tld] += 1
        
        # Build statistics
        self.statistics = {
            'total_domains': total_results,
            'resolved_count': len(resolved_domains),
            'unresolved_count': len(unresolved_domains),
            'error_count': len(error_domains),
            'timeout_count': len(timeout_domains),
            'resolution_rate': (len(resolved_domains) / total_results) * 100,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'total_execution_time': time.time() - self.start_time,
            'domains_per_second': total_results / (time.time() - self.start_time),
            'status_distribution': {status.value: count for status, count in status_counts.items()},
            'top_tlds': dict(sorted(tld_distribution.items(), key=lambda x: x[1], reverse=True)[:10]),
            'error_messages': Counter(r.error_message for r in self.results if r.error_message)
        }
    
    def _output_text(self) -> None:
        """Output results in text format using Rich tables."""
        if self.config.output_file:
            self._save_text_to_file()
        else:
            self._display_text_console()
    
    def _display_text_console(self) -> None:
        """Display results in console using Rich formatting."""
        # Create main results table
        table = Table(
            title=f"Domain Resolution Results ({len(self.results)} domains)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Domain", style="cyan", no_wrap=False, min_width=30)
        table.add_column("Status", justify="center", min_width=12)
        table.add_column("IP Addresses", style="green", no_wrap=False, min_width=15)
        table.add_column("Response Time", justify="right", min_width=13)
        
        if self.config.verbosity >= 2:
            table.add_column("Error", style="red", no_wrap=False)
        
        # Add rows based on filters
        for result in self._filter_results():
            status_color = self._get_status_color(result.status)
            status_text = f"[{status_color}]{result.status.value.title()}[/{status_color}]"
            
            # Format IP addresses
            ips = ", ".join(result.ip_addresses) if result.ip_addresses else "-"
            
            # Format response time
            response_time = f"{result.response_time:.3f}s" if result.response_time > 0 else "-"
            
            row = [result.domain, status_text, ips, response_time]
            
            if self.config.verbosity >= 2:
                error_msg = result.error_message or "-"
                if len(error_msg) > 40:
                    error_msg = error_msg[:37] + "..."
                row.append(error_msg)
            
            table.add_row(*row)
        
        self.console.print(table)
        self.console.print()
    
    def _save_text_to_file(self) -> None:
        """Save text output to file."""
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            f.write(f"Domain Resolution Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write("=" * 80 + "\\n\\n")
            
            for result in self._filter_results():
                f.write(f"Domain: {result.domain}\\n")
                f.write(f"Status: {result.status.value.title()}\\n")
                
                if result.ip_addresses:
                    f.write(f"IP Addresses: {', '.join(result.ip_addresses)}\\n")
                
                if result.response_time > 0:
                    f.write(f"Response Time: {result.response_time:.3f}s\\n")
                
                if result.error_message and self.config.verbosity >= 2:
                    f.write(f"Error: {result.error_message}\\n")
                
                f.write("-" * 40 + "\\n")
        
        logger.info(f"Text output saved to {self.config.output_file}")
    
    def _output_json(self) -> None:
        """Output results in JSON format."""
        output_data = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_domains': len(self.results),
                'format_version': '2.1'
            },
            'statistics': self.statistics if self.config.include_statistics else None,
            'results': [
                {
                    'domain': result.domain,
                    'status': result.status.value,
                    'ip_addresses': result.ip_addresses,
                    'response_time': result.response_time,
                    'error_message': result.error_message,
                    'timestamp': result.timestamp
                }
                for result in self._filter_results()
            ]
        }
        
        if self.config.output_file:
            with open(self.config.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON output saved to {self.config.output_file}")
        else:
            self.console.print(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    def _output_csv(self) -> None:
        """Output results in CSV format."""
        fieldnames = [
            'domain', 'status', 'ip_addresses', 'response_time', 
            'error_message', 'timestamp'
        ]
        
        if self.config.output_file:
            output_file = self.config.output_file
        else:
            output_file = Path('/dev/stdout')  # Output to stdout
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self._filter_results():
                writer.writerow({
                    'domain': result.domain,
                    'status': result.status.value,
                    'ip_addresses': ';'.join(result.ip_addresses),
                    'response_time': result.response_time,
                    'error_message': result.error_message or '',
                    'timestamp': result.timestamp
                })
        
        if self.config.output_file:
            logger.info(f"CSV output saved to {self.config.output_file}")
    
    def _filter_results(self) -> List[DNSResult]:
        """Filter results based on configuration."""
        filtered = self.results
        
        # Filter out unresolved domains if not wanted
        if not self.config.include_unresolved:
            filtered = [r for r in filtered if r.status != DNSStatus.UNRESOLVED]
        
        return filtered
    
    def _display_statistics(self) -> None:
        """Display comprehensive statistics."""
        if not self.statistics:
            return
        
        # Create statistics panel
        stats_content = []
        
        # Basic counts
        stats_content.extend([
            f"[bold cyan]Total Domains:[/bold cyan] {self.statistics['total_domains']:,}",
            f"[bold green]Resolved:[/bold green] {self.statistics['resolved_count']:,} ({self.statistics['resolution_rate']:.1f}%)",
            f"[bold red]Unresolved:[/bold red] {self.statistics['unresolved_count']:,}",
            f"[bold yellow]Errors:[/bold yellow] {self.statistics['error_count']:,}",
            f"[bold orange]Timeouts:[/bold orange] {self.statistics['timeout_count']:,}",
            "",
        ])
        
        # Performance stats
        stats_content.extend([
            f"[bold blue]Performance:[/bold blue]",
            f"  Average Response: {self.statistics['avg_response_time']:.3f}s",
            f"  Min Response: {self.statistics['min_response_time']:.3f}s",
            f"  Max Response: {self.statistics['max_response_time']:.3f}s",
            f"  Total Time: {self.statistics['total_execution_time']:.1f}s",
            f"  Domains/Second: {self.statistics['domains_per_second']:.1f}",
            "",
        ])
        
        # Top TLDs
        if self.statistics['top_tlds']:
            stats_content.append("[bold magenta]Top TLDs:[/bold magenta]")
            for tld, count in list(self.statistics['top_tlds'].items())[:5]:
                stats_content.append(f"  .{tld}: {count:,}")
        
        panel = Panel(
            "\\n".join(stats_content),
            title="[bold white]Statistics[/bold white]",
            border_style="blue",
            box=box.ROUNDED
        )
        
        self.console.print(panel)
    
    def _get_status_color(self, status: DNSStatus) -> str:
        """Get color for DNS status."""
        color_map = {
            DNSStatus.RESOLVED: "green",
            DNSStatus.UNRESOLVED: "yellow",
            DNSStatus.ERROR: "red",
            DNSStatus.TIMEOUT: "orange3"
        }
        return color_map.get(status, "white")
    
    def display_progress(self, total: int) -> Progress:
        """Create and return a progress bar for domain checking.
        
        Args:
            total: Total number of domains to check
            
        Returns:
            Progress bar instance
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            console=self.console
        )
        
        return progress
    
    def display_summary_header(self, input_domains: int, generated_domains: int) -> None:
        """Display summary header information.
        
        Args:
            input_domains: Number of input domains
            generated_domains: Number of generated domain variations
        """
        header_text = f"""
[bold cyan]DomainGenChecker v2.1[/bold cyan] - Advanced Typosquatting Detection
        
[bold]Input Configuration:[/bold]
• Input domains: {input_domains:,}
• Generated variations: {generated_domains:,}
• Output format: {self.config.format.value.upper()}
        """
        
        panel = Panel(
            header_text.strip(),
            title="[bold white]Scan Summary[/bold white]",
            border_style="cyan",
            box=box.DOUBLE
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_error(self, message: str) -> None:
        """Display error message with formatting.
        
        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def display_warning(self, message: str) -> None:
        """Display warning message with formatting.
        
        Args:
            message: Warning message to display
        """
        self.console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
    
    def display_info(self, message: str) -> None:
        """Display info message with formatting.
        
        Args:
            message: Info message to display
        """
        self.console.print(f"[bold blue]Info:[/bold blue] {message}")