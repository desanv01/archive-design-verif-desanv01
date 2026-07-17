"""Assignment 3: count instruction definitions in each ISA extension."""

import argparse
import csv
from collections import Counter
from pathlib import Path

from opcode_parser import load_instructions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="riscv-opcodes repository root")
    parser.add_argument("--output", default=str(Path(__file__).with_name("extension_counts.csv")))
    parser.add_argument(
        "--include-imports",
        action="store_true",
        help="count $import references in addition to real and pseudo definitions",
    )
    args = parser.parse_args()

    _, records = load_instructions(args.root)
    selected = records if args.include_imports else [r for r in records if r.kind != "import"]
    counts = Counter(record.extension for record in selected)

    output = Path(args.output)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["extension", "instruction_count"])
        writer.writerows(sorted(counts.items()))

    width = max(len(name) for name in counts)
    print(f"{'Extension':<{width}}  Count")
    print(f"{'-' * width}  -----")
    for extension, count in sorted(counts.items()):
        print(f"{extension:<{width}}  {count:5d}")
    print(f"Saved {sum(counts.values())} definitions across {len(counts)} extensions to {output}")


if __name__ == "__main__":
    main()

