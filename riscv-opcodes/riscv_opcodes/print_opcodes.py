"""Assignment 1: print and save all unique RISC-V instruction mnemonics."""

import argparse
from pathlib import Path

from opcode_parser import load_instructions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="riscv-opcodes repository root")
    parser.add_argument("--output", default=str(Path(__file__).with_name("all_opcodes.txt")))
    args = parser.parse_args()

    _, records = load_instructions(args.root)
    mnemonics = sorted({record.mnemonic for record in records}, key=str.lower)
    output = Path(args.output)
    output.write_text("\n".join(mnemonics) + "\n", encoding="utf-8")

    for mnemonic in mnemonics:
        print(mnemonic)
    print(f"\nSaved {len(mnemonics)} unique mnemonics to {output}")


if __name__ == "__main__":
    main()

