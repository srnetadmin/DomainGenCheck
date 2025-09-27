# DomainGenChecker v2.1

[![CI/CD Pipeline](https://github.com/srnetadmin/DomainGenCheck/actions/workflows/ci.yml/badge.svg)](https://github.com/srnetadmin/DomainGenCheck/actions/workflows/ci.yml)
[![CodeQL Analysis](https://github.com/srnetadmin/DomainGenCheck/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/srnetadmin/DomainGenCheck/actions/workflows/codeql-analysis.yml)
[![Security Policy](https://img.shields.io/badge/security-policy-blue.svg)](SECURITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Advanced domain variation generation and testing tool for typosquatting detection.**

DomainGenChecker is a comprehensive Python tool that generates domain name variations using sophisticated typosquatting techniques and tests their DNS resolution status. It's designed for security professionals, threat intelligence analysts, and researchers to identify potentially malicious domain registrations.

## 🚀 Features

### Advanced Domain Generation Techniques
- **Keyboard-based typos**: Adjacent key substitutions based on QWERTY layout
- **Visual similarity**: Character substitutions using visually similar characters
- **Character manipulation**: Omission, repetition, and substitution
- **IDN confusables**: International domain name homograph attacks
- **Subdomain variations**: Common subdomain prefix combinations
- **Multiple TLD combinations**: Test across various top-level domains

### High-Performance DNS Resolution  
- **Asynchronous DNS lookups**: Concurrent processing for speed
- **Intelligent caching**: TTL-based result caching to avoid redundant queries
- **Rate limiting**: Configurable query throttling to respect DNS servers
- **Retry logic**: Automatic retry with exponential backoff
- **Multiple DNS servers**: Support for custom nameservers
- **Health checking**: Built-in DNS resolver health validation

### Rich Output Formats
- **Text**: Beautiful console output with Rich formatting
- **JSON**: Structured data for integration with other tools
- **CSV**: Spreadsheet-compatible format for analysis
- **Statistics**: Comprehensive reporting and analytics

### Security & Reliability
- **Input validation**: Robust domain and configuration validation
- **Error handling**: Graceful handling of DNS failures and timeouts
- **Logging**: Comprehensive logging with configurable levels
- **Configuration**: Flexible JSON-based configuration system
- **Automated security scanning**: CodeQL analysis, dependency scanning, and vulnerability detection
- **Secret scanning**: GitHub's advanced secret detection with push protection
- **Security updates**: Automated Dependabot security patches

## 📦 Installation

### Quick Install (Virtual Environment Recommended)

Modern Python distributions (like Kali Linux, Ubuntu 23.04+, etc.) require virtual environments due to PEP 668 externally-managed environments.

#### **Method 1: Using Python venv (Recommended)**
```bash
# Clone the repository
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# OR: venv\Scripts\activate  # On Windows

# Install DomainGenChecker
pip install -e .

# Verify installation
domaingen --help
```

#### **Method 2: Using pipx (Isolated Installation)**
```bash
# Install pipx if not already installed
sudo apt install pipx  # On Debian/Ubuntu/Kali
# OR: python3 -m pip install --user pipx

# Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
pipx install -e .

# Verify installation
domaingen --help
```

### Legacy Installation (System-wide)

⚠️ **Note**: Only works on older Python distributions without externally-managed environments.

```bash
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
pip install -e .
```

### Development Installation

#### **With Virtual Environment (Recommended)**
```bash
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Running After Installation

#### **With Virtual Environment**
```bash
# Activate the virtual environment first
cd DomainGenCheck-v2
source venv/bin/activate

# Then run commands
domaingen --domain example.com
domaingen --file domains.txt
```

#### **With pipx**
```bash
# Direct usage (no activation needed)
domaingen --domain example.com
domaingen --file domains.txt
```

### Troubleshooting Installation

> 📋 **For comprehensive installation instructions, troubleshooting, and OS-specific guidance, see [INSTALL.md](INSTALL.md)**

#### **"externally-managed-environment" Error**
If you see this error:
```
error: externally-managed-environment

× This environment is externally managed
```

You're on a modern Python distribution. Use the virtual environment method:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### **Missing Dependencies**
```bash
# Install system dependencies (Ubuntu/Kali/Debian)
sudo apt update
sudo apt install python3-venv python3-pip git

# For development
sudo apt install python3-dev build-essential
```

## 🔄 v2.1.0 CLI Changes

### New Flag-First Interface

v2.1.0 introduces a **flag-first CLI interface** for clearer, more explicit input handling:

#### **Before (v2.0.x)**:
```bash
domaingen domains.txt                    # Auto-detected as file
domaingen example.com --domain           # Required explicit flag
```

#### **After (v2.1.0)**:
```bash
domaingen --file domains.txt             # Explicit file input
domaingen --domain example.com           # Explicit domain input
```

### Key Benefits
- ✅ **Any file extension works**: `.domains`, `.list`, `.input`, `.txt` - all supported
- ✅ **No ambiguity**: Clear, explicit input type specification
- ✅ **Better UX**: Follows standard CLI patterns
- ✅ **Enhanced validation**: Immediate error feedback

### Migration Guide
| **v2.0.x Command** | **v2.1.0 Equivalent** |
|---------------------|------------------------|
| `domaingen domains.txt` | `domaingen --file domains.txt` |
| `domaingen example.com --domain` | `domaingen --domain example.com` |
| `domaingen sites.list` | `domaingen --file sites.list` |

**Note**: This is a breaking change. The new explicit flags are required in v2.1.0+.

## 🔧 Quick Start

> **📝 Note**: If you installed using a virtual environment, make sure to activate it first:
> ```bash
> cd DomainGenCheck-v2
> source venv/bin/activate  # Activate virtual environment
> ```

### Basic Usage
```bash
# Single domain analysis
domaingen --domain example.com

# Multiple domains from file
domaingen --file domains.txt

# Custom output format with single domain
domaingen --domain github.com --format json --output results.json

# File input with enhanced performance
domaingen --file domains.txt --concurrent 200 --rate-limit 20

# Generate more variants per domain
domaingen --domain google.com --max-variants 100
```

### Advanced Usage
```bash
# Disable specific generation techniques
domaingen --file domains.txt --disable-keyboard-typos --disable-subdomain-variations

# Enable IDN confusable attacks (use with caution)
domaingen --domain example.com --enable-idn-confusables

# Use custom DNS servers
domaingen --file domains.txt --nameservers 8.8.8.8 --nameservers 8.8.8.8

# High verbosity with detailed error reporting
domaingen --domain test.com --verbosity 2 --log-level DEBUG

# Short flags for convenience
domaingen -d example.com -f json --max-variants 50
domaingen -f domains.txt --format csv --output results.csv
```

## 🛠️ Configuration

### Command Line Options

#### Input Options
| Option | Description | Required |
|--------|-------------|----------|
| `--domain, -d` | Single domain name to analyze | One of --domain or --file |
| `--file, -f` | Path to file containing domains | One of --domain or --file |

#### Processing Options
| Option | Description | Default |
| `--max-variants` | Maximum variants per domain | 50 |
| `--concurrent` | Concurrent DNS queries | 100 |
| `--rate-limit` | DNS queries per second | 10.0 |
| `--timeout` | DNS timeout in seconds | 5.0 |
| `--format` | Output format (text/json/csv) | text |
| `--output` | Output file path | stdout |
| `--verbosity` | Output verbosity level (0-3) | 1 |

### Configuration File
Create a JSON configuration file for persistent settings:

```json
{
  "generator": {
    "max_variants_per_domain": 100,
    "enable_keyboard_typos": true,
    "enable_visual_similarity": true,
    "enable_idn_confusables": false
  },
  "dns": {
    "concurrent_limit": 150,
    "rate_limit": 15.0,
    "timeout": 3.0,
    "nameservers": ["8.8.8.8", "1.1.1.1"]
  },
  "output": {
    "format": "json",
    "include_statistics": true,
    "verbosity": 2
  }
}
```

Use with: `domaingen --file domains.txt --config config.json`

## 📝 Input Methods

### Single Domain Input
```bash
# Analyze a single domain
domaingen --domain example.com
domaingen -d github.com  # Short flag
```

### File Input
Create a text file with domains to analyze (one per line):

```
# Target domains for analysis
google.com
github.com
microsoft.com
example.org
```

Comments (lines starting with #) are ignored.

**Supported file extensions**: Any extension works with the `--file` flag:
```bash
domaingen --file domains.txt      # Standard .txt
domaingen --file sites.list       # Custom .list
domaingen --file corporate.domains # Custom .domains
domaingen -f targets.input        # Any extension works!
```

## 📊 Output Examples

### Text Format
```
┌─────────────────────────────────────────────────────────────┐
│                    Domain Resolution Results (150 domains) │
├─────────────────────────────────────────────────────────────┤
│ Domain                 │ Status    │ IP Addresses      │ Response Time │
├─────────────────────────────────────────────────────────────┤
│ googl.com             │ Resolved  │ 142.251.46.14     │         0.023s │
│ gooogle.com           │ Resolved  │ 185.199.108.153   │         0.045s │
│ google.co             │ Resolved  │ 216.58.194.142    │         0.031s │
│ google.cm             │ Unresolved│ -                 │         0.102s │
└─────────────────────────────────────────────────────────────┘

Statistics:
• Total Domains: 150
• Resolved: 47 (31.3%)
• Unresolved: 98 (65.3%)
• Errors: 5 (3.3%)
```

### JSON Format
```json
{
  "metadata": {
    "timestamp": "2024-01-15 14:30:22",
    "total_domains": 150,
    "format_version": "2.1"
  },
  "statistics": {
    "resolution_rate": 31.3,
    "avg_response_time": 0.045,
    "domains_per_second": 25.4
  },
  "results": [
    {
      "domain": "googl.com",
      "status": "resolved",
      "ip_addresses": ["142.251.46.14"],
      "response_time": 0.023,
      "timestamp": 1705330222.123
    }
  ]
}
```

## 🔍 Domain Generation Techniques

### 1. Character Manipulation
- **Omission**: `google.com` → `gogle.com`
- **Repetition**: `google.com` → `gooogle.com` 
- **Substitution**: `google.com` → `gaogle.com`

### 2. Keyboard Typos
Based on QWERTY keyboard layout proximity:
- `google.com` → `foogle.com` (g→f adjacent keys)
- `github.com` → `githib.com` (u→i adjacent keys)

### 3. Visual Similarity
- `google.com` → `g00gle.com` (o→0)
- `microsoft.com` → `microsft.com` (o→o)

### 4. Subdomain Variations
- `google.com` → `mail-google.com`
- `google.com` → `secure.google.com`

### 5. IDN Confusables (Optional)
- `google.com` → `gооgle.com` (Latin o → Cyrillic о)

## 📈 Performance Tuning

### Optimizing for Speed
```bash
# Maximum performance (be respectful to DNS servers)
domaingen --file domains.txt \\
  --concurrent 500 \\
  --rate-limit 50 \\
  --timeout 2.0 \\
  --retries 1
```

### Optimizing for Thoroughness
```bash
# Maximum coverage
domaingen --domain example.com \\
  --max-variants 200 \\
  --enable-idn-confusables \\
  --timeout 10.0 \\
  --retries 5
```

## 🛡️ Security Considerations

1. **Rate Limiting**: Always use appropriate rate limiting to avoid overwhelming DNS servers
2. **Legal Compliance**: Ensure your use case complies with applicable laws and regulations
3. **Responsible Disclosure**: Report identified threats through appropriate channels
4. **DNS Privacy**: Be aware that DNS queries may be logged by DNS providers

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
pip install -e ".[dev]"
pre-commit install
```

### Running Tests
```bash
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
black src/ tests/
isort src/ tests/  
flake8 src/ tests/
mypy src/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [dnspython](https://dnspython.readthedocs.io/) for DNS resolution
- [Rich](https://rich.readthedocs.io/) for beautiful console output
- [Click](https://click.palletsprojects.com/) for CLI interface
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/srnetadmin/DomainGenCheck/issues)
- **Discussions**: [GitHub Discussions](https://github.com/srnetadmin/DomainGenCheck/discussions)
- **Security**: Report security vulnerabilities via [GitHub Security Advisories](https://github.com/srnetadmin/DomainGenCheck/security/advisories)

---

**⚠️ Disclaimer**: This tool is intended for legitimate security research and defensive purposes only. Users are responsible for ensuring their use complies with applicable laws and regulations.