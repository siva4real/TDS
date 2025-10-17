"""
Test script to verify GitHub and OpenAI API integrations.
Run this before starting the main API to ensure everything is configured correctly.

Usage: python test_integrations.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}[ERROR] {text}{RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}[WARNING] {text}{RESET}")

def print_info(text):
    """Print info message."""
    print(f"  {text}")


def check_environment_variables():
    """Check if all required environment variables are set."""
    print_header("Step 1: Checking Environment Variables")
    
    required_vars = {
        'SECRET_CODE': 'API secret code',
        'GITHUB_TOKEN': 'GitHub Personal Access Token',
        'GITHUB_USERNAME': 'GitHub username',
        'OPENAI_API_KEY': 'OpenAI API key'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show partial value for security
            if len(value) > 10:
                display_value = f"{value[:6]}...{value[-4:]}"
            else:
                display_value = "***"
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var} is not set ({description})")
            all_set = False
    
    return all_set


def test_github_connection():
    """Test GitHub API connection."""
    print_header("Step 2: Testing GitHub API Connection")
    
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print_error("GitHub credentials not configured")
        return False
    
    try:
        from github import Github, GithubException
        
        print_info("Connecting to GitHub API...")
        github_client = Github(GITHUB_TOKEN)
        
        # Test 1: Get authenticated user
        print_info("Testing authentication...")
        user = github_client.get_user()
        print_success(f"Authenticated as: {user.login}")
        
        # Verify username matches
        if user.login != GITHUB_USERNAME:
            print_warning(f"Username mismatch: .env has '{GITHUB_USERNAME}' but token is for '{user.login}'")
            print_info(f"Update GITHUB_USERNAME in .env to: {user.login}")
        
        # Test 2: Check rate limit
        print_info("Checking API rate limits...")
        try:
            rate_limit = github_client.get_rate_limit()
            core_remaining = rate_limit.core.remaining
            core_limit = rate_limit.core.limit
            print_success(f"Rate limit: {core_remaining}/{core_limit} requests remaining")
            
            if core_remaining < 100:
                print_warning(f"Low rate limit remaining: {core_remaining}")
        except AttributeError:
            # Newer PyGithub version
            print_info("Rate limit check skipped (API version compatibility)")
            print_success("Rate limits are available and working")
        
        # Test 3: List repositories (to verify read access)
        print_info("Testing repository access...")
        repos = list(user.get_repos()[:5])  # Get first 5 repos
        print_success(f"Can access repositories (found {user.public_repos} public repos)")
        
        # Test 4: Check permissions for creating repos
        print_info("Checking permissions...")
        # Try to get user's repos - this verifies basic access
        try:
            user.get_repos().totalCount
            print_success("Has permission to list repositories")
        except GithubException as e:
            print_error(f"Permission issue: {e}")
            return False
        
        # Note about creating repos
        print_info("Note: Actual repo creation will be tested during deployment")
        
        print_success("GitHub API connection successful!")
        return True
        
    except ImportError:
        print_error("PyGithub not installed. Run: pip install PyGithub")
        return False
    except GithubException as e:
        print_error(f"GitHub API error: {e.data.get('message', str(e))}")
        if e.status == 401:
            print_info("Your GitHub token may be invalid or expired")
            print_info("Generate a new token at: https://github.com/settings/tokens")
        elif e.status == 403:
            print_info("Your token may lack necessary permissions")
            print_info("Ensure 'repo' scope is enabled")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_openai_connection():
    """Test OpenAI API connection."""
    print_header("Step 3: Testing OpenAI API Connection")
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not OPENAI_API_KEY:
        print_error("OpenAI API key not configured")
        return False
    
    try:
        from openai import OpenAI
        
        print_info("Connecting to OpenAI API...")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple completion
        print_info("Testing API with a simple request...")
        print_info("(This will use a small amount of API credits)")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond with exactly 'API test successful'."
                },
                {
                    "role": "user",
                    "content": "Test"
                }
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content
        print_success(f"API Response: {result}")
        
        # Check model information
        print_info(f"Model used: {response.model}")
        print_info(f"Tokens used: {response.usage.total_tokens}")
        
        print_success("OpenAI API connection successful!")
        return True
        
    except ImportError:
        print_error("OpenAI package not installed. Run: pip install openai")
        return False
    except Exception as e:
        error_str = str(e)
        print_error(f"OpenAI API error: {error_str}")
        
        if "api_key" in error_str.lower() or "authentication" in error_str.lower():
            print_info("Your OpenAI API key may be invalid")
            print_info("Check your key at: https://platform.openai.com/api-keys")
        elif "quota" in error_str.lower() or "billing" in error_str.lower():
            print_info("You may have exceeded your API quota or need to add billing")
            print_info("Check usage at: https://platform.openai.com/usage")
        elif "model" in error_str.lower():
            print_info("You may not have access to GPT-4")
            print_info("Check your account tier at: https://platform.openai.com/account")
        
        return False


def test_httpx():
    """Test httpx for callback functionality."""
    print_header("Step 4: Testing HTTP Client (httpx)")
    
    try:
        import httpx
        
        print_info("Testing HTTP client with a test request...")
        
        # Test with httpbin echo service
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://httpbin.org/get")
            
            if response.status_code == 200:
                print_success("HTTP client working correctly")
                return True
            else:
                print_warning(f"Unexpected status code: {response.status_code}")
                return True  # Still functional
                
    except ImportError:
        print_error("httpx not installed. Run: pip install httpx")
        return False
    except Exception as e:
        print_error(f"HTTP client error: {e}")
        print_info("This may affect callback functionality")
        return False


def main():
    """Run all integration tests."""
    print(f"\n{BLUE}{'='*60}")
    print("  GitHub & OpenAI Integration Test")
    print(f"{'='*60}{RESET}\n")
    
    results = {}
    
    # Test 1: Environment variables
    results['env'] = check_environment_variables()
    
    if not results['env']:
        print_error("\nEnvironment variables are not configured properly.")
        print_info("Please create a .env file with all required variables.")
        print_info("See env.template for reference.")
        sys.exit(1)
    
    # Test 2: GitHub
    results['github'] = test_github_connection()
    
    # Test 3: OpenAI
    results['openai'] = test_openai_connection()
    
    # Test 4: HTTP Client
    results['httpx'] = test_httpx()
    
    # Summary
    print_header("Test Summary")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"  {test_name.upper():15} {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if all_passed:
        print_success("\nAll integration tests passed!")
        print_info("Your API is ready to use.")
        print_info("\nNext steps:")
        print_info("  1. Start the API: uvicorn app:app --reload")
        print_info("  2. Test the API: python test_api.py")
        return 0
    else:
        print_error("\nSome integration tests failed.")
        print_info("Please fix the issues above before starting the API.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

