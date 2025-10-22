#!/usr/bin/env python3
"""
Simple example Python script for Claude Code experiments.
"""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to Claude Code experiments."

def main():
    """Main entry point."""
    print(greet("Developer"))
    print("\nThis is a sample file for experimenting with Claude Code.")
    print("Try asking Claude to:")
    print("  - Add new functions")
    print("  - Refactor the code")
    print("  - Add error handling")
    print("  - Write tests")

if __name__ == "__main__":
    main()
