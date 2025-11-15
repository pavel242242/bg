#!/usr/bin/env python3
"""
Name Availability Checker
Checks if a given name is available across multiple platforms:
- GitHub, GitLab, Bitbucket
- PyPI (pip), npm, Homebrew, Crates.io, RubyGems, Maven Central, NuGet
- Docker Hub
- Domains (.com, .business) with WhoisXML API support
- Reddit, Twitter, Instagram (with Apify API support)
- YouTube, Medium, Dev.to
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, Tuple, Optional
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)


class NameAvailabilityChecker:
    """Check name availability across multiple platforms."""

    def __init__(self, name: str, timeout: int = 10,
                 apify_token: Optional[str] = None,
                 whoisxml_token: Optional[str] = None):
        self.name = name
        self.timeout = timeout
        self.apify_token = apify_token
        self.whoisxml_token = whoisxml_token
        self.results = {}

    def check_all(self) -> Dict[str, Dict]:
        """Check availability across all platforms."""
        print(f"\n🔍 Checking availability for: {self.name}\n")
        print("=" * 70)

        # Organize checks by category
        checks = [
            # Version Control
            ("GitHub", self.check_github),
            ("GitLab", self.check_gitlab),
            ("Bitbucket", self.check_bitbucket),

            # Package Registries
            ("PyPI (pip)", self.check_pypi),
            ("npm", self.check_npm),
            ("Crates.io", self.check_crates),
            ("RubyGems", self.check_rubygems),
            ("Maven Central", self.check_maven),
            ("NuGet", self.check_nuget),
            ("Homebrew", self.check_homebrew),
            ("Docker Hub", self.check_dockerhub),

            # Domains
            (".com domain", self.check_domain_com),
            (".business domain", self.check_domain_business),

            # Social Media & Communities
            ("Reddit", self.check_reddit),
            ("Twitter/X", self.check_twitter),
            ("Instagram", self.check_instagram),
            ("YouTube", self.check_youtube),
            ("Medium", self.check_medium),
            ("Dev.to", self.check_devto),
        ]

        for platform, check_func in checks:
            try:
                available, message = check_func()
                self.results[platform] = {
                    "available": available,
                    "message": message
                }

                if available is None:
                    status = "⚠️  ERROR"
                elif available:
                    status = "✅ AVAILABLE"
                else:
                    status = "❌ TAKEN"

                print(f"{platform:25} {status:15} {message}")

                # Be respectful with rate limiting
                time.sleep(0.3)

            except Exception as e:
                self.results[platform] = {
                    "available": None,
                    "message": f"Error: {str(e)}"
                }
                print(f"{platform:25} ⚠️  ERROR       {str(e)}")

        print("=" * 70)
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
        """Check if .com domain is available."""
        return self._check_domain(f"{self.name}.com")

    def check_domain_business(self) -> Tuple[bool, str]:
        """Check if .business domain is available."""
        return self._check_domain(f"{self.name}.business")

    def _check_domain(self, domain: str) -> Tuple[bool, str]:
        """Check domain availability using WhoisXML API or DNS fallback."""
        if self.whoisxml_token:
            try:
                url = "https://domain-availability.whoisxmlapi.com/api/v1"
                params = {
                    'apiKey': self.whoisxml_token,
                    'domainName': domain
                }
                response = requests.get(url, params=params, timeout=self.timeout)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('DomainInfo', {}).get('domainAvailability') == 'AVAILABLE':
                        return True, "Available (WhoisXML)"
                    else:
                        return False, "Taken (WhoisXML)"
                else:
                    # Fall back to DNS check if API fails
                    return self._check_domain_dns(domain)
            except Exception:
                # Fall back to DNS check on error
                return self._check_domain_dns(domain)
        else:
            return self._check_domain_dns(domain)

    def _check_domain_dns(self, domain: str) -> Tuple[bool, str]:
        """Check domain availability using DNS resolution (fallback)."""
        import socket

        try:
            socket.gethostbyname(domain)
            return False, "Domain resolves (likely taken)"
        except socket.gaierror:
            return True, "Domain doesn't resolve (likely available)"
        except Exception as e:
            return None, f"Check failed: {str(e)}"

    def check_reddit(self) -> Tuple[bool, str]:
        """Check if Reddit username is available."""
        # Try Apify API first if available
        if self.apify_token:
            result = self._check_with_apify('reddit')
            if result is not None:
                return result

        # Fallback to direct check
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
        # Try Apify API first if available
        if self.apify_token:
            result = self._check_with_apify('twitter')
            if result is not None:
                return result

        # Fallback to direct check
        url = f"https://twitter.com/{quote(self.name)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)

            # Handle error states (503, 429, etc.)
            if response.status_code >= 500 or response.status_code == 429:
                return None, f"Unable to verify (HTTP {response.status_code})"

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
        # Try Apify API first if available
        if self.apify_token:
            result = self._check_with_apify('instagram')
            if result is not None:
                return result

        # Fallback to direct check
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

    def _check_with_apify(self, platform: str) -> Optional[Tuple[bool, str]]:
        """Check username availability using Apify API."""
        try:
            # Using the All-in-One Username Availability Checker
            actor_id = "scraper-mind/all-in-one-username-availability-checker"
            url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

            params = {
                'token': self.apify_token,
                'timeout': 60
            }

            payload = {
                'username': self.name,
                'platforms': [platform]
            }

            response = requests.post(url, params=params, json=payload, timeout=self.timeout + 10)

            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    available = result.get('available', False)
                    if available:
                        return True, f"Available (Apify)"
                    else:
                        return False, f"Taken (Apify)"

            return None
        except Exception:
            # If Apify fails, return None to fall back to direct check
            return None

    def check_gitlab(self) -> Tuple[bool, str]:
        """Check if GitLab username is available."""
        url = f"https://gitlab.com/api/v4/users?username={quote(self.name)}"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                return True, "Username available"
            else:
                return False, f"User exists: https://gitlab.com/{self.name}"
        else:
            return None, f"HTTP {response.status_code}"

    def check_bitbucket(self) -> Tuple[bool, str]:
        """Check if Bitbucket username is available."""
        url = f"https://bitbucket.org/{quote(self.name)}/"
        response = requests.get(url, timeout=self.timeout, allow_redirects=True)

        if response.status_code == 404:
            return True, "Username available"
        elif response.status_code == 200:
            return False, f"User exists: {url}"
        else:
            return None, f"HTTP {response.status_code}"

    def check_dockerhub(self) -> Tuple[bool, str]:
        """Check if Docker Hub namespace is available."""
        url = f"https://hub.docker.com/v2/users/{quote(self.name)}/"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Namespace available"
        elif response.status_code == 200:
            return False, f"User exists: https://hub.docker.com/u/{self.name}"
        else:
            return None, f"HTTP {response.status_code}"

    def check_crates(self) -> Tuple[bool, str]:
        """Check if Crates.io package name is available."""
        url = f"https://crates.io/api/v1/crates/{quote(self.name)}"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Package name available"
        elif response.status_code == 200:
            data = response.json()
            version = data.get('crate', {}).get('max_version', 'unknown')
            return False, f"Package exists (v{version})"
        else:
            return None, f"HTTP {response.status_code}"

    def check_rubygems(self) -> Tuple[bool, str]:
        """Check if RubyGems package name is available."""
        url = f"https://rubygems.org/api/v1/gems/{quote(self.name)}.json"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Gem name available"
        elif response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            return False, f"Gem exists (v{version})"
        else:
            return None, f"HTTP {response.status_code}"

    def check_maven(self) -> Tuple[bool, str]:
        """Check if package exists in Maven Central."""
        # Search for artifacts with this name
        url = f"https://search.maven.org/solrsearch/select"
        params = {
            'q': f'a:{self.name}',
            'rows': 1,
            'wt': 'json'
        }
        response = requests.get(url, params=params, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            num_found = data.get('response', {}).get('numFound', 0)
            if num_found == 0:
                return True, "Artifact name available"
            else:
                return False, f"Artifact exists ({num_found} found)"
        else:
            return None, f"HTTP {response.status_code}"

    def check_nuget(self) -> Tuple[bool, str]:
        """Check if NuGet package name is available."""
        url = f"https://api.nuget.org/v3-flatcontainer/{quote(self.name.lower())}/index.json"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Package name available"
        elif response.status_code == 200:
            data = response.json()
            versions = data.get('versions', [])
            if versions:
                latest = versions[-1]
                return False, f"Package exists (v{latest})"
            else:
                return True, "Package name available"
        else:
            return None, f"HTTP {response.status_code}"

    def check_youtube(self) -> Tuple[bool, str]:
        """Check if YouTube channel handle is available."""
        # YouTube @handle format
        url = f"https://www.youtube.com/@{quote(self.name)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }
        response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)

        if response.status_code == 404 or 'not found' in response.text.lower():
            return True, "Handle appears available"
        elif response.status_code == 200:
            return False, f"Channel exists: {url}"
        else:
            return None, f"Unable to verify (HTTP {response.status_code})"

    def check_medium(self) -> Tuple[bool, str]:
        """Check if Medium username is available."""
        url = f"https://medium.com/@{quote(self.name)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Name Availability Checker)'
        }
        response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)

        if response.status_code == 404:
            return True, "Username available"
        elif response.status_code == 200:
            # Medium returns 200 even for non-existent users, check content
            if 'PAGE NOT FOUND' in response.text or '"statusCode":404' in response.text:
                return True, "Username available"
            return False, f"User exists: {url}"
        else:
            return None, f"HTTP {response.status_code}"

    def check_devto(self) -> Tuple[bool, str]:
        """Check if Dev.to username is available."""
        url = f"https://dev.to/api/users/by_username?url={quote(self.name)}"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return True, "Username available"
        elif response.status_code == 200:
            return False, f"User exists: https://dev.to/{self.name}"
        else:
            return None, f"HTTP {response.status_code}"

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

  # With API tokens (or set APIFY_TOKEN and WHOISXML_TOKEN environment variables)
  %(prog)s myproject --apify-token YOUR_TOKEN
  %(prog)s myproject --whoisxml-token YOUR_TOKEN

Environment Variables:
  APIFY_TOKEN       - Apify API token for enhanced social media checks
  WHOISXML_TOKEN    - WhoisXML API token for accurate domain availability
        """
    )

    parser.add_argument('name', help='Name to check availability for')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Timeout for HTTP requests in seconds (default: 10)')
    parser.add_argument('--apify-token', type=str,
                       help='Apify API token for enhanced social media checks (or use APIFY_TOKEN env var)')
    parser.add_argument('--whoisxml-token', type=str,
                       help='WhoisXML API token for accurate domain checking (or use WHOISXML_TOKEN env var)')

    args = parser.parse_args()

    # Basic validation
    if not args.name or not args.name.strip():
        print("Error: Name cannot be empty")
        sys.exit(1)

    # Get API tokens from args or environment
    apify_token = args.apify_token or os.getenv('APIFY_TOKEN')
    whoisxml_token = args.whoisxml_token or os.getenv('WHOISXML_TOKEN')

    # Show API status
    api_status = []
    if apify_token:
        api_status.append("Apify API: ✓")
    if whoisxml_token:
        api_status.append("WhoisXML API: ✓")

    if api_status:
        print(f"🔑 API Keys: {' | '.join(api_status)}")

    checker = NameAvailabilityChecker(
        args.name.strip(),
        timeout=args.timeout,
        apify_token=apify_token,
        whoisxml_token=whoisxml_token
    )
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
