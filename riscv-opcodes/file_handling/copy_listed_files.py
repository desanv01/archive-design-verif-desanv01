"""Problem 2: find named files and copy each into an output/stem folder."""

import argparse
from pathlib import Path
import shutil

from fs_utils import ensure_distinct, is_within


def requested_names(arguments: list[str], list_file: str | None) -> list[str]:
    names = list(arguments)
    if list_file:
        names.extend(
            line.strip()
            for line in Path(list_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return list(dict.fromkeys(names))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("output")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--list-file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    ensure_distinct(root, output)
    names = requested_names(args.files, args.list_file)
    if not names:
        parser.error("provide file names or --list-file")

    copied = 0
    for name in names:
        matches = sorted(
            path
            for path in root.rglob(name)
            if path.is_file() and not is_within(path, output)
        )
        if not matches:
            print(f"WARNING: {name} was not found under {root}")
            continue
        if len(matches) > 1:
            print(f"WARNING: {name} has {len(matches)} matches; using {matches[0]}")

        source = matches[0]
        destination = output / source.stem / source.name
        if args.dry_run:
            print(f"DRY-RUN: {source} -> {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"COPIED: {source} -> {destination}")
        copied += 1

    print(f"Requested={len(names)}, copied={copied}, missing={len(names) - copied}")


if __name__ == "__main__":
    main()

