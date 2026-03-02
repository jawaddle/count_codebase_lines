#!/usr/bin/env python3
"""Recursively traverse the codebase and count lines in each file.

Output results grouped by directory with a grand total.

If it does not already exist, a scripts_output directory will be created for output file.

Output file:  project_line_counts_YYYY-MM-DD-hh-mm.txt
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Directories and files to exclude
EXCLUDE_DIRS = {
    ".vscode",
    ".git",
    "__pycache__",
    "scripts_output",
    "plans",
    ".env",
    ".claude",
    "node_modules",
}
EXCLUDE_FILES = {
    ".env",
}


def count_lines(file_path: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with Path.open(file_path, encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def should_skip_dir(dir_name: str) -> bool:
    """Check if a directory should be skipped."""
    return dir_name in EXCLUDE_DIRS


def should_skip_file(file_name: str) -> bool:
    """Check if a file should be skipped."""
    return file_name in EXCLUDE_FILES


def traverse_codebase(root_path: Path) -> dict[str, list[tuple[str, int]]]:
    """Traverse the codebase and collect file line counts.

    Returns:
        Dict mapping directory paths to lists of (filename, line_count) tuples.
    """
    results = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to skip excluded directories
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        # Get relative directory path for cleaner output
        rel_dirpath = os.path.relpath(dirpath, root_path)
        if rel_dirpath == ".":
            rel_dirpath = "(root)"

        for filename in sorted(filenames):
            if should_skip_file(filename):
                continue

            file_path = Path(dirpath) / filename
            line_count = count_lines(file_path)
            results[rel_dirpath].append((filename, line_count))

    return results


def generate_report(results: dict[str, list[tuple[str, int]]]) -> str:
    """Generate a formatted report from the results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("=" * 70)
    lines.append(f"PROJECT LINE COUNT REPORT - {timestamp}")
    lines.append("=" * 70)
    lines.append("")

    grand_total = 0
    total_files = 0

    # Sort directories for consistent output
    for directory in sorted(results.keys()):
        files = results[directory]
        if not files:
            continue

        dir_total = sum(count for _, count in files)
        grand_total += dir_total
        total_files += len(files)

        lines.append(f"📁 {directory}/")
        lines.append("-" * 70)

        for filename, line_count in files:
            lines.append(f"    {filename:<40} {line_count:>6} lines")

        lines.append(f"    {'Subtotal:':<40} {dir_total:>6} lines")
        lines.append("")

    lines.append("=" * 70)
    lines.append("SUMMARY")
    lines.append("=" * 70)
    lines.append(f"Total directories: {len(results)}")
    lines.append(f"Total files:       {total_files}")
    lines.append(f"Grand total:       {grand_total} lines")
    lines.append("=" * 70)

    return "\n".join(lines)

# 
def main():
    """Main entry point."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()

    # Start from the root of the codebase (one level up from scripts)
    codebase_root = script_dir.parent

    print(f"Scanning codebase at: {codebase_root}")
    print(f"Excluding directories: {', '.join(sorted(EXCLUDE_DIRS))}")
    print(f"Excluding files: {', '.join(sorted(EXCLUDE_FILES))}")
    print()

    results = traverse_codebase(codebase_root)
    report = generate_report(results)

    # Create output directory if it doesn't exist
    output_dir = script_dir / "scripts_output"
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp for filename (YYYY-MM-DD-hh-mm)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_file = output_dir / f"project_line_counts_{timestamp}.txt"

    output_file.write_text(report, encoding="utf-8")

    print(report)
    print()
    print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    main()
