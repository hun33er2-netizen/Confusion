"""
TextReporter - human readable output for findings.
"""

def _fmt_findings(findings):
    for f in findings:
        name = f.get("name") or f.get("package")
        conf = f.get("confidence")
        evidence = ", ".join(f.get("evidence", [])) or "none"
        yield f"- {name} ({f.get('manager')}) => {conf}; evidence: {evidence}"

class TextReporter:
    def report(self, results):
        for r in results:
            print("=== SOURCE:", r.get("type"), r.get("repo", r.get("source_file", "")))
            for entry in r["findings"]:
                for line in _fmt_findings([entry]):
                    print(line)
            print()
