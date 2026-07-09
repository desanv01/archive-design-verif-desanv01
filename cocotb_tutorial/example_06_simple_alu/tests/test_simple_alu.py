import random
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_alu_random(dut):
    """Verify ALU outputs using random tests"""

    dut._log.info("Starting ALU test...")

    # Test valid operations
    for i in range(100):

        a_val = random.randint(0, 15)
        b_val = random.randint(0, 15)
        op_val = random.randint(0, 3)

        dut.a.value = a_val
        dut.b.value = b_val
        dut.op.value = op_val

        await Timer(1, unit="ns")

        if op_val == 0:
            value = a_val + b_val
            expected_result = value & 0xF
            expected_carry = (value >> 4) & 1

        elif op_val == 1:
            value = a_val - b_val
            expected_result = value & 0xF
            expected_carry = (value >> 4) & 1

        elif op_val == 2:
            expected_result = a_val & b_val
            expected_carry = 0

        else:  # op_val == 3
            expected_result = a_val | b_val
            expected_carry = 0

        assert int(dut.result.value) == expected_result
        assert int(dut.carry_out.value) == expected_carry

    dut._log.info("Valid opcode tests passed.")

    # ----------------------------
    # Test the default case
    # ----------------------------

    dut._log.info("Testing default case...")

    dut.a.value = 9
    dut.b.value = 6
    dut.op.value = "XX"      # Invalid opcode

    await Timer(1, unit="ns")

    assert int(dut.result.value) == 0, \
        f"Expected result=0 for default case, got {int(dut.result.value)}"

    dut._log.info("Default case passed.")
