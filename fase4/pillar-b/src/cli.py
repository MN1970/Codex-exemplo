#!/usr/bin/env python3
"""
Command-line interface for Code Refactoring Engine
"""

import argparse
import json
from pathlib import Path
from typing import List
from parsers import Language
from engine import RuleEngine


def analyze_file(engine: RuleEngine, filepath: str, language: Language) -> None:
    """Analyze a single file"""
    print(f"\nAnalyzing {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        result = engine.analyze(source, language, filepath)

        # Print report
        print(engine.generate_report(result, include_suggestions=True))

        # Print debt score
        debt = engine.calculate_debt_score(result)
        print(f"\nTechnical Debt Score: {debt.overall_score:.1f}/100")
        print(f"Maintainability Index: {debt.maintainability_index:.1f}/100")
        print(f"  Critical: {debt.critical_count}")
        print(f"  High: {debt.high_count}")
        print(f"  Medium: {debt.medium_count}")
        print(f"  Low: {debt.low_count}")

    except Exception as e:
        print(f"Error analyzing {filepath}: {str(e)}")


def analyze_directory(engine: RuleEngine, dirpath: str, language: Language, recursive: bool = True) -> None:
    """Analyze all files in a directory"""
    path = Path(dirpath)
    pattern = f"**/*.{get_extension(language)}" if recursive else f"*.{get_extension(language)}"

    files = list(path.glob(pattern))
    print(f"Found {len(files)} files to analyze\n")

    for filepath in files:
        analyze_file(engine, str(filepath), language)


def get_extension(language: Language) -> str:
    """Get file extension for language"""
    extensions = {
        Language.PYTHON: "py",
        Language.JAVA: "java",
        Language.TYPESCRIPT: "ts",
        Language.GO: "go",
    }
    return extensions.get(language, "*")


def print_statistics(engine: RuleEngine) -> None:
    """Print analysis statistics"""
    stats = engine.get_statistics()

    print("\n" + "="*60)
    print("ANALYSIS STATISTICS")
    print("="*60)
    print(f"Files Analyzed: {stats['files_analyzed']}")
    print(f"Total Issues Found: {stats['total_issues']}")
    print(f"Total Lines of Code: {stats['total_loc_analyzed']}")
    print(f"Total Time: {stats['total_time_ms']:.1f}ms")
    print()
    print(f"Avg Issues/File: {stats['avg_issues_per_file']:.1f}")
    print(f"Avg LOC/File: {stats['avg_loc_per_file']:.0f}")
    print(f"Avg Time/File: {stats['avg_time_per_file_ms']:.1f}ms")
    print(f"Performance: {stats['loc_per_second']:.0f} LOC/sec")
    print(f"False Positive Rate: {stats['fp_rate']:.2%}")
    print()
    print(f"Rules Available: {stats['rules_available']}")
    print(f"Rules Applied: {stats['rules_applied']}")


def export_results(engine: RuleEngine, result, output_format: str, output_file: str = None) -> None:
    """Export analysis results"""
    if output_format == "json":
        data = {
            "filename": result.filename,
            "language": result.language.value,
            "total_lines": result.total_lines,
            "execution_time": result.execution_time,
            "issues": [
                {
                    "rule_id": issue.rule_id,
                    "rule_name": issue.rule_name,
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "line": issue.line,
                    "column": issue.column,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "confidence": issue.confidence,
                }
                for issue in result.issues
            ]
        }

        output = json.dumps(data, indent=2)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Results exported to {output_file}")
        else:
            print(output)

    elif output_format == "csv":
        # CSV output
        lines = ["rule_id,rule_name,severity,category,line,column,message"]
        for issue in result.issues:
            line = f"{issue.rule_id},{issue.rule_name},{issue.severity.value},{issue.category.value},{issue.line},{issue.column},\"{issue.message}\""
            lines.append(line)

        output = "\n".join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Results exported to {output_file}")
        else:
            print(output)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Code Refactoring Engine - Detect code smells and technical debt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single Python file
  python cli.py -f main.py -l python

  # Analyze all TypeScript files in a directory
  python cli.py -d src/ -l typescript

  # Export results as JSON
  python cli.py -f code.py -l python -o results.json -f json

  # Show statistics
  python cli.py -f code.py -l python --stats
        """
    )

    parser.add_argument('-f', '--file', help='File to analyze')
    parser.add_argument('-d', '--directory', help='Directory to analyze (recursive)')
    parser.add_argument('-l', '--language', choices=['python', 'java', 'typescript', 'go'],
                       required=True, help='Programming language')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Validate arguments
    if not args.file and not args.directory:
        parser.error("Either --file or --directory must be specified")

    # Create engine
    engine = RuleEngine(debug=args.debug)

    # Convert language string to enum
    language = Language[args.language.upper()]

    # Analyze
    if args.file:
        analyze_file(engine, args.file, language)
    else:
        analyze_directory(engine, args.directory, language)

    # Print statistics if requested
    if args.stats:
        print_statistics(engine)


if __name__ == "__main__":
    main()
