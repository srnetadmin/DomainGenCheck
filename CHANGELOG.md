# Changelog

All notable changes to DomainGenChecker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-09-26

### Added
- Flag-first CLI interface for explicit input type specification
- `--domain` / `-d` flag for single domain input
- `--file` / `-f` flag for file-based input
- Support for any file extension when using `--file` flag
- Comprehensive input validation and error handling
- Clear usage examples in help documentation

### Changed
- **BREAKING**: Replaced positional argument with explicit flags
- CLI now requires either `--domain DOMAIN` or `--file FILE`
- Improved error messages with actionable guidance
- Enhanced help text with usage examples

### Removed
- Auto-detection heuristics (replaced with explicit flags)
- Positional argument support for input source

### Fixed
- Issue with non-standard file extensions (`.domains`, `.list`, `.input`)
- Ambiguous input interpretation edge cases
- File path validation now handled by Click framework

### Technical
- Simplified domain loading logic
- Removed complex heuristic-based input detection
- Added robust CLI argument validation
- Improved error handling consistency

## [2.0.0] - 2025-09-26

### Added
- Complete rewrite of DomainGenChecker with modern architecture
- Advanced domain generation using multiple typosquatting techniques
- High-performance asynchronous DNS resolution
- Multiple output formats (TEXT, JSON, CSV)
- Comprehensive statistics and performance metrics
- Rich terminal UI with progress bars and colored output
- Flexible configuration system with JSON config file support
- Extensive logging and debugging capabilities
- Built-in TLD database with 1300+ TLDs
- Keyboard layout-based typos, visual similarity substitutions
- Character manipulation techniques (omission, repetition, substitution)
- Subdomain variation generation
- DNS caching and rate limiting
- Concurrent processing with configurable limits
- Professional command-line interface with comprehensive options

### Technical
- Built with Python 3.8+ using modern async/await patterns
- Click framework for CLI with rich validation
- Pydantic for configuration management and validation
- Rich library for beautiful terminal output
- DNSPython for robust DNS resolution
- Comprehensive test coverage
- Professional package structure with setuptools
- Type hints throughout codebase
- Modular architecture for extensibility