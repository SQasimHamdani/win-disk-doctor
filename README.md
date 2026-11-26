# win-disk-doctor: what is using your Windows disk space, and what is safe to clean

[![CI](https://github.com/SQasimHamdani/win-disk-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/SQasimHamdani/win-disk-doctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

**win-disk-doctor checks well-known Windows cleanup locations, such as temp files, the Windows
Update download folder and package caches, and explains each one in plain language:** how big it
is, whether it is safe to clean, and what you lose if you do. It is **read-only**. It never
deletes or changes anything.

## Vision

When a Windows drive fills up, disk usage maps show which folders are large but not whether
removing them will break something. win-disk-doctor is for people who want that second answer
before they touch anything.

Good looks like: every item has a size, a clear label and an honest note about the consequences,
and anything that could not be measured says so instead of showing zero.

What it will **not** do: delete files by default, touch browser profiles, credential stores or your
documents, or promise that cleaning will make your PC faster.

## Quick start

```bat
git clone https://github.com/SQasimHamdani/win-disk-doctor.git
cd win-disk-doctor
pip install .
win-disk-doctor
```

Example output (made-up sample data, shortened):

```text
win-disk-doctor: read-only report. Nothing was deleted or changed.

Your temporary files  [CHECK FIRST]
    Size: 48.0 MB
    Path: %TEMP%
    What: Working files created by programs and installers.
    If removed: Usually nothing, but files opened from email or zip archives
      and then edited may exist only here.

pip download cache  [SAFE]
    Size: 22.0 MB
    Path: %LOCALAPPDATA%\pip\Cache
    What: Python packages kept to avoid downloading them again.
    If removed: Later installs download again. 'pip cache purge' clears it.

Windows Installer cache  [LEAVE ALONE]
    Size: 17.0 MB
    Path: %SystemRoot%\Installer
    What: Installer files Windows keeps for installed programs.
    If removed: Repairing, updating or uninstalling programs can fail. Do not
      delete by hand.
```

## What it checks

| Location | Path | Label |
|---|---|---|
| Your temporary files | `%TEMP%` | check first |
| Windows temporary files | `%SystemRoot%\Temp` | check first |
| Recycle Bin (system drive only) | `%SystemDrive%\$Recycle.Bin` | check first |
| Windows Update downloads | `%SystemRoot%\SoftwareDistribution\Download` | check first |
| Thumbnail cache | `%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db` | safe |
| pip download cache | `%LOCALAPPDATA%\pip\Cache` | safe |
| npm download cache | `%LOCALAPPDATA%\npm-cache` | safe |
| Windows Installer cache | `%SystemRoot%\Installer` | leave alone |

## Usage

Plain-language report, largest first:

```bat
win-disk-doctor
```

The same data for scripts:

```bat
win-disk-doctor --json
```

If the command is not on your PATH:

```bat
python -m win_disk_doctor
```

Some locations need an administrator terminal to be read. Without it they are reported as
*no access*, or as *at least* a given size when only part could be read.

There is nothing to configure.

## How it works and privacy

It lists the folders above and adds up file sizes. It does not open file contents, follow links or
junctions, or make network requests. Output shows paths such as `%TEMP%` rather than your real
folders, and never lists file names, so a report can be shared.

Limits:
- Sizes are logical file sizes. Compressed, sparse and hard-linked files can make the space
  actually freed differ.
- Only default locations are checked. A moved pip or npm cache is not detected.
- Only the system drive's Recycle Bin is checked.
- Labels are general guidance, not a guarantee. You are responsible for what you delete.

## Roadmap

- Detect custom pip and npm cache locations.
- More locations, each with an explanation and a label.
- Optional cleanup with a dry run first. This needs a real way to undo (a log alone cannot
  restore a deleted file), so it will not be added until that is designed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

[MIT](LICENSE). No third-party runtime dependencies.
