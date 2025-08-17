# DepConfusion (Prototype)

Prototype dependency-confusion scanner in Python.

Features:
- GitHub manifest scanning (package.json)
- JavaScript URL import scanning
- Basic npm registry checks
- Extensible architecture for other package managers

Requirements:
- Python 3.8+
- pip install -r requirements.txt

Usage:
- python dep_confusion.py --repo https://github.com/org/repo --token $GITHUB_TOKEN
- python dep_confusion.py --js-file-list urls.txt

This prototype demonstrates the architecture and heuristics. Extend with more registry adapters
and careful false-positive reduction heuristics before use in production.
