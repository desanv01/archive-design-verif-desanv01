"""Problem 5: copy co-directories with dut/, excluding ref and renaming ELF files."""

import argparse
from pathlib import Path
import shutil

from fs_utils import ensure_distinct, is_within


def rename_elf_files(dut: Path, directory_name: str) -> int:
    elf_files = sorted(path for path in dut.rglob("*.elf") if path.is_file())
    for index, elf_file in enumerate(elf_files, start=1):
        suffix = "" if index == 1 else f"_{index}"
        target = elf_file.with_name(f"{directory_name}{suffix}.elf")
        if target != elf_file:
            if target.exists():
                target.unlink()
            elf_file.rename(target)
    return len(elf_files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent")
    parser.add_argument("destination")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    parent = Path(args.parent).expanduser().resolve()
    destination = Path(args.destination).expanduser().resolve()
    ensure_distinct(parent, destination)

    co_directories = sorted(
        directory
        for directory in parent.rglob("*")
        if directory.is_dir()
        and (directory / "dut").is_dir()
        and not is_within(directory, destination)
    )

    copied = 0
    renamed = 0
    for source in co_directories:
        target = destination / source.relative_to(parent)
        if args.dry_run:
            count = len(list((source / "dut").rglob("*.elf")))
            print(f"DRY-RUN: {source} -> {target}; rename {count} ELF file(s)")
            copied += 1
            renamed += count
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("ref"),
        )
        count = rename_elf_files(target / "dut", source.name)
        print(f"COPIED: {source} -> {target}; renamed {count} ELF file(s)")
        copied += 1
        renamed += count

    print(f"Co-directories copied={copied}, ELF files renamed={renamed}")


if __name__ == "__main__":
    main()

