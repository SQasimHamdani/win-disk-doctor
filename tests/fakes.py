"""Made-up Windows folders for tests. Nothing here points at the real system."""
import os


def fake_env(root):
    env = {
        "TEMP": os.path.join(str(root), "Temp"),
        "SystemRoot": os.path.join(str(root), "Windows"),
        "SystemDrive": os.path.join(str(root), "Drive"),
        "LOCALAPPDATA": os.path.join(str(root), "Local"),
    }
    for path in env.values():
        os.makedirs(path, exist_ok=True)
    return env


def write(path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(b"x" * size)
