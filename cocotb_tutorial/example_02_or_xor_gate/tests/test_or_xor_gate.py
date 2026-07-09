import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_or_gate(dut):
    """Test the OR gate output (y_or)"""
    dut._log.info("Starting OR gate test...")
    # Test all 4 combinations for OR
    for a_val, b_val, expected in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")
        dut._log.info(f"OR Input: a={a_val}, b={b_val} -> Output: y_or={dut.y_or.value}")
        assert dut.y_or.value == expected, f"OR failed: {a_val} | {b_val} = {expected}, got {dut.y_or.value}"

@cocotb.test()
async def test_xor_gate(dut):
    """Test the XOR gate output (y_xor)"""
    dut._log.info("Starting XOR gate test...")
    # Test all 4 combinations for XOR
    for a_val, b_val, expected in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]:
        dut.a.value = a_val
        dut.b.value = b_val
        await Timer(1, unit="ns")
        dut._log.info(f"XOR Input: a={a_val}, b={b_val} -> Output: y_xor={dut.y_xor.value}")
        assert dut.y_xor.value == expected, f"XOR failed: {a_val} ^ {b_val} = {expected}, got {dut.y_xor.value}"
