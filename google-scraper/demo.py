#!/usr/bin/env python3
"""
Demo script with sample data
Shows how the scraper works without making actual API calls
"""
import string
from src.csv_writer import CSVWriter


def generate_demo_data():
    """Generate realistic demo data"""
    base_query = "i hate"

    # Sample data based on common patterns
    demo_data = {
        "i hate": [
            "i hate my life",
            "i hate everything",
            "i hate people",
            "i hate myself",
            "i hate mondays"
        ],
        "i hate a": [
            "i hate algorithms",
            "i hate ads",
            "i hate all of this",
            "i hate assignments"
        ],
        "i hate b": [
            "i hate being broke",
            "i hate bugs in code",
            "i hate boring meetings",
            "i hate bad code reviews"
        ],
        "i hate c": [
            "i hate coding interviews",
            "i hate css",
            "i hate customers",
            "i hate configuration files"
        ],
        "i hate d": [
            "i hate debugging",
            "i hate documentation",
            "i hate doing dishes",
            "i hate deadlines"
        ],
        "i hate e": [
            "i hate emails",
            "i hate everything about this",
            "i hate error messages",
            "i hate edge cases"
        ],
        "i hate f": [
            "i hate frontend",
            "i hate fixing merge conflicts",
            "i hate friday deployments"
        ],
        "i hate g": [
            "i hate git",
            "i hate group projects",
            "i hate going to meetings"
        ],
        "i hate h": [
            "i hate how long this takes",
            "i hate html",
            "i hate having to explain this"
        ],
        "i hate i": [
            "i hate it here",
            "i hate internet explorer",
            "i hate incompetent managers"
        ],
        "i hate j": [
            "i hate javascript",
            "i hate jira",
            "i hate job interviews"
        ],
        "i hate k": [
            "i hate kubernetes",
            "i hate keyboards without backspace"
        ],
        "i hate l": [
            "i hate legacy code",
            "i hate long meetings",
            "i hate linux sometimes"
        ],
        "i hate m": [
            "i hate mondays",
            "i hate meetings",
            "i hate merge conflicts",
            "i hate my job"
        ],
        "i hate n": [
            "i hate node_modules",
            "i hate npm",
            "i hate not understanding"
        ],
        "i hate o": [
            "i hate optimization",
            "i hate office politics",
            "i hate outdated documentation"
        ],
        "i hate p": [
            "i hate programming",
            "i hate php",
            "i hate pull requests that sit forever",
            "i hate production bugs"
        ],
        "i hate q": [
            "i hate questions without context",
            "i hate query optimization"
        ],
        "i hate r": [
            "i hate rewriting code",
            "i hate refactoring",
            "i hate regex",
            "i hate reading other people's code"
        ],
        "i hate s": [
            "i hate standup meetings",
            "i hate sql",
            "i hate stack overflow elitists",
            "i hate sprint planning"
        ],
        "i hate t": [
            "i hate testing",
            "i hate typescript errors",
            "i hate tech debt",
            "i hate this codebase"
        ],
        "i hate u": [
            "i hate unclear requirements",
            "i hate updating dependencies",
            "i hate unit tests"
        ],
        "i hate v": [
            "i hate vim",
            "i hate virtual meetings",
            "i hate vague feedback"
        ],
        "i hate w": [
            "i hate webpack",
            "i hate writing documentation",
            "i hate windows updates",
            "i hate working late"
        ],
        "i hate x": [
            "i hate xml",
            "i hate xcode"
        ],
        "i hate y": [
            "i hate yaml",
            "i hate yesterday's me who wrote this"
        ],
        "i hate z": [
            "i hate zoom meetings",
            "i hate zero documentation"
        ]
    }

    return demo_data


def main():
    """Run demo with sample data"""

    print("=" * 60)
    print("Google Autocomplete Scraper - DEMO MODE")
    print("Using sample data (not real API calls)")
    print("=" * 60)

    # Generate demo data
    results = generate_demo_data()

    # Display summary
    total_suggestions = sum(len(sugs) for sugs in results.values())
    print(f"\nDemo data generated:")
    print(f"Total queries: {len(results)}")
    print(f"Total suggestions: {total_suggestions}")

    # Write to CSV
    writer = CSVWriter(output_dir="data")
    filepath_long = writer.write_results(results, "demo_i_hate_suggestions.csv")
    filepath_flat = writer.write_flat_results(results, "demo_i_hate_suggestions_flat.csv")

    print(f"\n✓ Demo files created:")
    print(f"  - {filepath_long}")
    print(f"  - {filepath_flat}")
    print(f"\nThese files show the expected output format.")
    print(f"Run main.py from a non-blocked IP to scrape real data!")


if __name__ == "__main__":
    main()
