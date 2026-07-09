# Student Guide: Learning cocotb from Scratch

Welcome to **cocotb** (Coroutine-based Co-simulation Testbench)!

Unlike traditional hardware verification languages (like SystemVerilog or VHDL) which require learning complex and vendor-specific syntax, **cocotb** allows you to write your testbenches in **Python**. It connects Python to standard HDL simulators (like Icarus Verilog or Verilator) using a simulator interface.

---------

## Cheat Sheet: cocotb Syntax

| Syntax | Action | Example |
|---|---|---|
| `dut.signal_name.value = val` | Write value to signal | `dut.en.value = 1` |
| `val = dut.signal_name.value` | Read value from signal | `en_state = dut.en.value` |
| `await Timer(time, unit)` | Pause test for a duration | `await Timer(5, unit="ns")` |
| `await RisingEdge(clk)` | Wait for clock to go low to high | `await RisingEdge(dut.clk)` |
| `await FallingEdge(clk)` | Wait for clock to go high to low | `await FallingEdge(dut.clk)` |
| `await ClockCycles(clk, num)` | Wait for multiple clock cycles | `await ClockCycles(dut.clk, 4)` |
| `await ReadOnly()` | Wait for signal values to settle | `await ReadOnly()` |
| `await with_timeout(trigger, t, unit)` | Wrap trigger in a timeout guard | `await with_timeout(RisingEdge(dut.ready), 20, "ns")` |
| `Clock(clk_pin, period, unit)` | Create clock generator | `clk = Clock(dut.clk, 10, "ns")` |
| `cocotb.start_soon(clk.start())` | Start background task (like clock) | `cocotb.start_soon(clk.start())` |
| `dut._log.info(message)` | Print styled logging output with simulator time | `dut._log.info("Test passed")` |
