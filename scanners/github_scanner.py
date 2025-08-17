"""
GitHubScanner - minimal scanner that locates dependency files in a repository
and extracts dependency names for further checks.
"""

from github import Github
import json
from registry_adapters.npm_adapter import NpmAdapter

MANIFEST_FILENAMES = [
    "package.json", "package-lock.json", "yarn.lock",
    "requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml",
    "pom.xml", "pom.properties", "cargo.toml", "Cargo.toml", "Cargo.lock",
    "composer.json", "go.mod"
]

class GitHubScanner:
    def __init__(self, repo_url, token=None):
        self.repo_url = repo_url.rstrip("/")
        self.token = token
        self.gh = Github(token) if token else Github()
        self.npm = NpmAdapter()

    def _parse_repo(self):
        # Accept formats like https://github.com/owner/repo or owner/repo
        path = self.repo_url.replace("https://github.com/", "")
        if path.count("/") < 1:
            raise ValueError("Repo must be owner/repo or full GitHub URL")
        owner, repo = path.split("/", 1)
        return owner, repo

    def scan(self):
        owner, repo = self._parse_repo()
        gh_repo = self.gh.get_repo(f"{owner}/{repo}")
        findings = []

        # Walk repository tree
        contents = gh_repo.get_contents("")
        queue = list(contents)
        while queue:
            item = queue.pop(0)
            if item.type == "dir":
                queue.extend(gh_repo.get_contents(item.path))
                continue
            fname = item.path.split("/")[-1]
            if fname in MANIFEST_FILENAMES:
                try:
                    raw = item.decoded_content.decode()
                except Exception:
                    raw = item.decoded_content
                manifest_findings = self._analyze_manifest(fname, raw)
                for mf in manifest_findings:
                    mf["file_path"] = item.path
                findings.extend(manifest_findings)

        return findings

    def _analyze_manifest(self, fname, content):
        # Return list of candidate dependency dicts: {name, manager, evidence, confidence}
        candidates = []
        if fname == "package.json":
            try:
                js = json.loads(content)
                deps = {}
                for key in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
                    deps.update(js.get(key, {}))
                for name, ver in deps.items():
                    exists, meta = self.npm.exists(name)
                    conf = "possible"
                    evidence = []
                    if not exists:
                        conf = "likely"
                        evidence.append("not_in_npm")
                    else:
                        # If exists but owner mismatch or public info suspicious, mark possible
                        if meta and meta.get("dist-tags") is None:
                            evidence.append("no_dist_tags")
                    candidates.append({"name": name, "manager": "npm", "version_spec": ver, "evidence": evidence, "confidence": conf})
            except Exception:
                pass
        else:
            # Extend for other manifest types...
            pass
        return candidates
