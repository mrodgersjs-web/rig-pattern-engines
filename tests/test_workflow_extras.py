"""Every `pip install -e ".[extra]"` in a workflow must name an extra that pyproject.toml defines.

The smoke workflow installed `.[test]` after the extra was renamed to `dev`, so pip
installed no test tools and CI failed with "No module named pytest".
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _extras_defined():
    text = (ROOT / "pyproject.toml").read_text()
    block = text.split("[project.optional-dependencies]", 1)[1].split("\n[", 1)[0]
    return set(re.findall(r"^(\w[\w-]*)\s*=", block, re.M))


def test_workflow_install_extras_exist():
    defined = _extras_defined()
    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        for extra in re.findall(r'pip install -e "\.\[([\w,-]+)\]"', wf.read_text()):
            for name in extra.split(","):
                assert name in defined, f"{wf.name} installs undefined extra [{name}]"
