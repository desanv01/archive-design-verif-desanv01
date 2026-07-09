import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_and_gate_simple(dut):
    """Test that a & b behaves as an AND gate"""

    dut._log.info("Starting AND gate simple test...")

    # 1. Drive inputs to 0
    dut.a.value = 0
    dut.b.value = 0
    # Wait for 1 nanosecond for the simulator to propagate values
    await Timer(1, unit="ns")
    dut._log.info(f"Inputs driven: a={dut.a.value}, b={dut.b.value} -> Output: y={dut.y.value}")
    # Assert output y is 0
    assert dut.y.value == 0, f"Expected 0 & 0 = 0, got {dut.y.value}"

    # 2. Drive inputs: a=1, b=0
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, unit="ns")
    dut._log.info(f"Inputs driven: a={dut.a.value}, b={dut.b.value} -> Output: y={dut.y.value}")
    assert dut.y.value == 0, f"Expected 1 & 0 = 0, got {dut.y.value}"

    # 3. Drive inputs: a=0, b=1
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, unit="ns")
    dut._log.info(f"Inputs driven: a={dut.a.value}, b={dut.b.value} -> Output: y={dut.y.value}")
    assert dut.y.value == 0, f"Expected 0 & 1 = 0, got {dut.y.value}"

    # 4. Drive inputs: a=1, b=1
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, unit="ns")
    dut._log.info(f"Inputs driven: a={dut.a.value}, b={dut.b.value} -> Output: y={dut.y.value}")
    assert dut.y.value == 1, f"Expected 1 & 1 = 1, got {dut.y.value}"
    
    dut._log.info("AND gate test completed successfully!")
