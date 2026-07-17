"""Assignment 5: count definitions sharing each seven-bit base opcode."""

import argparse
from collections import defaultdict
from pathlib import Path

from opcode_parser import load_instructions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="riscv-opcodes repository root")
    parser.add_argument("--output", default=str(Path(__file__).with_name("opcode_frequencies.txt")))
    args = parser.parse_args()

    _, records = load_instructions(args.root)
    by_opcode = defaultdict(list)
    for record in records:
        if record.kind != "import" and record.opcode is not None:
            by_opcode[record.opcode].append(record)

    lines = []
    for opcode in sorted(by_opcode):
        records_for_opcode = by_opcode[opcode]
        mnemonics = sorted({record.mnemonic for record in records_for_opcode})
        lines.append(
            f"0b{opcode:07b} (0x{opcode:02X}) | definitions={len(records_for_opcode):4d} | "
            f"mnemonics={', '.join(mnemonics)}"
        )

    output = Path(args.output)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSaved {len(by_opcode)} opcode groups to {output}")


if __name__ == "__main__":
    main()

