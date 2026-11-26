"""The fixed list of places that are checked, and what is known about each."""
from typing import NamedTuple, Optional

SAFE = "safe"
CHECK_FIRST = "check first"
LEAVE_ALONE = "leave alone"


class Location(NamedTuple):
    id: str
    name: str
    template: str
    label: str
    what: str
    lose: str
    pattern: Optional[str] = None  # if set, only matching files directly in the folder


LOCATIONS = (
    Location(
        "user-temp", "Your temporary files", r"%TEMP%", CHECK_FIRST,
        "Working files created by programs and installers.",
        "Usually nothing, but files opened from email or zip archives and then edited "
        "may exist only here.",
    ),
    Location(
        "windows-temp", "Windows temporary files", r"%SystemRoot%\Temp", CHECK_FIRST,
        "Working files created by Windows and services.",
        "Usually nothing. Leave files in use; a pending install may need some.",
    ),
    Location(
        "recycle-bin", "Recycle Bin (system drive)", r"%SystemDrive%\$Recycle.Bin", CHECK_FIRST,
        "Files you or other accounts deleted but have not removed permanently.",
        "The chance to restore them. Look through it before emptying.",
    ),
    Location(
        "windows-update", "Windows Update downloads",
        r"%SystemRoot%\SoftwareDistribution\Download", CHECK_FIRST,
        "Update packages downloaded by Windows Update.",
        "Windows downloads them again if needed. Do not remove while updates are pending.",
    ),
    Location(
        "thumbnail-cache", "Thumbnail cache",
        r"%LOCALAPPDATA%\Microsoft\Windows\Explorer", SAFE,
        "Small preview images that File Explorer has generated.",
        "Nothing lasting. Previews are rebuilt, so folders may open slowly once.",
        "thumbcache_*.db",
    ),
    Location(
        "pip-cache", "pip download cache", r"%LOCALAPPDATA%\pip\Cache", SAFE,
        "Python packages kept to avoid downloading them again.",
        "Later installs download again. 'pip cache purge' clears it.",
    ),
    Location(
        "npm-cache", "npm download cache", r"%LOCALAPPDATA%\npm-cache", SAFE,
        "Node.js packages kept to avoid downloading them again.",
        "Later installs download again. 'npm cache clean --force' clears it.",
    ),
    Location(
        "windows-installer", "Windows Installer cache", r"%SystemRoot%\Installer", LEAVE_ALONE,
        "Installer files Windows keeps for installed programs.",
        "Repairing, updating or uninstalling programs can fail. Do not delete by hand.",
    ),
)
