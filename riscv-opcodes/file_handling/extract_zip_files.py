"""Problem 1: recursively find and safely extract ZIP archives in place."""

import argparse
from pathlib import Path
import zipfile

from fs_utils import is_within


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    for member in archive.infolist():
        target = destination / member.filename
        if not is_within(target, destination):
            raise ValueError(f"unsafe archive member: {member.filename}")
    archive.extractall(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    archives = sorted(path for path in root.rglob("*.zip") if path.is_file())
    extracted = 0
    skipped = 0

    for path in archives:
        try:
            if args.dry_run:
                print(f"DRY-RUN: extract {path} into {path.parent}")
            else:
                with zipfile.ZipFile(path) as archive:
                    safe_extract(archive, path.parent)
                print(f"EXTRACTED: {path}")
            extracted += 1
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            print(f"WARNING: skipped {path}: {exc}")
            skipped += 1

    print(f"Archives found={len(archives)}, extracted={extracted}, skipped={skipped}")


if __name__ == "__main__":
    main()

