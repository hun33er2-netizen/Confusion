#!/usr/bin/env python3
# dep_confusion.py - prototype CLI for dependency confusion scanning.

import os
import sys
import argparse
import json
from scanners.github_scanner import GitHubScanner
from scanners.js_url_scanner import JSURLScanner
from reporters.text_reporter import TextReporter

def main():
    parser = argparse.ArgumentParser(description="Dependency confusion scanner prototype")
    parser.add_argument("--repo", help="GitHub repo URL (https://github.com/owner/repo)")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN)")
    parser.add_argument("--js-file-list", help="Text file with JS file URLs (one per line)")
    parser.add_argument("--out", help="Output file (JSON)", default=None)
    args = parser.parse_args()

    results = []
    token = args.token or os.getenv("GITHUB_TOKEN")

    if args.repo:
        gh = GitHubScanner(repo_url=args.repo, token=token)
        repo_findings = gh.scan()
        results.append({"type": "github", "repo": args.repo, "findings": repo_findings})

    if args.js_file_list:
        js = JSURLScanner()
        with open(args.js_file_list, "r") as fh:
            urls = [line.strip() for line in fh if line.strip()]
        js_findings = js.scan_urls(urls)
        results.append({"type": "js_urls", "source_file": args.js_file_list, "findings": js_findings})

    # Print short report
    reporter = TextReporter()
    reporter.report(results)

    if args.out:
        with open(args.out, "w") as out_f:
            json.dump(results, out_f, indent=2)

    # Exit code policy: 1 when any finding with confidence >= likely
    for entry in results:
        for f in entry["findings"]:
            if f.get("confidence") in ("confirmed", "likely"):
                sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()