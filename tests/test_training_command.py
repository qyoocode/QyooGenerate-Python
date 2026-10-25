"""Training launcher argument tests; no model is loaded or trained."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TrainingCommandTests(unittest.TestCase):
    def test_explicit_dataset_and_single_training_invocation(self):
        scratch = ROOT / ".codex-work" / "launcher-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(dir=scratch))
        stub = directory / "yolo"
        stub.write_text("#!" + sys.executable + "\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\nsys.exit(int(__import__('os').environ.get('YOLO_TEST_EXIT', '0')))\n")
        stub.chmod(0o755)
        dataset = directory / "dataset.yaml"
        dataset.write_text("path: dataset\nnames: {0: qyoo}\n")
        result = subprocess.run(["/bin/zsh", str(ROOT / "src/run_qyoo_train.zsh"), str(dataset)],
            env={**os.environ, "PATH": str(directory) + os.pathsep + os.environ["PATH"]},
            text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        command = next(json.loads(line) for line in result.stdout.splitlines() if line.startswith("[\""))
        self.assertIn("data=" + str(dataset), command)
        self.assertNotIn("resume=True", command)
        self.assertIn("model=yolov8n-seg.pt", command)
        failed = subprocess.run(["/bin/zsh", str(ROOT / "src/run_qyoo_train.zsh"), str(dataset)],
            env={**os.environ, "PATH": str(directory) + os.pathsep + os.environ["PATH"], "YOLO_TEST_EXIT": "7"},
            text=True, capture_output=True, timeout=5)
        self.assertEqual(failed.returncode, 7)
        self.assertEqual(len(failed.stdout.splitlines()), 1)

    def test_missing_dataset_is_rejected(self):
        result = subprocess.run(["/bin/zsh", str(ROOT / "src/run_qyoo_train.zsh")],
            text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)

if __name__ == "__main__":
    unittest.main()
