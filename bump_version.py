import re
import os

VERSION_FILE = "version.py"

def bump_version():
    if not os.path.exists(VERSION_FILE):
        print(f"Error: {VERSION_FILE} not found.")
        return

    with open(VERSION_FILE, "r") as f:
        content = f.read()

    # Find version string
    match = re.search(r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("Error: Could not find version string.")
        return

    major, minor, patch = map(int, match.groups())
    new_patch = patch + 1
    new_version = f"{major}.{minor}.{new_patch}"

    new_content = re.sub(
        r'__version__\s*=\s*".*"',
        f'__version__ = "{new_version}"',
        content
    )

    with open(VERSION_FILE, "w") as f:
        f.write(new_content)

    print(f"Version bumped: {major}.{minor}.{patch} -> {new_version}")

if __name__ == "__main__":
    bump_version()
