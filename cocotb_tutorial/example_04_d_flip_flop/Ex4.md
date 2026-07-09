## Example 04: D Flip-Flop
**Learning Goal**: Driving a clock, using background tasks, and synchronizing on rising/falling edges with `ReadOnly()`.

| Reset (`rst`) |      Clock     | Data (`d`) |   Next Output (`q`)  | Explanation                                            |
| :-----------: | :------------: | :--------: | :------------------: | ------------------------------------------------------ |
|       1       |        X       |      X     |           0          | Reset is asserted, so `q` is immediately cleared to 0. |
|       0       |        ↑       |      0     |           0          | On the rising edge, `q` copies `d` (which is 0).       |
|       0       |        ↑       |      1     |           1          | On the rising edge, `q` copies `d` (which is 1).       |
|       0       | No rising edge |      X     | Holds previous value | Without a rising edge, `q` does not change.            |

**Key Concepts**:
- `FallingEdge(dut.clk)`: Pauses Python execution until the clock edge falls from high to low.
- **Wait after reset de-assertion**: After de-asserting reset, always wait 2–3 clock cycles before driving inputs or checking outputs. Real hardware may include logic that needs a few clock cycles to settle. Jumping straight into stimulus immediately after de-assertion creates unrealistic and potentially incorrect tests.
- `await ReadOnly()`: Instructs cocotb to wait until the simulator finishes writing/updating all signals in the current time-step. This is the industry-standard way to read signal values safely without triggering simulation race conditions (where Python reads a signal *before* the simulator has completed its update). Note: You must not write any signals while in the `ReadOnly` phase (e.g. immediately after awaiting `ReadOnly`), or cocotb will throw a `RuntimeError`. You must advance time (e.g. via `await FallingEdge()`) before writing inputs again.
