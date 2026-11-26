"""Measure locations. This module only lists folders and reads file metadata."""
import fnmatch
import ntpath
import os
import re
import stat
from typing import List, Mapping, NamedTuple, Optional

from .locations import LOCATIONS, Location

_REPARSE_POINT = 0x400


class Result(NamedTuple):
    location: Location
    status: str  # ok, partial, denied, missing, unavailable or link
    size: int = 0
    files: int = 0
    unreadable: int = 0


def resolve(template: str, env: Mapping[str, str]) -> Optional[str]:
    """Expand a leading %VAR%. Return None unless the variable gives an absolute path."""
    match = re.match(r"%(\w+)%\\?(.*)$", template)
    if not match:
        return None
    base = env.get(match.group(1), "")
    if re.match(r"^[A-Za-z]:$", base):
        base += os.sep
    if not os.path.isabs(base):
        return None
    parts = [part for part in match.group(2).split("\\") if part]
    return os.path.join(base, *parts)


def _long_path(path: str) -> str:
    """Allow paths over 260 characters on Windows."""
    if os.name != "nt" or path.startswith("\\\\"):
        return path
    return "\\\\?\\" + ntpath.abspath(path)


def _is_link(info: os.stat_result) -> bool:
    """True for symlinks and, on Windows, junctions and other reparse points."""
    attributes = getattr(info, "st_file_attributes", 0)
    return stat.S_ISLNK(info.st_mode) or bool(attributes & _REPARSE_POINT)


def scan_location(location: Location, env: Mapping[str, str]) -> Result:
    path = resolve(location.template, env)
    if path is None:
        return Result(location, "unavailable")
    root = _long_path(path)
    try:
        if _is_link(os.lstat(root)):
            return Result(location, "link")
    except FileNotFoundError:
        return Result(location, "missing")
    except OSError:
        return Result(location, "denied")

    size = files = unreadable = 0
    pending = [root]
    while pending:
        folder = pending.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        continue
                    except OSError:
                        unreadable += 1
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        if not location.pattern and not _is_link(info):
                            pending.append(entry.path)
                    elif stat.S_ISREG(info.st_mode):
                        if location.pattern and not fnmatch.fnmatch(entry.name, location.pattern):
                            continue
                        size += info.st_size
                        files += 1
        except FileNotFoundError:
            continue
        except OSError:
            if folder == root:
                return Result(location, "denied")
            unreadable += 1
    return Result(location, "partial" if unreadable else "ok", size, files, unreadable)


def scan(env: Mapping[str, str], locations=LOCATIONS) -> List[Result]:
    return [scan_location(location, env) for location in locations]
