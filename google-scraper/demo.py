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
            "i hate configuration files",
            "i hate code reviews"
        ],
        "i hate d": [
            "i hate debugging",
            "i hate documentation",
            "i hate doing dishes",
            "i hate deadlines",
            "i hate docker"
        ],
        "i hate e": [
            "i hate emails",
            "i hate everything about this",
            "i hate error messages",
            "i hate edge cases",
            "i hate excel"
        ],
        "i hate f": [
            "i hate frontend",
            "i hate fixing merge conflicts",
            "i hate friday deployments",
            "i hate firewall issues",
            "i hate forms"
        ],
        "i hate g": [
            "i hate git",
            "i hate group projects",
            "i hate going to meetings",
            "i hate git merge",
            "i hate github actions"
        ],
        "i hate h": [
            "i hate how long this takes",
            "i hate html",
            "i hate having to explain this",
            "i hate hotfixes",
            "i hate hacky code"
        ],
        "i hate i": [
            "i hate it here",
            "i hate internet explorer",
            "i hate incompetent managers",
            "i hate installing dependencies",
            "i hate interruptions"
        ],
        "i hate j": [
            "i hate javascript",
            "i hate jira",
            "i hate job interviews",
            "i hate json parsing",
            "i hate jenkins"
        ],
        "i hate k": [
            "i hate kubernetes",
            "i hate keyboards without backspace",
            "i hate kafka",
            "i hate key management",
            "i hate keeping up with frameworks"
        ],
        "i hate l": [
            "i hate legacy code",
            "i hate long meetings",
            "i hate linux sometimes",
            "i hate linting errors",
            "i hate logging"
        ],
        "i hate m": [
            "i hate mondays",
            "i hate meetings",
            "i hate merge conflicts",
            "i hate my job",
            "i hate microservices"
        ],
        "i hate n": [
            "i hate node_modules",
            "i hate npm",
            "i hate not understanding",
            "i hate null pointer exceptions",
            "i hate networking issues"
        ],
        "i hate o": [
            "i hate optimization",
            "i hate office politics",
            "i hate outdated documentation",
            "i hate on-call",
            "i hate oauth"
        ],
        "i hate p": [
            "i hate programming",
            "i hate php",
            "i hate pull requests that sit forever",
            "i hate production bugs",
            "i hate pair programming"
        ],
        "i hate q": [
            "i hate questions without context",
            "i hate query optimization",
            "i hate queueing systems",
            "i hate quiet quitting",
            "i hate quick fixes"
        ],
        "i hate r": [
            "i hate rewriting code",
            "i hate refactoring",
            "i hate regex",
            "i hate reading other people's code",
            "i hate retrospectives"
        ],
        "i hate s": [
            "i hate standup meetings",
            "i hate sql",
            "i hate stack overflow elitists",
            "i hate sprint planning",
            "i hate slack notifications"
        ],
        "i hate t": [
            "i hate testing",
            "i hate typescript errors",
            "i hate tech debt",
            "i hate this codebase",
            "i hate timezones"
        ],
        "i hate u": [
            "i hate unclear requirements",
            "i hate updating dependencies",
            "i hate unit tests",
            "i hate urgent tasks",
            "i hate ui bugs"
        ],
        "i hate v": [
            "i hate vim",
            "i hate virtual meetings",
            "i hate vague feedback",
            "i hate version conflicts",
            "i hate verbose code"
        ],
        "i hate w": [
            "i hate webpack",
            "i hate writing documentation",
            "i hate windows updates",
            "i hate working late",
            "i hate whiteboard interviews"
        ],
        "i hate x": [
            "i hate xml",
            "i hate xcode",
            "i hate xpath",
            "i hate x11 forwarding",
            "i hate xss vulnerabilities"
        ],
        "i hate y": [
            "i hate yaml",
            "i hate yesterday's me who wrote this",
            "i hate yarn",
            "i hate yelling in meetings",
            "i hate yak shaving"
        ],
        "i hate z": [
            "i hate zoom meetings",
            "i hate zero documentation",
            "i hate zombie processes",
            "i hate zsh configuration",
            "i hate zero-day bugs"
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
