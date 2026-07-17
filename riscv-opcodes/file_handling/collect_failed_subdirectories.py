"""Problem 3: collect directories containing a STATUS_FAILED marker."""

import argparse
from pathlib import Path
import shutil

from fs_utils import is_within


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--destination")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    destination = (
        Path(args.destination).expanduser().resolve()
        if args.destination
        else root / "failed_subdirectories"
    )

    candidates = sorted(
        marker.parent
        for marker in root.rglob("STATUS_FAILED")
        if marker.is_file() and not is_within(marker, destination)
    )
    # If a failed parent contains another failed directory, copying the parent
    # already preserves the child. Keep only top-level failed candidates.
    selected = [
        candidate
        for candidate in candidates
        if not any(parent in candidate.parents for parent in candidates)
    ]

    for source in selected:
        relative = source.relative_to(root)
        target = destination / relative
        if args.dry_run:
            print(f"DRY-RUN: {source} -> {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, dirs_exist_ok=True)
            print(f"COLLECTED: {source} -> {target}")

    print(f"Failed directories found={len(candidates)}, copied={len(selected)}")


if __name__ == "__main__":
    main()

