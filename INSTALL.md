# Installation Guide

This guide provides comprehensive installation instructions for DomainGenChecker across different operating systems and Python environments.

## 🚀 Quick Install

### For Modern Python Distributions (Recommended)

Modern Linux distributions like Kali Linux, Ubuntu 23.04+, Fedora 38+, etc., use PEP 668 externally-managed environments that require virtual environments.

#### **Method 1: Python Virtual Environment**

```bash
# 1. Clone the repository
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR: venv\Scripts\activate  # Windows

# 4. Install DomainGenChecker
pip install -e .

# 5. Verify installation
domaingen --help
```

#### **Method 2: pipx (Isolated Application)**

```bash
# 1. Install pipx (if not already installed)
sudo apt install pipx        # Debian/Ubuntu/Kali
# OR: brew install pipx      # macOS
# OR: pip install --user pipx

# 2. Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
pipx install -e .

# 3. Verify installation
domaingen --help
```

## 📋 Operating System Specific Instructions

### Kali Linux / Debian / Ubuntu

```bash
# Install prerequisites
sudo apt update
sudo apt install python3-venv python3-pip python3-dev git build-essential

# Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .
```

### Fedora / CentOS / RHEL

```bash
# Install prerequisites
sudo dnf install python3-virtualenv python3-pip python3-devel git gcc

# Or for older versions:
# sudo yum install python3-virtualenv python3-pip python3-devel git gcc

# Clone and install (same as above)
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Arch Linux / Manjaro

```bash
# Install prerequisites
sudo pacman -S python-virtualenv python-pip git base-devel

# Clone and install (same as above)
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### macOS

```bash
# Install prerequisites (using Homebrew)
brew install python3 git

# Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Windows

```powershell
# Install Python 3.8+ from python.org
# Install Git for Windows

# Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
python -m venv venv
venv\Scripts\activate
pip install -e .
```

## 🛠️ Development Installation

For contributors and developers who want to work on the codebase:

```bash
# Clone repository
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install

# Verify development tools
black --version
mypy --version
pytest --version
```

## 🏃 Running DomainGenChecker

### With Virtual Environment

```bash
# Always activate the virtual environment first
cd DomainGenCheck-v2
source venv/bin/activate

# Then run commands
domaingen --domain example.com
domaingen --file domains.txt
```

### With pipx

```bash
# Direct usage (no activation needed)
domaingen --domain example.com
domaingen --file domains.txt
```

### Creating a Desktop Shortcut (Optional)

Create a shell script for easy access:

```bash
# Create launcher script
cat > ~/bin/domaingen << 'EOF'
#!/bin/bash
cd ~/DomainGenCheck-v2
source venv/bin/activate
exec python -m domaingenchecker.cli "$@"
EOF

chmod +x ~/bin/domaingen

# Add ~/bin to PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Troubleshooting

### Error: "externally-managed-environment"

**Problem**: 
```
error: externally-managed-environment
× This environment is externally managed
```

**Solution**: You're on a modern Python distribution. Use virtual environments:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Error: "python3-venv not found"

**Problem**: Virtual environment module not installed.

**Solution**:
```bash
# Debian/Ubuntu/Kali
sudo apt install python3-venv

# Fedora
sudo dnf install python3-virtualenv

# Arch Linux
sudo pacman -S python-virtualenv
```

### Error: "Permission denied"

**Problem**: Trying to install system-wide without proper permissions.

**Solution**: Use virtual environment (recommended) or add `--user` flag:
```bash
# Recommended: Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Alternative: User-local installation
pip install --user -e .
```

### Error: "Command 'domaingen' not found"

**Problem**: Command not found after installation.

**Solutions**:
1. **With virtual environment**: Make sure it's activated:
   ```bash
   source venv/bin/activate
   domaingen --help
   ```

2. **With --user installation**: Add to PATH:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Direct module execution**:
   ```bash
   python -m domaingenchecker.cli --help
   ```

### Error: Building dependencies fails

**Problem**: Missing system development packages.

**Solution**: Install build dependencies:
```bash
# Debian/Ubuntu/Kali
sudo apt install python3-dev build-essential

# Fedora
sudo dnf install python3-devel gcc

# Arch Linux
sudo pacman -S base-devel
```

### DNS Resolution Issues

**Problem**: DNS queries failing or timing out.

**Solutions**:
1. **Use custom DNS servers**:
   ```bash
   domaingen --domain example.com --nameservers 8.8.8.8 --nameservers 1.1.1.1
   ```

2. **Adjust timeouts and rate limits**:
   ```bash
   domaingen --file domains.txt --timeout 10 --rate-limit 5
   ```

3. **Check network connectivity**:
   ```bash
   dig example.com  # Test DNS resolution
   ```

## 📦 Alternative Installation Methods

### Using Docker (Isolated Environment)

```bash
# Build Docker image
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
docker build -t domaingenchecker .

# Run with Docker
docker run --rm -v $(pwd):/workspace domaingenchecker --domain example.com
```

### Using Conda

```bash
# Create conda environment
conda create -n domaingenchecker python=3.11
conda activate domaingenchecker

# Clone and install
git clone https://github.com/srnetadmin/DomainGenCheck.git
cd DomainGenCheck-v2
pip install -e .
```

## ✅ Verification

After installation, verify everything works:

```bash
# Check installation
domaingen --version
domaingen --help

# Quick test
domaingen --domain example.com --max-variants 5

# Development verification (if installed with [dev])
black --check src/
mypy src/
pytest
```

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check existing issues**: https://github.com/srnetadmin/DomainGenCheck/issues
2. **Create new issue**: Include your OS, Python version, and error messages
3. **Discussion forum**: Use GitHub Discussions for general questions

## 🔄 Updating

To update to the latest version:

```bash
# Navigate to project directory
cd DomainGenCheck-v2

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git pull origin main

# Reinstall dependencies (in case of changes)
pip install -e .
```