"""Problem 4: copy directories whose names start with a chosen prefix."""

import argparse
from pathlib import Path
import shutil

from fs_utils import ensure_distinct, is_within


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("destination")
    parser.add_argument("--prefix", default="test_v")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    destination = Path(args.destination).expanduser().resolve()
    ensure_distinct(root, destination)
    matches = sorted(
        path
        for path in root.rglob(f"{args.prefix}*")
        if path.is_dir() and not is_within(path, destination)
    )

    for source in matches:
        target = destination / source.relative_to(root)
        if args.dry_run:
            print(f"DRY-RUN: {source} -> {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, dirs_exist_ok=True)
            print(f"COPIED: {source} -> {target}")

    print(f"Matching directories copied={len(matches)}")


if __name__ == "__main__":
    main()

