"""Create a disposable directory tree for exercising Problems 1-5."""

import argparse
from pathlib import Path
import shutil
import zipfile


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="demo_data")
    args = parser.parse_args()
    root = Path(args.target).expanduser().resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write(root / "source" / "alpha.txt", "alpha\n")
    write(root / "source" / "nested" / "beta.cfg", "beta\n")
    write(root / "requested_files.txt", "alpha.txt\nbeta.cfg\nmissing.bin\n")

    write(root / "runs" / "run_ok" / "result.txt", "PASS\n")
    write(root / "runs" / "run_bad" / "STATUS_FAILED", "")
    write(root / "runs" / "run_bad" / "result.txt", "FAIL\n")

    write(root / "tests" / "test_v001" / "case.txt", "case 1\n")
    write(root / "tests" / "test_v002" / "case.txt", "case 2\n")
    write(root / "tests" / "other" / "case.txt", "ignored\n")

    write(root / "co" / "add" / "dut" / "output.elf", "ELF add\n")
    write(root / "co" / "add" / "ref" / "reference.txt", "skip me\n")
    write(root / "co" / "mul" / "dut" / "first.elf", "ELF mul 1\n")
    write(root / "co" / "mul" / "dut" / "second.elf", "ELF mul 2\n")

    archive_dir = root / "archives"
    archive_dir.mkdir()
    with zipfile.ZipFile(archive_dir / "good.zip", "w") as archive:
        archive.writestr("from_zip/hello.txt", "hello from ZIP\n")
    (archive_dir / "corrupt.zip").write_bytes(b"not a zip file")

    print(f"Created demo tree: {root}")


if __name__ == "__main__":
    main()

