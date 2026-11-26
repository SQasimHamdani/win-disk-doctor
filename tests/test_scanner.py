import os
import sys

import pytest

from fakes import fake_env, write
from win_disk_doctor import scanner
from win_disk_doctor.locations import LOCATIONS, Location

windows_only = pytest.mark.skipif(sys.platform != "win32", reason="Windows behaviour")


def location(template="%TEMP%", pattern=None):
    return Location("t", "Test", template, "safe", "what", "lose", pattern)


def snapshot(root):
    found = {}
    for folder, dirs, files in os.walk(str(root)):
        for name in dirs + files:
            path = os.path.join(folder, name)
            info = os.lstat(path)
            found[path] = (info.st_size, info.st_mtime_ns)
    return found


def test_sums_nested_files(tmp_path):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "a.bin"), 10)
    write(os.path.join(env["TEMP"], "sub", "b.bin"), 25)
    result = scanner.scan_location(location(), env)
    assert (result.status, result.size, result.files, result.unreadable) == ("ok", 35, 2, 0)


def test_pattern_counts_only_matching_files_at_top_level(tmp_path):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "thumbcache_96.db"), 7)
    write(os.path.join(env["TEMP"], "iconcache_96.db"), 100)
    write(os.path.join(env["TEMP"], "sub", "thumbcache_1.db"), 100)
    result = scanner.scan_location(location(pattern="thumbcache_*.db"), env)
    assert (result.size, result.files) == (7, 1)


def test_missing_folder(tmp_path):
    env = fake_env(tmp_path)
    assert scanner.scan_location(location(r"%TEMP%\nope"), env).status == "missing"


@pytest.mark.parametrize("value", [None, "", r"relative\folder", "."])
def test_unset_empty_or_relative_variable_is_never_scanned(value, monkeypatch):
    monkeypatch.setattr(os, "scandir", lambda *a: pytest.fail("scanned a folder"))
    env = {} if value is None else {"TEMP": value}
    assert scanner.scan_location(location(), env).status == "unavailable"


def test_denied_root_is_not_reported_as_empty(tmp_path, monkeypatch):
    env = fake_env(tmp_path)

    def deny(path):
        raise PermissionError("denied")

    monkeypatch.setattr(os, "scandir", deny)
    assert scanner.scan_location(location(), env).status == "denied"


def test_denied_subfolder_makes_result_partial(tmp_path, monkeypatch):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "a.bin"), 10)
    write(os.path.join(env["TEMP"], "locked", "b.bin"), 25)
    real = os.scandir

    def deny_locked(path):
        if str(path).endswith("locked"):
            raise PermissionError("denied")
        return real(path)

    monkeypatch.setattr(os, "scandir", deny_locked)
    result = scanner.scan_location(location(), env)
    assert (result.status, result.size, result.unreadable) == ("partial", 10, 1)


def test_folder_vanishing_mid_scan_is_ignored(tmp_path, monkeypatch):
    env = fake_env(tmp_path)
    write(os.path.join(env["TEMP"], "gone", "b.bin"), 25)
    real = os.scandir

    def vanish(path):
        if str(path).endswith("gone"):
            raise FileNotFoundError("gone")
        return real(path)

    monkeypatch.setattr(os, "scandir", vanish)
    result = scanner.scan_location(location(), env)
    assert (result.status, result.size) == ("ok", 0)


@windows_only
def test_junction_inside_location_is_not_followed(tmp_path):
    import _winapi

    env = fake_env(tmp_path)
    outside = tmp_path / "outside"
    write(str(outside / "big.bin"), 500)
    _winapi.CreateJunction(str(outside), os.path.join(env["TEMP"], "link"))
    result = scanner.scan_location(location(), env)
    assert (result.status, result.size, result.files) == ("ok", 0, 0)


@windows_only
def test_location_that_is_a_junction_is_reported_as_link(tmp_path):
    import _winapi

    env = fake_env(tmp_path)
    outside = tmp_path / "outside"
    write(str(outside / "big.bin"), 500)
    _winapi.CreateJunction(str(outside), os.path.join(env["TEMP"], "link"))
    result = scanner.scan_location(location(r"%TEMP%\link"), env)
    assert (result.status, result.size) == ("link", 0)


@windows_only
def test_paths_longer_than_260_characters_are_counted(tmp_path):
    env = fake_env(tmp_path)
    deep = os.path.join(env["TEMP"], *(["d" * 50] * 6))
    assert len(deep) > 260
    folder = "\\\\?\\" + env["TEMP"]
    for _ in range(6):
        folder = os.path.join(folder, "d" * 50)
        os.mkdir(folder)
    with open(os.path.join(folder, "a.bin"), "wb") as handle:
        handle.write(b"x" * 12)
    assert scanner.scan_location(location(), env).size == 12


def test_scanning_changes_nothing(tmp_path):
    env = fake_env(tmp_path)
    for item in LOCATIONS:
        path = scanner.resolve(item.template, env)
        write(os.path.join(path, "thumbcache_1.db"), 5)
    before = snapshot(tmp_path)
    results = scanner.scan(env)
    assert [r.size for r in results] == [5] * len(LOCATIONS)
    assert snapshot(tmp_path) == before


def test_location_list_and_labels():
    labels = {item.id: item.label for item in LOCATIONS}
    assert labels == {
        "user-temp": "check first",
        "windows-temp": "check first",
        "recycle-bin": "check first",
        "windows-update": "check first",
        "thumbnail-cache": "safe",
        "pip-cache": "safe",
        "npm-cache": "safe",
        "windows-installer": "leave alone",
    }
