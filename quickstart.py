#!/usr/bin/env python3
"""
Quick start script for the Deployment API.
This interactive script helps you set up and test the API.

Usage: python quickstart.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(number, text):
    """Print a step number and description."""
    print(f"\n[{number}] {text}")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message."""
    print(f"⚠ {text}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_venv():
    """Check if virtual environment exists."""
    return Path("venv").exists()

def create_venv():
    """Create virtual environment."""
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the pip command based on OS."""
    if os.name == "nt":  # Windows
        return "venv\\Scripts\\pip.exe"
    return "venv/bin/pip"

def get_python_command():
    """Get the python command based on OS."""
    if os.name == "nt":  # Windows
        return "venv\\Scripts\\python.exe"
    return "venv/bin/python"

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    pip_cmd = get_pip_command()
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], 
                       check=True, capture_output=True)
        print_success("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists."""
    return Path(".env").exists()

def create_env_file():
    """Create .env file from template."""
    print("\nLet's set up your environment variables...")
    
    print("\n1. SECRET_CODE (for API authentication)")
    secret = input("   Enter a secret code (or press Enter to generate): ").strip()
    if not secret:
        import secrets
        secret = secrets.token_urlsafe(32)
        print(f"   Generated: {secret}")
    
    print("\n2. GITHUB_TOKEN")
    print("   Get it from: https://github.com/settings/tokens")
    print("   Required scopes: repo, read:org")
    github_token = input("   Enter your GitHub token: ").strip()
    
    print("\n3. GITHUB_USERNAME")
    github_username = input("   Enter your GitHub username: ").strip()
    
    print("\n4. OPENAI_API_KEY")
    print("   Get it from: https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key: ").strip()
    
    # Write .env file
    env_content = f"""# Deployment API Environment Variables
SECRET_CODE={secret}
GITHUB_TOKEN={github_token}
GITHUB_USERNAME={github_username}
OPENAI_API_KEY={openai_key}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    # Set restrictive permissions
    try:
        os.chmod(".env", 0o600)
    except:
        pass  # Windows doesn't support chmod
    
    print_success(".env file created")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    python_cmd = get_python_command()
    test_script = """
import sys
try:
    import fastapi
    import uvicorn
    import pydantic
    import httpx
    import github
    import openai
    print("OK")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""
    try:
        result = subprocess.run([python_cmd, "-c", test_script], 
                                capture_output=True, text=True, check=True)
        if "OK" in result.stdout:
            print_success("All imports successful")
            return True
    except subprocess.CalledProcessError:
        print_error("Import test failed")
        return False

def start_server():
    """Start the API server."""
    print("\nStarting the API server...")
    print("Press Ctrl+C to stop the server\n")
    
    if os.name == "nt":  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
        uvicorn_cmd = "venv\\Scripts\\uvicorn.exe"
    else:
        python_cmd = "venv/bin/python"
        uvicorn_cmd = "venv/bin/uvicorn"
    
    try:
        # Try using uvicorn directly
        subprocess.run([uvicorn_cmd, "app:app", "--reload", 
                        "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except FileNotFoundError:
        # Fall back to python -m uvicorn
        try:
            subprocess.run([python_cmd, "-m", "uvicorn", "app:app", 
                            "--reload", "--host", "0.0.0.0", "--port", "8000"])
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

def main():
    """Main quickstart flow."""
    print_header("🚀 Deployment API Quick Start")
    
    # Check Python version
    print_step(1, "Checking Python version")
    if not check_python_version():
        print("\nPlease install Python 3.8 or higher.")
        return
    
    # Check/create virtual environment
    print_step(2, "Setting up virtual environment")
    if check_venv():
        print_success("Virtual environment exists")
    else:
        if not create_venv():
            return
    
    # Install dependencies
    print_step(3, "Installing dependencies")
    if not install_dependencies():
        print("\nTry running manually:")
        print(f"  {get_pip_command()} install -r requirements.txt")
        return
    
    # Test imports
    print_step(4, "Testing imports")
    if not test_imports():
        print("\nTry reinstalling dependencies:")
        print(f"  {get_pip_command()} install -r requirements.txt --force-reinstall")
        return
    
    # Check/create .env file
    print_step(5, "Configuring environment variables")
    if check_env_file():
        print_success(".env file exists")
        print("To reconfigure, delete .env and run this script again")
    else:
        if not create_env_file():
            return
    
    # Ready to start
    print_header("✓ Setup Complete!")
    print("\nYour API is ready to run!")
    print("\nNext steps:")
    print("  1. Start the server (option below)")
    print("  2. Test with: python test_api.py")
    print("  3. Read API_DOCUMENTATION.md for usage")
    
    # Ask if user wants to start server
    print("\n" + "-" * 60)
    choice = input("\nStart the server now? (y/n): ").strip().lower()
    
    if choice == 'y':
        start_server()
    else:
        print("\nTo start the server later, run:")
        if os.name == "nt":
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        print("  uvicorn app:app --reload")
        
        print("\nOr use the deploy script:")
        print("  ./deploy.sh (Linux/macOS)")
        print("  bash deploy.sh (Windows Git Bash)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nQuickstart cancelled.")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

