"""Focused tests for the Week-1 assignment scripts."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OPCODE_DIR = ROOT / "riscv_opcodes"
FILE_DIR = ROOT / "file_handling"
TEST_TMP = ROOT / "test_tmp"
TEST_TMP.mkdir(exist_ok=True)
sys.path.insert(0, str(OPCODE_DIR))

from opcode_parser import load_instructions  # noqa: E402


class OpcodeAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEST_TMP)
        self.root = Path(self.temp.name)
        extensions = self.root / "extensions"
        extensions.mkdir()
        (extensions / "rv_i").write_text(
            "\n".join(
                [
                    "add rd rs1 rs2 31..25=0 14..12=0 6..2=0x0C 1..0=3",
                    "sub rd rs1 rs2 31..25=32 14..12=0 6..2=0x0C 1..0=3",
                    "$pseudo_op rv_i::addi nop 31..20=0 19..15=0 14..12=0 11..7=0 6..2=0x04 1..0=3",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_current_extension_parser(self):
        _, records = load_instructions(self.root)
        by_name = {record.mnemonic: record for record in records}
        self.assertEqual(set(by_name), {"add", "sub", "nop"})
        self.assertEqual(by_name["add"].opcode, 0b0110011)
        self.assertEqual(by_name["add"].funct3, 0)
        self.assertEqual(by_name["sub"].funct7, 0b0100000)

    def test_all_opcode_cli_outputs_sorted_file(self):
        output = self.root / "all_opcodes.txt"
        subprocess.run(
            [
                sys.executable,
                str(OPCODE_DIR / "print_opcodes.py"),
                "--root",
                str(self.root),
                "--output",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(output.read_text(encoding="utf-8").splitlines(), ["add", "nop", "sub"])


class FileAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEST_TMP)
        self.root = Path(self.temp.name) / "demo"
        subprocess.run(
            [sys.executable, str(FILE_DIR / "create_demo_data.py"), str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, name: str, *arguments: str):
        return subprocess.run(
            [sys.executable, str(FILE_DIR / name), *map(str, arguments)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_extract_zip_skips_corrupt_archive(self):
        result = self.run_script("extract_zip_files.py", self.root)
        self.assertTrue((self.root / "archives" / "from_zip" / "hello.txt").is_file())
        self.assertIn("skipped=1", result.stdout)

    def test_copy_listed_files(self):
        destination = self.root / "listed_output"
        self.run_script(
            "copy_listed_files.py",
            self.root,
            destination,
            "--list-file",
            self.root / "requested_files.txt",
        )
        self.assertTrue((destination / "alpha" / "alpha.txt").is_file())
        self.assertTrue((destination / "beta" / "beta.cfg").is_file())

    def test_collect_and_matching_directories(self):
        self.run_script("collect_failed_subdirectories.py", self.root)
        self.assertTrue(
            (self.root / "failed_subdirectories" / "runs" / "run_bad" / "STATUS_FAILED").is_file()
        )
        destination = self.root / "matching"
        self.run_script("copy_matching_directories.py", self.root / "tests", destination)
        self.assertTrue((destination / "test_v001" / "case.txt").is_file())
        self.assertFalse((destination / "other").exists())

    def test_codirectory_copy_renames_elf_and_skips_ref(self):
        destination = self.root / "co_output"
        self.run_script("rename_copy_codirectories.py", self.root / "co", destination)
        self.assertTrue((destination / "add" / "dut" / "add.elf").is_file())
        self.assertTrue((destination / "mul" / "dut" / "mul.elf").is_file())
        self.assertTrue((destination / "mul" / "dut" / "mul_2.elf").is_file())
        self.assertFalse((destination / "add" / "ref").exists())


if __name__ == "__main__":
    unittest.main()

