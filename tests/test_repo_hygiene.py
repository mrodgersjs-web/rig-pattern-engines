"""Repo hygiene checks: the files a production repo must have, checked on disk.

These assert the polish-wave rules directly from the tracked files, so a future
edit that drops a badge, a timeout, or the code owner fails the test suite.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_NAME = "rig-pattern-engines"


def _workflow_files() -> list[Path]:
    return sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))


def test_codeowners_assigns_repo_owner_everywhere() -> None:
    text = (REPO_ROOT / ".github" / "CODEOWNERS").read_text()
    rules = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    assert rules, "CODEOWNERS must have at least one rule"
    assert rules[0].split() == ["*", "@mrodgersjs-web"]


def test_copilot_instructions_size_and_commands() -> None:
    path = REPO_ROOT / ".github" / "copilot-instructions.md"
    text = path.read_text()
    assert len(text.encode()) <= 8000
    assert 500 <= len(text.encode()) <= 8000
    assert "pytest" in text
    assert "ruff check" in text
    assert "conventional" in text.lower()
    assert "truth rule" in text.lower()


def test_readme_badges_footer_and_clone_target() -> None:
    text = (REPO_ROOT / "README.md").read_text()
    assert "github/actions/workflow/status" in text
    assert "rodgersintelligence.com" in text
    assert any(word in text for word in ("pytest", "smoke", "npm test", "node --test"))
    clones = re.findall(r"git clone\s+(\S+)", text)
    assert clones, "README must show a clone command"
    for target in clones:
        assert f"mrodgersjs-web/{REPO_NAME}" in target


def test_workflows_have_timeouts_and_no_continue_on_error() -> None:
    files = _workflow_files()
    assert files, "at least one workflow must exist"
    for path in files:
        doc = yaml.safe_load(path.read_text())
        for job_name, job in (doc.get("jobs") or {}).items():
            assert "timeout-minutes" in job, f"{path.name}:{job_name} has no timeout-minutes"
            assert "continue-on-error" not in job, f"{path.name}:{job_name} sets continue-on-error"


def test_test_job_runs_on_push() -> None:
    doc = yaml.safe_load((REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text())
    on = doc.get("on") or doc.get(True) or {}
    assert "push" in on and "pull_request" in on
    test_job = doc["jobs"]["test"]
    runs = "\n".join(step.get("run", "") for step in test_job["steps"])
    assert "pytest" in runs
