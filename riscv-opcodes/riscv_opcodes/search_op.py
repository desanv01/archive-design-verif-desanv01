"""Assignment 2: search instruction mnemonics and write structured JSON."""

import argparse
import json
from pathlib import Path
import re

from opcode_parser import load_instructions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="literal mnemonic or regular expression")
    parser.add_argument("--root", default=".", help="riscv-opcodes repository root")
    parser.add_argument("--output", default=str(Path(__file__).with_name("search.json")))
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-r", "--regex", action="store_true")
    args = parser.parse_args()

    root, records = load_instructions(args.root)
    flags = re.IGNORECASE if args.ignore_case else 0
    expression = args.query if args.regex else re.escape(args.query)
    pattern = re.compile(expression, flags)

    results = [
        record.to_dict(root)
        for record in records
        if (pattern.search(record.mnemonic) if args.regex else pattern.fullmatch(record.mnemonic))
    ]
    payload = {
        "query": args.query,
        "regex": args.regex,
        "case_insensitive": args.ignore_case,
        "match_count": len(results),
        "results": results,
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for result in results:
        print(
            f"{result['filename']}:{result['line_number']}: "
            f"{result['mnemonic']} [{result['kind']}]"
        )
    print(f"Saved {len(results)} match(es) to {output}")


if __name__ == "__main__":
    main()

