## Example 01: AND Gate 

**Learning Goal**: Driving input signals, waiting for simulator updates, assertions, and using `dut._log.info()`.

**Key Concepts**:
- `dut`: Represents the "Device Under Test". Signals are accessed as attributes (e.g., `dut.a`).
- `dut.a.value = 1`: Sets the value of signal `a` in the simulator.
- `await Timer(1, unit="ns")`: Pauses Python execution and lets the simulator run for 1 nanosecond so values can propagate.
- `dut._log.info(...)`: Prints logs to the terminal prefixing them with simulation timestamp. Much cleaner than `print()`.
- `assert ...`: Verifies the condition. If false, the test fails.
