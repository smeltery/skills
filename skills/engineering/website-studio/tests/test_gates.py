"""Exercise recovery and refusal behavior through the public CLI."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gates.py"
spec = importlib.util.spec_from_file_location("gates", SCRIPT)
gates = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gates)


class GateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.run_cli("init")
        self.source = self.root / "index.html"
        self.source.write_text("<h1>Studio</h1>")

    def run_cli(self, command, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, "--root", str(self.root), *args],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def report(self, gate):
        evidence = self.root / ".website-studio" / f"{gate}.md"
        evidence.write_text(f"Fixture evidence for {gate}; not a real website audit.")
        data = {
            "gate": gate,
            "checks": {
                check: {
                    "result": "pass", "note": "Test fixture receipt",
                    "evidence": [str(evidence.relative_to(self.root))],
                }
                for check in gates.CHECKS[gate]
            },
            "issues": [],
        }
        path = self.root / ".website-studio" / f"{gate}.json"
        path.write_text(json.dumps(data))
        return path

    def advance_through(self, last):
        for gate in gates.GATES:
            self.run_cli("pass", "--report", str(self.report(gate)))
            if gate == last:
                break

    def test_empty_project_init_is_idempotent(self):
        self.advance_through("context")
        before = (self.root / ".website-studio/state.json").read_bytes()
        self.run_cli("init")
        self.assertEqual(before, (self.root / ".website-studio/state.json").read_bytes())

    def test_gate_cannot_be_skipped(self):
        result = self.run_cli("pass", "--report", str(self.report("delivery")), success=False)
        self.assertIn("Next gate is context", result.stderr)

    def test_incomplete_or_failed_reports_do_not_advance(self):
        path = self.report("context")
        original = json.loads(path.read_text())
        for mutation in ["missing", "failed", "issues", "empty-evidence", "missing-file"]:
            with self.subTest(mutation=mutation):
                data = json.loads(json.dumps(original))
                if mutation == "missing":
                    del data["checks"]["brief"]
                elif mutation == "failed":
                    data["checks"]["brief"]["result"] = "fail"
                elif mutation == "issues":
                    data["issues"] = ["Broken primary CTA"]
                elif mutation == "empty-evidence":
                    data["checks"]["brief"]["evidence"] = []
                else:
                    data["checks"]["brief"]["evidence"] = ["missing.png"]
                path.write_text(json.dumps(data))
                self.run_cli("pass", "--report", str(path), success=False)
                self.assertEqual(json.loads(self.run_cli("status").stdout)["next"], "context")

    def test_evidence_must_stay_inside_target_even_through_symlinks(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "private.txt"
            external.write_text("outside evidence")
            link = self.root / ".website-studio" / "external.txt"
            link.symlink_to(external)
            path = self.report("context")
            data = json.loads(path.read_text())
            data["checks"]["brief"]["evidence"] = [str(link.relative_to(self.root))]
            path.write_text(json.dumps(data))
            self.run_cli("pass", "--report", str(path), success=False)

    def test_modified_and_deleted_evidence_invalidate_earliest_gate(self):
        self.advance_through("structure")
        evidence = self.root / ".website-studio/references.md"
        evidence.write_text("Changed observations")
        result = self.run_cli("status", success=False)
        self.assertEqual(json.loads(result.stdout)["next"], "references")
        evidence.unlink()
        self.run_cli("status", success=False)
        self.run_cli("pass", "--report", str(self.report("build")), success=False)

    def test_source_edit_returns_to_build_and_repair_clears_successors(self):
        self.advance_through("responsive")
        self.source.write_text("<h1>Revised studio</h1>")
        result = self.run_cli("status", success=False)
        self.assertEqual(json.loads(result.stdout)["next"], "build")
        self.run_cli("pass", "--report", str(self.report("build")))
        state = json.loads((self.root / ".website-studio/state.json").read_text())
        self.assertNotIn("journeys", state["receipts"])
        self.assertEqual(json.loads(self.run_cli("status").stdout)["next"], "journeys")

    def test_new_untracked_asset_invalidates_runtime_evidence(self):
        self.advance_through("build")
        (self.root / "logo.svg").write_text("<svg/>")
        self.run_cli("status", success=False)

    def test_explicit_invalidation_retains_prior_gates(self):
        self.advance_through("build")
        self.run_cli("invalidate", "--gate", "direction", "--reason", "Changed brand")
        self.assertEqual(json.loads(self.run_cli("status").stdout)["next"], "direction")
        self.assertTrue((self.root / ".website-studio/build.md").exists())

    def test_full_run_and_repeated_receipt(self):
        self.advance_through("delivery")
        self.assertIsNone(json.loads(self.run_cli("status").stdout)["next"])
        self.run_cli("pass", "--report", ".website-studio/delivery.json")
        (self.root / ".website-studio/new-capture.png").write_bytes(b"fixture")
        self.assertIsNone(json.loads(self.run_cli("status").stdout)["next"])

    def test_modified_report_and_corrupt_state_fail_closed(self):
        self.advance_through("context")
        path = self.root / ".website-studio/context.json"
        path.write_text(path.read_text() + "\n")
        self.run_cli("status", success=False)
        (self.root / ".website-studio/state.json").write_text("{broken")
        self.run_cli("init", success=False)

    def test_invalid_state_shape_reports_an_explicit_error(self):
        path = self.root / ".website-studio/state.json"
        for data in [[], {"version": 1, "root": str(self.root), "receipts": {"context": None}}]:
            with self.subTest(data=data):
                path.write_text(json.dumps(data))
                result = self.run_cli("status", success=False)
                self.assertIn("Gate error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
