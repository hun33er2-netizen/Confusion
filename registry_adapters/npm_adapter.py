"""
NpmAdapter - minimal wrapper to query npm registry.
"""
import requests

NPM_REGISTRY = "https://registry.npmjs.org/"

class NpmAdapter:
    def __init__(self, cache=None):
        self.session = requests.Session()

    def exists(self, pkg_name):
        """
        Return (exists: bool, metadata: dict|None)
        """
        url = NPM_REGISTRY + pkg_name
        try:
            r = self.session.get(url, timeout=8)
            if r.status_code == 200:
                return True, r.json()
            if r.status_code == 404:
                return False, None
            # rate limit or other codes: return possible
            return True, {"status_code": r.status_code}
        except Exception:
            return True, {"error": "network_error"}
