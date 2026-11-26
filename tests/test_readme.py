"""Commands shown in the README must work when copied."""
import os
import re

import pytest

from win_disk_doctor.cli import main

README = os.path.join(os.path.dirname(__file__), os.pardir, "README.md")
PREFIXES = ("python -m win_disk_doctor", "win-disk-doctor")


def readme_commands():
    with open(README, encoding="utf-8") as handle:
        blocks = re.findall(r"```bat\n(.*?)```", handle.read(), re.DOTALL)
    lines = [line.strip() for block in blocks for line in block.splitlines()]
    return [line for line in lines if line.startswith(PREFIXES)]


def test_readme_shows_commands():
    assert len(readme_commands()) >= 3


@pytest.mark.parametrize("command", readme_commands())
def test_readme_command_is_accepted(command):
    prefix = next(p for p in PREFIXES if command.startswith(p))
    assert main(command[len(prefix):].split(), env={}) == 0
