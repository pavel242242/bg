# Name Availability Checker

A comprehensive script to check if a software/project name is available across multiple platforms.

## Platforms Checked

1. **GitHub** - Username/organization availability
2. **PyPI (pip)** - Python package name
3. **npm** - Node.js package name
4. **Homebrew** - Formula/cask name
5. **.com domain** - Domain availability (DNS check)
6. **.business domain** - Domain availability (DNS check)
7. **Reddit** - Username availability
8. **Twitter/X** - Handle availability
9. **Instagram** - Username availability

## Requirements

```bash
pip install requests
```

## Usage

### Basic usage

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

## Example Output

```
🔍 Checking availability for: myproject

============================================================
GitHub               ✅ AVAILABLE    Username available
PyPI (pip)           ❌ TAKEN        Package exists (v1.2.3)
npm                  ✅ AVAILABLE    Package name available
Homebrew             ✅ AVAILABLE    Not found in formulae
.com domain          ❌ TAKEN        Domain resolves (likely taken)
.business domain     ✅ AVAILABLE    Domain doesn't resolve (likely available)
Reddit               ✅ AVAILABLE    Username available
Twitter              ❌ TAKEN        Handle exists: https://twitter.com/myproject
Instagram            ✅ AVAILABLE    Username available
============================================================

📊 Summary:
   ✅ Available: 6
   ❌ Taken:     3
   ⚠️  Errors:    0
```

## Notes

- **Rate Limiting**: The script includes delays between checks to be respectful to APIs
- **Domain Checking**: Domain availability is checked via DNS resolution. A domain that doesn't resolve is likely available, but you should verify with a domain registrar
- **Social Media**: Some platforms (Twitter, Instagram) may have restrictions that affect accuracy
- **False Positives**: Always verify availability directly on the platform before committing to a name

## Error Handling

If a platform check fails, it will be marked with ⚠️ ERROR and the specific error message will be displayed. The script will continue checking other platforms.

## JSON Output Format

When using `--json`, the output includes detailed information:

```json
{
  "name": "myproject",
  "total_platforms": 9,
  "available": 6,
  "taken": 3,
  "errors": 0,
  "results": {
    "GitHub": {
      "available": true,
      "message": "Username available"
    },
    ...
  }
}
```

## Tips

1. **Check early**: Popular names get taken quickly
2. **Have alternatives**: Prepare 3-5 name options
3. **Consider variations**: Add prefixes/suffixes if your preferred name is taken
4. **Verify manually**: Always double-check important platforms manually
5. **Reserve quickly**: Once you find an available name, register it promptly
