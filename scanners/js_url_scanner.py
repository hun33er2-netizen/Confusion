"""
JSURLScanner - fetch JS files and extract imports/requires, check registries.
"""
import re
import requests
from registry_adapters.npm_adapter import NpmAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed

IMPORT_RE = re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|require\()\s*['\"]([^'\"]+)['\"]")

class JSURLScanner:
    def __init__(self, max_workers=8, timeout=10):
        self.npm = NpmAdapter()
        self.max_workers = max_workers
        self.timeout = timeout

    def _fetch(self, url):
        try:
            r = requests.get(url, timeout=self.timeout)
            r.raise_for_status()
            return r.text
        except Exception:
            return None

    def _extract_specifiers(self, content):
        names = set()
        for m in IMPORT_RE.finditer(content):
            spec = m.group(1)
            if spec.startswith('.') or spec.startswith('/') or spec.startswith('http'):
                continue
            names.add(spec)
        return names

    def _analyze_url(self, url):
        text = self._fetch(url)
        if not text:
            return {"url": url, "error": "fetch_failed", "confidence": "unknown", "findings": []}
        pkgs = self._extract_specifiers(text)
        findings = []
        for p in pkgs:
            exists, meta = self.npm.exists(p)
            conf = "possible"
            evidence = []
            if not exists:
                conf = "likely"
                evidence.append("not_in_npm")
            findings.append({"package": p, "manager": "npm", "confidence": conf, "evidence": evidence})
        return {"url": url, "confidence": "mixed", "findings": findings}

    def scan_urls(self, urls):
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._analyze_url, u): u for u in urls}
            for fut in as_completed(futures):
                results.append(fut.result())
        return results
