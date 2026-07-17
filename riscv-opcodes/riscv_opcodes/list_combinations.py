"""Assignment 4: group unique opcode/funct3/funct7 combinations by extension."""

import argparse
from collections import defaultdict
import json
from pathlib import Path

from opcode_parser import format_field, load_instructions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="riscv-opcodes repository root")
    parser.add_argument("--output", default=str(Path(__file__).with_name("combinations.json")))
    args = parser.parse_args()

    _, records = load_instructions(args.root)
    grouped = defaultdict(lambda: defaultdict(set))
    for record in records:
        if record.kind == "import" or record.opcode is None:
            continue
        key = (record.opcode, record.funct3, record.funct7)
        grouped[record.extension][key].add(record.mnemonic)

    payload = {}
    for extension in sorted(grouped):
        combinations = []
        for (opcode, funct3, funct7), mnemonics in sorted(
            grouped[extension].items(),
            key=lambda item: tuple(-1 if value is None else value for value in item[0]),
        ):
            combinations.append(
                {
                    "opcode": format_field(opcode, 7),
                    "funct3": format_field(funct3, 3),
                    "funct7": format_field(funct7, 7),
                    "mnemonics": sorted(mnemonics),
                }
            )
        payload[extension] = combinations

    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    total = sum(len(items) for items in payload.values())
    print(f"Saved {total} unique combinations across {len(payload)} extensions to {output}")


if __name__ == "__main__":
    main()

