"""Turn scan results into text or JSON. Only %VARIABLE% paths are ever shown."""
import json
import textwrap

from .locations import SAFE

_MEASURED = ("ok", "partial")
_NOTES = {
    "denied": "no access (try an administrator terminal)",
    "missing": "not found",
    "unavailable": "location unknown (variable not set)",
    "link": "is a link, not followed",
}


def format_size(size):
    if size < 1024:
        return "{} B".format(size)
    value = float(size)
    for unit in ("KB", "MB", "GB", "TB"):
        value /= 1024
        if value < 1024 or unit == "TB":
            return "{:.1f} {}".format(value, unit)


def _size_text(result):
    if result.status not in _MEASURED:
        return _NOTES[result.status]
    if result.status == "partial":
        return "at least {} ({} item(s) unreadable)".format(
            format_size(result.size), result.unreadable
        )
    return format_size(result.size)


def _field(title, text):
    first = "    {}: ".format(title)
    return textwrap.fill(text, width=79, initial_indent=first, subsequent_indent="      ")


def render_text(results):
    ordered = sorted(
        results, key=lambda r: (r.status not in _MEASURED, -r.size)
    )
    lines = ["win-disk-doctor: read-only report. Nothing was deleted or changed.", ""]
    for result in ordered:
        location = result.location
        lines.append("{}  [{}]".format(location.name, location.label.upper()))
        lines.append("    Size: " + _size_text(result))
        path = location.template
        if location.pattern:
            path += "\\" + location.pattern
        lines.append("    Path: " + path)
        lines.append(_field("What", location.what))
        lines.append(_field("If removed", location.lose))
        lines.append("")
    safe = [r for r in results if r.location.label == SAFE]
    total = format_size(sum(r.size for r in safe if r.status in _MEASURED))
    if any(r.status not in ("ok", "missing") for r in safe):
        total = "at least " + total
    lines.append("Measured in items labelled safe: " + total)
    lines.append("Sizes are approximate. Only the places listed above are checked.")
    return "\n".join(lines)


def render_json(results):
    return json.dumps(
        {
            "locations": [
                {
                    "id": r.location.id,
                    "name": r.location.name,
                    "path": r.location.template,
                    "pattern": r.location.pattern,
                    "label": r.location.label,
                    "what": r.location.what,
                    "if_removed": r.location.lose,
                    "status": r.status,
                    "size_bytes": r.size if r.status in _MEASURED else None,
                    "files": r.files if r.status in _MEASURED else None,
                    "unreadable": r.unreadable,
                }
                for r in results
            ]
        },
        indent=2,
    )
