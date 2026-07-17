"""Shared parsing utilities for the RISC-V opcode assignments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable


ASSIGNMENT_RE = re.compile(
    r"(?<!\S)(?P<msb>\d+)(?:\.\.(?P<lsb>\d+))?="
    r"(?P<value>0[xX][0-9a-fA-F]+|0[bB][01]+|\d+)(?!\S)"
)
MNEMONIC_KEYS = ("mnemonic", "name", "instruction", "instr")
FIELD_KEYS = {"opcode", "funct3", "funct7", "encoding", "match", "mask"}


@dataclass(frozen=True)
class InstructionRecord:
    mnemonic: str
    extension: str
    source: Path
    line_number: int
    text: str
    kind: str
    opcode: int | None
    funct3: int | None
    funct7: int | None

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        source = self.source
        if root is not None:
            try:
                source = source.relative_to(root)
            except ValueError:
                pass
        return {
            "mnemonic": self.mnemonic,
            "extension": self.extension,
            "kind": self.kind,
            "filename": source.as_posix(),
            "line_number": self.line_number,
            "matched_text": self.text,
            "opcode": self.opcode,
            "funct3": self.funct3,
            "funct7": self.funct7,
        }


def find_repository_root(start: str | Path) -> Path:
    """Find a directory containing current extensions or legacy YAML opcodes."""
    start_path = Path(start).expanduser().resolve()
    candidates = (start_path, *start_path.parents)
    for candidate in candidates:
        if (candidate / "extensions").is_dir() or (candidate / "opcodes").is_dir():
            return candidate
    raise FileNotFoundError(
        f"Could not find an 'extensions' or 'opcodes' directory from {start_path}"
    )


def _fixed_bits(text: str) -> dict[int, int]:
    bits: dict[int, int] = {}
    for match in ASSIGNMENT_RE.finditer(text):
        msb = int(match.group("msb"))
        lsb = int(match.group("lsb") or msb)
        value = int(match.group("value"), 0)
        if msb < lsb:
            msb, lsb = lsb, msb
        width = msb - lsb + 1
        if value >= (1 << width):
            continue
        for offset, bit_position in enumerate(range(lsb, msb + 1)):
            bits[bit_position] = (value >> offset) & 1
    return bits


def _field(bits: dict[int, int], msb: int, lsb: int) -> int | None:
    if any(position not in bits for position in range(lsb, msb + 1)):
        return None
    value = 0
    for position in range(lsb, msb + 1):
        value |= bits[position] << (position - lsb)
    return value


def parse_extension_file(path: Path, root: Path) -> list[InstructionRecord]:
    """Parse one current-format extensions/rv* opcode file."""
    records: list[InstructionRecord] = []
    relative = path.relative_to(root / "extensions")
    extension = relative.as_posix()

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        text = raw_line.strip()
        if not text or text.startswith("#"):
            continue

        tokens = text.split()
        if tokens[0] == "$import" and len(tokens) >= 2:
            mnemonic = tokens[1].split("::")[-1]
            kind = "import"
            encoding_text = ""
        elif tokens[0] == "$pseudo_op" and len(tokens) >= 3:
            mnemonic = tokens[2]
            kind = "pseudo_op"
            encoding_text = " ".join(tokens[3:])
        elif tokens[0].startswith("$"):
            continue
        else:
            mnemonic = tokens[0]
            kind = "regular"
            encoding_text = " ".join(tokens[1:])

        bits = _fixed_bits(encoding_text)
        records.append(
            InstructionRecord(
                mnemonic=mnemonic,
                extension=extension,
                source=path,
                line_number=line_number,
                text=text,
                kind=kind,
                opcode=_field(bits, 6, 0),
                funct3=_field(bits, 14, 12),
                funct7=_field(bits, 31, 25),
            )
        )
    return records


def _yaml_line_number(lines: list[str], mnemonic: str) -> int:
    pattern = re.compile(rf"\b{re.escape(mnemonic)}\b", re.IGNORECASE)
    for number, line in enumerate(lines, start=1):
        if pattern.search(line):
            return number
    return 0


def _integer_field(value: Any, width: int) -> int | None:
    if value is None:
        return None
    try:
        result = int(str(value), 0)
    except (TypeError, ValueError):
        return None
    return result if 0 <= result < (1 << width) else None


def _walk_yaml(node: Any, inherited_name: str | None = None) -> Iterable[tuple[str, dict]]:
    if isinstance(node, list):
        for item in node:
            yield from _walk_yaml(item)
        return
    if not isinstance(node, dict):
        return

    explicit_name = next((node[key] for key in MNEMONIC_KEYS if key in node), None)
    has_fields = bool(FIELD_KEYS.intersection(node))
    name = str(explicit_name or inherited_name) if (explicit_name or inherited_name) else None
    if name and (has_fields or explicit_name):
        yield name, node
        return

    for key, value in node.items():
        if isinstance(value, (dict, list)):
            child_name = str(key) if isinstance(value, dict) and FIELD_KEYS.intersection(value) else None
            yield from _walk_yaml(value, child_name)


def parse_yaml_file(path: Path, root: Path) -> list[InstructionRecord]:
    """Parse common legacy YAML opcode layouts used by older assignments."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Legacy YAML input requires: python3 -m pip install PyYAML") from exc

    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    lines = raw.splitlines()
    extension = path.relative_to(root / "opcodes").with_suffix("").as_posix()
    records = []
    for mnemonic, fields in _walk_yaml(data):
        opcode = _integer_field(fields.get("opcode"), 7)
        funct3 = _integer_field(fields.get("funct3"), 3)
        funct7 = _integer_field(fields.get("funct7"), 7)
        line_number = _yaml_line_number(lines, mnemonic)
        text = lines[line_number - 1].strip() if line_number else mnemonic
        records.append(
            InstructionRecord(
                mnemonic=mnemonic,
                extension=extension,
                source=path,
                line_number=line_number,
                text=text,
                kind="yaml",
                opcode=opcode,
                funct3=funct3,
                funct7=funct7,
            )
        )
    return records


def load_instructions(root: str | Path) -> tuple[Path, list[InstructionRecord]]:
    """Load all current extension files and any legacy YAML opcode files."""
    repository = find_repository_root(root)
    records: list[InstructionRecord] = []

    extension_root = repository / "extensions"
    if extension_root.is_dir():
        for path in sorted(extension_root.rglob("rv*")):
            if path.is_file():
                records.extend(parse_extension_file(path, repository))

    yaml_root = repository / "opcodes"
    if yaml_root.is_dir():
        for pattern in ("*.yaml", "*.yml"):
            for path in sorted(yaml_root.rglob(pattern)):
                records.extend(parse_yaml_file(path, repository))

    if not records:
        raise RuntimeError(f"No instruction definitions found under {repository}")
    return repository, records


def format_field(value: int | None, width: int) -> str:
    return "*" if value is None else f"0b{value:0{width}b}"

