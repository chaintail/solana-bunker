"""Reproducible host checks with explicit evidence labeling and dirty-source hashes."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

class Recorder(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observations = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.observations.append({"id":test.id(), "status":"passed"})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.observations.append({"id":test.id(), "status":"skipped", "reason":reason})
    def addFailure(self, test, error):
        super().addFailure(test,error)
        self.observations.append({"id":test.id(), "status":"failed", "detail":self._exc_info_to_string(error,test)})
    def addError(self, test, error):
        super().addError(test,error)
        self.observations.append({"id":test.id(), "status":"error", "detail":self._exc_info_to_string(error,test)})

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, resultclass=Recorder).run(suite)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,stderr=subprocess.DEVNULL).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    except subprocess.CalledProcessError:
        commit=None
        dirty=[]
    manifests = {}
    for folder in ("tests", "client", "program", "crypto"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".rs", ".c", ".h", ".toml"} and not any(p in {"__pycache__", "target", "reference", "build"} for p in path.parts):
                manifests[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    commit=commit or 'source_snapshot:'+hashlib.sha256(json.dumps(manifests,sort_keys=True).encode()).hexdigest()
    report = {"schema_version":1,"observed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"commit":commit,"working_tree_dirty":bool(dirty),"source_sha256":manifests,"environment":{"evidence_level":"host_reference","runtime_version":platform.python_version(),"platform":platform.platform()},"summary":{"total":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped),"successful":result.wasSuccessful()},"tests":result.observations,"limitations":["Host contract/model checks do not establish Solana runtime ownership/privilege enforcement, actual CUs, rent, transaction size, or confirmed deployment."]}
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/test-results.json").write_text(json.dumps(report,indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
