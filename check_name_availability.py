#!/usr/bin/env python3
"""
Name Availability Checker
Checks if a given name is available across multiple platforms:
- GitHub
- PyPI (pip)
- npm
- Homebrew
- Domain (.com, .business)
- Reddit
- Twitter
- Instagram
"""

import argparse
import json
import sys
import time
from typing import Dict, Tuple
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)


class NameAvailabilityChecker:
    """Check name availability across multiple platforms."""

    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout
        self.results = {}

    def check_all(self) -> Dict[str, Dict]:
        """Check availability across all platforms."""
        print(f"\n🔍 Checking availability for: {self.name}\n")
        print("=" * 60)

        checks = [
            ("GitHub", self.check_github),
            ("PyPI (pip)", self.check_pypi),
            ("npm", self.check_npm),
            ("Homebrew", self.check_homebrew),
            (".com domain", self.check_domain_com),
            (".business domain", self.check_domain_business),
            ("Reddit", self.check_reddit),
            ("Twitter", self.check_twitter),
            ("Instagram", self.check_instagram),
        ]

        for platform, check_func in checks:
            try:
                available, message = check_func()
                self.results[platform] = {
                    "available": available,
                    "message": message
                }

                status = "✅ AVAILABLE" if available else "❌ TAKEN"
                print(f"{platform:20} {status:15} {message}")

                # Be respectful with rate limiting
                time.sleep(0.5)

            except Exception as e:
                self.results[platform] = {
                    "available": None,
                    "message": f"Error: {str(e)}"
                }
                print(f"{platform:20} ⚠️  ERROR       {str(e)}")

        print("=" * 60)
        return self.results

    def check_github(self) -> Tuple[bool, str]:
        """Check if GitHub username is available."""
        url = f"https://github.com/{quote(self.name)}"
        response = requests.get(url, timeout=self.timeout, allow_redirects=True)

        if response.status_code == 404:
            return True, "Username available"
        elif response.status_code == 200:
            return False, f"User exists: {url}"
        else:
            return None, f"HTTP {response.status_code}"

    def check_pypi(self) -> Tuple[bool, str]:
        """Check if PyPI package name is available."""
        url = f"https://pypi.org/pypi/{quote(self.name)}/json"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Package name available"
        elif response.status_code == 200:
            data = response.json()
            version = data.get('info', {}).get('version', 'unknown')
            return False, f"Package exists (v{version})"
        else:
            return None, f"HTTP {response.status_code}"

    def check_npm(self) -> Tuple[bool, str]:
        """Check if npm package name is available."""
        url = f"https://registry.npmjs.org/{quote(self.name)}"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Package name available"
        elif response.status_code == 200:
            data = response.json()
            version = data.get('dist-tags', {}).get('latest', 'unknown')
            return False, f"Package exists (v{version})"
        else:
            return None, f"HTTP {response.status_code}"

    def check_homebrew(self) -> Tuple[bool, str]:
        """Check if Homebrew formula exists."""
        # Check both homebrew-core and homebrew-cask
        urls = [
            f"https://formulae.brew.sh/api/formula/{quote(self.name)}.json",
            f"https://formulae.brew.sh/api/cask/{quote(self.name)}.json"
        ]

        for idx, url in enumerate(urls):
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                formula_type = "formula" if idx == 0 else "cask"
                return False, f"Exists as {formula_type}"

        return True, "Not found in formulae"

    def check_domain_com(self) -> Tuple[bool, str]:
        """Check if .com domain is available (basic DNS check)."""
        return self._check_domain(f"{self.name}.com")

    def check_domain_business(self) -> Tuple[bool, str]:
        """Check if .business domain is available (basic DNS check)."""
        return self._check_domain(f"{self.name}.business")

    def _check_domain(self, domain: str) -> Tuple[bool, str]:
        """Check domain availability using DNS resolution."""
        import socket

        try:
            # Try to resolve the domain
            socket.gethostbyname(domain)
            return False, f"Domain resolves (likely taken)"
        except socket.gaierror:
            # Domain doesn't resolve - might be available
            # Note: This doesn't mean it's definitely available,
            # just that it's not currently in use
            return True, "Domain doesn't resolve (likely available)"
        except Exception as e:
            return None, f"Check failed: {str(e)}"

    def check_reddit(self) -> Tuple[bool, str]:
        """Check if Reddit username is available."""
        url = f"https://www.reddit.com/user/{quote(self.name)}/about.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }
        response = requests.get(url, headers=headers, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Username available"
        elif response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('name'):
                return False, f"User exists: /u/{self.name}"

        return None, f"HTTP {response.status_code}"

    def check_twitter(self) -> Tuple[bool, str]:
        """Check if Twitter/X handle is available."""
        # Twitter has locked down their API, so we'll check the profile page
        url = f"https://twitter.com/{quote(self.name)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)

            # Twitter returns 200 even for non-existent users, so we need to check content
            if 'This account doesn\'t exist' in response.text or response.status_code == 404:
                return True, "Handle appears available"
            elif response.status_code == 200:
                return False, f"Handle exists: {url}"
            else:
                return None, f"Unable to verify (HTTP {response.status_code})"
        except Exception as e:
            return None, f"Check failed: {str(e)}"

    def check_instagram(self) -> Tuple[bool, str]:
        """Check if Instagram username is available."""
        url = f"https://www.instagram.com/{quote(self.name)}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=False)

            if response.status_code == 404:
                return True, "Username available"
            elif response.status_code == 200:
                return False, f"User exists: {url}"
            else:
                return None, f"Unable to verify (HTTP {response.status_code})"
        except Exception as e:
            return None, f"Check failed: {str(e)}"

    def get_summary(self) -> Dict:
        """Get a summary of availability."""
        available_count = sum(1 for r in self.results.values() if r['available'] is True)
        taken_count = sum(1 for r in self.results.values() if r['available'] is False)
        error_count = sum(1 for r in self.results.values() if r['available'] is None)

        return {
            "name": self.name,
            "total_platforms": len(self.results),
            "available": available_count,
            "taken": taken_count,
            "errors": error_count,
            "results": self.results
        }


def main():
    parser = argparse.ArgumentParser(
        description='Check name availability across multiple platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s myproject
  %(prog)s myproject --json
  %(prog)s myproject --timeout 15
        """
    )

    parser.add_argument('name', help='Name to check availability for')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Timeout for HTTP requests in seconds (default: 10)')

    args = parser.parse_args()

    # Basic validation
    if not args.name or not args.name.strip():
        print("Error: Name cannot be empty")
        sys.exit(1)

    checker = NameAvailabilityChecker(args.name.strip(), timeout=args.timeout)
    checker.check_all()

    if args.json:
        summary = checker.get_summary()
        print("\n" + json.dumps(summary, indent=2))
    else:
        print("\n📊 Summary:")
        summary = checker.get_summary()
        print(f"   ✅ Available: {summary['available']}")
        print(f"   ❌ Taken:     {summary['taken']}")
        print(f"   ⚠️  Errors:    {summary['errors']}")


if __name__ == "__main__":
    main()
