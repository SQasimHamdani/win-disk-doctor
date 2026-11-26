import json
import os

import pytest

from fakes import fake_env, write
from win_disk_doctor import __version__
from win_disk_doctor.cli import main
from win_disk_doctor.locations import LOCATIONS
from win_disk_doctor.report import format_size, render_text
from win_disk_doctor.scanner import Result


def result(index, status, size=0):
    return Result(LOCATIONS[index], status, size, 1 if size else 0, 0)


@pytest.mark.parametrize(
    "size, text",
    [
        (0, "0 B"),
        (1023, "1023 B"),
        (1024, "1.0 KB"),
        (1536 * 1024, "1.5 MB"),
        (3 * 1024 ** 3, "3.0 GB"),
    ],
)
def test_format_size(size, text):
    assert format_size(size) == text


def test_largest_first_and_partial_is_a_minimum():
    text = render_text([result(0, "ok", 10), result(1, "partial", 2048)])
    assert text.index("Windows temporary files") < text.index("Your temporary files")
    assert "at least 2.0 KB" in text


@pytest.mark.parametrize(
    "status, words",
    [
        ("denied", "no access"),
        ("missing", "not found"),
        ("unavailable", "location unknown"),
        ("link", "is a link"),
    ],
)
def test_unmeasured_locations_show_no_size(status, words):
    block = render_text([result(0, status)]).split("Measured in")[0]
    assert words in block
    assert "0 B" not in block


def test_safe_total_excludes_other_labels():
    # index 4 is the thumbnail cache (safe), index 0 is user temp (check first)
    text = render_text([result(0, "ok", 5000), result(4, "ok", 100)])
    assert "Measured in items labelled safe: 100 B" in text


@pytest.mark.parametrize("status", ["partial", "denied", "unavailable", "link"])
def test_safe_total_is_a_minimum_when_a_safe_item_is_not_fully_measured(status):
    text = render_text([result(4, status)])
    assert "Measured in items labelled safe: at least 0 B" in text


def test_output_never_contains_real_paths(tmp_path, capsys):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "secret-name.bin"), 10)
    for arguments in ([], ["--json"]):
        assert main(arguments, env=env) == 0
        output = capsys.readouterr().out
        assert "%TEMP%" in output
        assert tmp_path.name not in output
        assert "secret-name" not in output
        output.encode("ascii")


def test_json_fields(tmp_path, capsys):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "a.bin"), 10)
    main(["--json"], env=env)
    first = json.loads(capsys.readouterr().out)["locations"][0]
    assert first["id"] == "user-temp"
    assert (first["status"], first["size_bytes"], first["label"]) == ("ok", 10, "check first")


def test_json_size_is_null_when_not_measured(capsys):
    main(["--json"], env={})
    items = json.loads(capsys.readouterr().out)["locations"]
    assert {item["size_bytes"] for item in items} == {None}


def test_version(capsys):
    with pytest.raises(SystemExit) as stop:
        main(["--version"], env={})
    assert stop.value.code == 0
    assert __version__ in capsys.readouterr().out
