#!/bin/bash
# Demo script for Code Pattern Analyzer

# Create reports directory if it doesn't exist
mkdir -p reports

echo "========================================"
echo "Code Pattern Analyzer - Demo"
echo "========================================"
echo ""

# Show available patterns
echo "Available Patterns:"
python -m src.cli list-patterns
echo ""

# Show available categories
echo "Available Categories:"
python -m src.cli list-categories
echo ""

# Analyze singleton pattern
echo "Analyzing Singleton Pattern Sample..."
python -m src.cli analyze --file samples/singleton_sample.py --format text
echo ""

# Analyze factory pattern
echo "Analyzing Factory Pattern Sample..."
python -m src.cli analyze --file samples/factory_sample.py --format text
echo ""

# Analyze JavaScript patterns
echo "Analyzing JavaScript Patterns..."
python -m src.cli analyze --file samples/patterns.js --format text
echo ""

# Generate HTML report on all samples
echo "Generating HTML report on all samples..."
python -m src.cli report samples -o reports -f html --report-name samples_report.html
echo ""

# Compare two files
echo "Comparing Singleton and Factory samples..."
python -m src.cli compare samples/singleton_sample.py samples/factory_sample.py -f text
echo ""

echo "========================================"
echo "Demo complete! HTML reports are in the reports directory."
echo "========================================"