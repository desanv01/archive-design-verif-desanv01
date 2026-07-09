import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, ClockCycles

@cocotb.test()
async def test_d_flip_flop(dut):
    """Test sequential D flip-flop with reset and data input transitions"""

    dut._log.info("Starting D Flip-Flop test...")

    # 1. Start a 10ns clock in the background
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # 2. Assert reset, hold all inputs to safe defaults
    dut._log.info("Asserting reset...")
    dut.rst.value = 1
    dut.d.value = 0
    await FallingEdge(dut.clk)

    # 3. Deassert reset on a falling edge
    dut.rst.value = 0
    dut._log.info("Reset de-asserted. Waiting 3 cycles for design to exit reset cleanly...")

    # 4. Wait 3 clock cycles after reset for the design to fully settle
    #    This is standard practice: real designs need time to synchronize out of reset.
    await ClockCycles(dut.clk, 3)

    await ReadOnly()
    assert dut.q.value == 0, f"Expected Q=0 after reset settling, got {dut.q.value}"
    dut._log.info("Design settled after reset. Starting data test...")

    # 5. Drive D = 1 on FallingEdge (drive on fall, sample on rise pattern)
    await FallingEdge(dut.clk)
    dut.d.value = 1
    dut._log.info("D driven to 1 on falling edge")

    await RisingEdge(dut.clk)
    await ReadOnly()
    dut._log.info(f"Posedge clock sample: Q={dut.q.value}")
    assert dut.q.value == 1, f"Expected Q=1 after posedge when D=1, got {dut.q.value}"

    # 6. Drive D = 0 on FallingEdge
    await FallingEdge(dut.clk)
    dut.d.value = 0
    dut._log.info("D driven to 0 on falling edge")

    await RisingEdge(dut.clk)
    await ReadOnly()
    dut._log.info(f"Posedge clock sample: Q={dut.q.value}")
    assert dut.q.value == 0, f"Expected Q=0 after posedge when D=0, got {dut.q.value}"
    
    dut._log.info("D Flip-Flop test completed successfully!")
