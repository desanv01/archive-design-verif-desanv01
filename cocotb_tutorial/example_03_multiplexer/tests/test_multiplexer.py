import random
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_mux_random(dut):
    """Test 2-to-1 Multiplexer with random inputs"""
    dut._log.info("Starting Multiplexer test...")

    for i in range(50):
        a_val = random.randint(0, 15)  # 4-bit range
        b_val = random.randint(0, 15)
        sel_val = random.randint(0, 1)

        dut.a.value = a_val
        dut.b.value = b_val
        dut.sel.value = sel_val

        await Timer(1, unit="ns")

        expected = b_val if sel_val == 1 else a_val
        assert dut.y.value == expected, f"Mux failed: sel={sel_val}, a={a_val}, b={b_val}"
        
    dut._log.info("50 random test trials passed successfully!")
