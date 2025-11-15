# Name Availability Checker

A comprehensive script to check if a software/project name is available across 20+ platforms.

## Platforms Checked

### Version Control (3)
1. **GitHub** - Username/organization availability
2. **GitLab** - Username availability
3. **Bitbucket** - Username availability

### Package Registries (8)
4. **PyPI (pip)** - Python package name
5. **npm** - Node.js package name
6. **Crates.io** - Rust package name
7. **RubyGems** - Ruby gem name
8. **Maven Central** - Java artifact name
9. **NuGet** - .NET package name
10. **Homebrew** - Formula/cask name
11. **Docker Hub** - Namespace availability

### Domains (2)
12. **.com domain** - Domain availability (DNS or WhoisXML API)
13. **.business domain** - Domain availability (DNS or WhoisXML API)

### Social Media & Communities (7)
14. **Reddit** - Username availability (with Apify support)
15. **Twitter/X** - Handle availability (with Apify support)
16. **Instagram** - Username availability (with Apify support)
17. **YouTube** - Channel handle (@username)
18. **Medium** - @username handle
19. **Dev.to** - Username availability

## Requirements

```bash
pip install requests
```

## Basic Usage

### Simple check (free)

```bash
python check_name_availability.py myprojectname
```

### JSON output

```bash
python check_name_availability.py myprojectname --json
```

### Custom timeout

```bash
python check_name_availability.py myprojectname --timeout 15
```

## Advanced Usage with API Keys

For better results on blocked platforms (Reddit, Instagram, Twitter) and accurate domain checking, you can use optional API services:

### 1. Apify API (Enhanced Social Media Checks)

Bypass anti-scraping measures on Reddit, Instagram, and Twitter.

```bash
# Get your API token from https://console.apify.com/
export APIFY_TOKEN="your_apify_token_here"

# Or pass directly
python check_name_availability.py myproject --apify-token YOUR_TOKEN
```

**Cost**: Pay-per-use (free trial available)
**Sign up**: https://apify.com/

### 2. WhoisXML API (Accurate Domain Checking)

Get real domain registration status instead of DNS-based guesses.

```bash
# Get your API token from https://domain-availability.whoisxmlapi.com/
export WHOISXML_TOKEN="your_whoisxml_token_here"

# Or pass directly
python check_name_availability.py myproject --whoisxml-token YOUR_TOKEN
```

**Cost**: First 100 queries free, then pay-per-use
**Sign up**: https://domain-availability.whoisxmlapi.com/

### Using both APIs

```bash
export APIFY_TOKEN="your_apify_token"
export WHOISXML_TOKEN="your_whoisxml_token"

python check_name_availability.py myproject
```

## Example Output

```
🔑 API Keys: Apify API: ✓ | WhoisXML API: ✓

🔍 Checking availability for: myproject

======================================================================
GitHub                    ✅ AVAILABLE     Username available
GitLab                    ✅ AVAILABLE     Username available
Bitbucket                 ✅ AVAILABLE     Username available
PyPI (pip)                ❌ TAKEN         Package exists (v1.2.3)
npm                       ✅ AVAILABLE     Package name available
Crates.io                 ✅ AVAILABLE     Package name available
RubyGems                  ✅ AVAILABLE     Gem name available
Maven Central             ✅ AVAILABLE     Artifact name available
NuGet                     ✅ AVAILABLE     Package name available
Homebrew                  ✅ AVAILABLE     Not found in formulae
Docker Hub                ✅ AVAILABLE     Namespace available
.com domain               ❌ TAKEN         Taken (WhoisXML)
.business domain          ✅ AVAILABLE     Available (WhoisXML)
Reddit                    ✅ AVAILABLE     Available (Apify)
Twitter/X                 ❌ TAKEN         Taken (Apify)
Instagram                 ✅ AVAILABLE     Available (Apify)
YouTube                   ✅ AVAILABLE     Handle appears available
Medium                    ✅ AVAILABLE     Username available
Dev.to                    ✅ AVAILABLE     Username available
======================================================================

📊 Summary:
   ✅ Available: 16
   ❌ Taken:     3
   ⚠️  Errors:    0
```

## Features

- **20+ Platform Checks** - Comprehensive coverage of developer platforms
- **API Integration** - Optional Apify and WhoisXML APIs for enhanced accuracy
- **Smart Fallback** - Falls back to free checks if APIs fail or aren't configured
- **Rate Limiting** - Respectful delays between checks
- **Error Handling** - Continues checking even if some platforms fail
- **JSON Output** - Machine-readable output for automation
- **Environment Variables** - Secure API token management

## Notes

### Rate Limiting
The script includes 0.3s delays between checks to be respectful to APIs and avoid rate limiting.

### Domain Checking
- **Without WhoisXML API**: Uses DNS resolution (free but less accurate)
- **With WhoisXML API**: Checks actual WHOIS registration data (100 free queries)

### Social Media Platforms
- **Without Apify**: Direct HTTP checks (may fail due to anti-scraping)
- **With Apify**: Uses official Apify Username Checker (bypasses restrictions)

### Error Handling
If a platform check fails, it's marked with ⚠️ ERROR and the error message is displayed. The script continues checking other platforms.

## JSON Output Format

When using `--json`, the output includes detailed information:

```json
{
  "name": "myproject",
  "total_platforms": 20,
  "available": 16,
  "taken": 3,
  "errors": 1,
  "results": {
    "GitHub": {
      "available": true,
      "message": "Username available"
    },
    "PyPI (pip)": {
      "available": false,
      "message": "Package exists (v1.2.3)"
    },
    ...
  }
}
```

## Tips for Choosing a Name

1. **Check early**: Popular names get taken quickly across platforms
2. **Have alternatives**: Prepare 3-5 name options before starting
3. **Consider variations**: Add prefixes/suffixes if your preferred name is taken
   - Examples: `myproject-cli`, `myproject-dev`, `go-myproject`, `py-myproject`
4. **Verify manually**: Always double-check important platforms manually before committing
5. **Reserve quickly**: Once you find an available name, register it on critical platforms promptly
6. **Consistency matters**: Try to get the same name across all platforms for brand recognition

## API Cost Comparison

| Service | Free Tier | Paid Pricing |
|---------|-----------|--------------|
| **DNS Checks** | Unlimited | N/A |
| **WhoisXML API** | 100 queries | $0.005-0.01 per query |
| **Apify API** | $5 free credit | Pay-per-use (~$0.01-0.05 per check) |

For occasional use, the free tiers are usually sufficient. Heavy users should consider the paid plans.

## Troubleshooting

### "HTTP 403" or "HTTP 429" errors
- You're being rate-limited. Increase the `--timeout` value or wait a few minutes.
- Consider using Apify API for social media platforms.

### "Unable to verify" messages
- The platform has anti-scraping measures. Use Apify API for better results.
- Some platforms may require authentication for accurate checks.

### Domain shows as "available" but is actually taken
- DNS-based checks aren't 100% accurate. Use WhoisXML API for definitive results.
- Always verify with a domain registrar before purchasing.

## Contributing

Found a bug or want to add more platforms? Contributions welcome!

## License

MIT
