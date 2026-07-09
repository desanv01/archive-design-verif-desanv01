# Python Prerequisites for Learning cocotb

This document covers the Python concepts you need to understand before (or while) learning
**cocotb**.

## 1. Basic Python Syntax

Everything in cocotb testbenches is plain Python. You need to be comfortable with:

```python
# Variables and assignment
a = 5
b = 0b1010   # binary literal
c = 0xFF     # hex literal

# Arithmetic and bitwise operators (very common in hardware tests)
result  = a + b       # addition
mask    = 0xF & 0xFF  # bitwise AND
shifted = 1 << 3      # left shift: 0b1000
upper   = (0xAB >> 4) & 0xF  # extract upper nibble

# Boolean comparison
x = (a == 5)   # True
y = (a != 3)   # True
z = (a > 2)    # True

# Conditional
if a == 5:
    print("a is five")
elif a == 0:
    print("a is zero")
else:
    print("something else")
```

> **Why it matters in cocotb**: Signal values, expected values, and assertions all use
> these operators constantly. Bitwise operations are especially important when working
> with multi-bit values.

---
## 2. Data Structures

Different structures inside which data is stored.
Index starts at 0 and ends with the ( len(structure) - 1 )
### Lists
```python
# Enclosed in []
test_cases = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]

# Append an item (add an item to the end) 
test_cases.append((1, 1, 1))

# Access by index
first = test_cases[0]

# Slicing
subset = test_cases[1:3]  # items at index 1 and 2
```

### Tuples
```python
# Immutable (cannot be changed after creation)
# Enclosed in ()
case = (1, 0, 1)
a_val, b_val, expected = case  # unpacking => a_val =1, b_val = 0, c_val = 1

# Common in cocotb for test case tables
for a, b, exp in [(0,0,0), (1,1,1)]:
    print(a, b, exp)
```

### Dictionaries
```python
# Key-value pairs
opcodes = {
    "ADD": 0b00,
    "SUB": 0b01,
    "AND": 0b10,
    "OR" : 0b11
}

# Access value by key
op = opcodes["ADD"]  # 0b00 is the value
#.items() returns a list of tuples of the key and value pair
print(opcodes.items()) # [("ADD",0b00),("SUB",0b01),("AND",0b10),("OR",0b11)]
# Iterate over key-value pairs
for name, code in opcodes.items():      
    print(f"{name} -> {code}")
```

> **Why it matters in cocotb**: Test cases are almost always stored as lists of tuples.
> Dictionaries are useful for mapping opcode names to bit values, or signal names to
> expected outputs.

---

## 3. Functions and Arguments

```python
# Basic function
def add(a, b):
    return a + b

# Default argument values
def reset_dut(dut, cycles=3):
    # 'cycles' defaults to 3 if not provided
    print(f"Resetting for {cycles} cycles")

# Calling with positional and keyword arguments
reset_dut(dut)             # uses default: cycles=3
reset_dut(dut, cycles=5)   # override default

# Returning multiple values (returns a tuple)
def compare(a, b):
    return a > b, a < b, a == b

gt, lt, eq = compare(3, 5)  # "unpacking" the returned tuple
```

> **Why it matters in cocotb**: The **Golden Model** pattern (Example 09) uses functions
> to compute expected outputs. Helper functions like `reset_dut()` clean up repetitive
> setup code across multiple tests.

---

## 3. Loops and Iteration

```python
# for loop over a range 0 to n-1
for i in range(16):    # 0, 1, 2, ..., 15
    print(i)

# for loop over a list
for val in [0, 1, 0, 1]:
    print(val)

# Nested loops 
for a in range(4):
    for b in range(4):
        print(f"a={a}, b={b}")

# zip: creates a mapping between the 2 lists. Combining 1st item of list1 with 1st item of list2 and so on...
inputs   = [1, 0, 1, 1]
expected = [0b0001, 0b0010, 0b0101, 0b1011]
# zip(inputs, expected) = [(1,0b0001), (2,0b0010), (3,0b0011), (4,0b0100)]
for bit, state in zip(inputs, expected):
    print(f"Input {bit} -> Expected state {bin(state)}")
```

> **Why it matters in cocotb**: `zip()` is used heavily when pairing input sequences
> with expected output sequences.

---



## 4. f-Strings and Formatting

```python
a = 5
b = 0b1010

# f-string: embed variables directly in string
print(f"a = {a}, b = {b}")

# Format as binary, hex, decimal
print(f"binary: {b:04b}")   # 1010 (padded to 4 bits)
print(f"hex:    {b:#x}")    # 0xa
print(f"int:    {b}")       # 10

# bin() and hex() built-in functions
print(bin(b))   # '0b1010'
print(hex(b))   # '0xa'

# Common pattern in assertion error messages:
expected = 3
got = 5
assert got == expected, f"Expected {expected}, got {got} (binary: {got:04b})"
```

---

## 5. Modules and Imports

```python
# Import a whole module
import random

# Import specific items from a module
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles, ReadOnly
from cocotb.clock    import Clock

# Import with alias
import cocotb as cb

# Using the imported items
val = random.randint(0, 15)   # random integer 0-15
```

> **Why it matters in cocotb**: Every cocotb testbench starts with a set of imports.
> Understanding what you are importing and why is the first step to reading any testbench.

---

## 6. Decorators

A **decorator** is a special Python syntax that wraps a function to add behaviour.
cocotb uses `@cocotb.test()` to mark test functions.

```python
# How a decorator works conceptually:
def my_decorator(func):                     # declaration
    def wrapper(*args, **kwargs):
        print("Before the function")
        result = func(*args, **kwargs)
        print("After the function")
        return result
    return wrapper

@my_decorator                               # instantiation - (calling) 
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before the function
# Hello!
# After the function
```

In cocotb:
```python
import cocotb

# @cocotb.test() registers this function as a simulation test.
# Without the decorator, cocotb would not know to run it.
@cocotb.test()
async def test_and_gate(dut):
    dut.a.value = 1
    dut.b.value = 1
```

> **Why it matters in cocotb**: Every testbench function MUST have `@cocotb.test()`.

---

## 7. Exception Handling and assert

### assert
Similar to an 'if' statement in a single line but with condition and output when it fails
```python
# assert condition, "message if False"
assert 1 + 1 == 2, "Math is broken"

# If condition is False, raises AssertionError with the message
x = 5
assert x == 3, f"Expected x=3, got x={x}"
# → AssertionError: Expected x=3, got x=5
```

### try / except
You try to perform some operation, in case you encounter some errors (exceptions), you are instructing the system how to handle it.

In cocotb, `with_timeout` raises a `cocotb.result.SimTimeoutError` if the trigger
does not fire in time:
```python
from cocotb.triggers import with_timeout, RisingEdge

try:
    await with_timeout(RisingEdge(dut.ready), 100, "ns") # waiting for 100 ns for a Rising Edge of the 'dut.ready' signal
except Exception:
    assert False, "Timed out waiting for ready signal!"
```

> **Why it matters in cocotb**: Every verification check uses `assert`. Understanding how
> exceptions work helps you handle timeout errors and write robust tests.

---

## 8. Classes and Objects (Basics)

You do not need to write your own classes for beginner cocotb, but you need to
**use** classes provided by cocotb (like `Clock`).

```python
# A simple class definition
class Dog:
    def __init__(self, name):  # constructor
        self.name = name       # instance attribute

    def bark(self):
        print(f"{self.name} says: Woof!")

# Creating an instance (object) of the class
my_dog = Dog("Rex")  # calls __init__
my_dog.bark()        # calls the method bark
# Output:"Rex says: Woof!"
```

In cocotb you use the `Clock` class like this:
```python
from cocotb.clock import Clock

# Create a Clock object (calls Clock.__init__ internally)
clock = Clock(dut.clk, 10, unit="ns")

# Call a method on the Clock object
cocotb.start_soon(clock.start())
```
---

## 9. Generators and yield
Yield: Here's one value. Remember where I stopped, and continue from here next time.

A generator is a function that **yields** values one at a time, pausing between each yield. It *suspends its own execution* at `yield` 
and *transfers control back to the caller*.

You need to use next() function to yield the next value.

```python
# A normal function returns one value and exits
def normal():
    return 1

# A generator yields multiple values, pausing at each yield
def counter_gen(n):
    for i in range(n):
        yield i          # pause here, resume on next()

gen = counter_gen(3)
print(next(gen))   # 0  (runs until first yield, then pauses)
print(next(gen))   # 1  (resumes, runs until next yield, then pauses)
print(next(gen))   # 2

# More common pattern: iterate over all values
for val in counter_gen(5):
    print(val)  # 0, 1, 2, 3, 4
```

**Key insight**:  This is the exact mental model you need for `await`.

> **Why it matters in cocotb**: `async/await` is built on top of this generator
> mechanism. Understanding `yield` makes `await` intuitive.

---

## 10. Coroutines: async and await

This is the **most important Python concept for cocotb**.

### What is a coroutine?
A coroutine is a function defined with async def. It can pause itself at an await point, hand control back to the simulator,
and resume later when the awaited event occurs.

### How cocotb maps to this
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_coroutine(dut):

    print("A")
    await Timer(10, units="ns")

    print("B")
    await Timer(20, units="ns")

    print("C")
```
The rule is simple:
- **`await Timer(t, unit)`** → give simulator `t` time units, then come back
- **`await RisingEdge(sig)`** → wait until `sig` goes 0→1, then come back
- **`await FallingEdge(sig)`** → wait until `sig` goes 1→0, then come back
- **`await ReadOnly()`** → wait until simulator finishes updating signals, then come back
- **`await ClockCycles(clk, n)`** → wait for `n` rising edges of `clk`, then come back

### Chaining awaits = sequential stimulus
```python
@cocotb.test()
async def test_seq(dut):
    dut.a.value = 0          # drive a = 0
    await Timer(5, unit="ns")  # wait 5 ns
    dut.a.value = 1          # drive a = 1
    await Timer(5, unit="ns")  # wait 5 ns
    # runs sequentially: 0 → (5 ns) → 1 → (5 ns)
```

---

## 11. Concurrency: Fork and Join with start_soon

### The Problem
What if you want two things to happen **at the same time** in simulation?

For example:
- A **clock generator** toggling forever in the background
- While your **test code** drives inputs and checks outputs

If you just `await clock_toggle_forever()`, your test never runs. You need **concurrency**.

### `cocotb.start_soon()` — Fork
Fork (start_soon) = "Start this task and let it run in the background."


`cocotb.start_soon(coroutine)` launches a coroutine **concurrently in the background**
and returns a `Task` object immediately — it does NOT wait for the coroutine to finish.

```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_clock(dut):

    # FORK: start the clock generator in the background, continue immediately
    clock = Clock(dut.clk, 10, unit="ns")
    clk_task = cocotb.start_soon(clock.start())
    # ↑ clock is now running independently. We don't await it.

    # Meanwhile, THIS coroutine continues doing test work:
    await ClockCycles(dut.clk, 5)  # wait 5 rising edges
    dut.a.value = 1
    await ClockCycles(dut.clk, 1)
    assert dut.y.value == 1
```

### Forking your own coroutines

You can `start_soon` any `async def` function, not just the built-in clock:

```python
async def monitor(dut):
    """A background monitor that watches for unexpected output"""
    for _ in range(100):   # watch for 100 cycles
        await RisingEdge(dut.clk)
        if dut.error_flag.value == 1:
            assert False, "DUT raised error_flag unexpectedly!"

@cocotb.test()
async def test_with_monitor(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # FORK the monitor — it runs in background while test proceeds
    monitor_task = cocotb.start_soon(monitor(dut))

    # Run the actual test stimulus
    dut.en.value = 1
    await ClockCycles(dut.clk, 20)

    # At end, the monitor_task finishes naturally (after 100 cycles)
    # or raises AssertionError if it detects an error
```

### Join — waiting for a forked task to finish
Join (await task) = "At some later point, wait until that background task has completed."
If you want to wait for a forked task to **complete**, you `await` its Task object.

```python
@cocotb.test()
async def test_fork_join(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start()) # starting clock coroutine in background

    # Fork two background tasks
    task_a = cocotb.start_soon(drive_a(dut))  # starting task A coroutine in background
    task_b = cocotb.start_soon(drive_b(dut))  # starting task B coroutine in background

    # JOIN: wait for both to finish before asserting
    await task_a  # blocks until task_a coroutine returns
    await task_b  # blocks until task_b coroutine returns

    # Now safe to check outputs — both drivers are done
    assert dut.out.value == 1
```

### Fork-Join Summary Table

| SystemVerilog | cocotb equivalent | Meaning |
|---|---|---|
| `fork ... join` | `t = start_soon(coro); await t` | Fork one task, join it |
| `fork ... join_none` | `start_soon(coro)` | Fork and never join (fire & forget) |
| `fork ... join_any` | `await First(task_a, task_b)` | Wait for whichever finishes first |

### Multiple forked tasks (join_any pattern)

```python
from cocotb.triggers import First

@cocotb.test()
async def test_join_any(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Wait for EITHER a timeout OR the ready signal — whichever comes first
    result = await First(
        ClockCycles(dut.clk, 100),   # timeout after 100 cycles
        RisingEdge(dut.ready)        # or ready went high
    )

    if result == RisingEdge(dut.ready):
        dut._log.info("Ready signal received!")
    else:
        assert False, "Timed out waiting for ready!"
```

---

## Quick Reference: Python Concepts in cocotb Context

| Python Concept | Where You See It in cocotb |
|---|---|
| `async def` | Every test function and helper coroutine |
| `await` | Every simulator interaction (Timer, RisingEdge, etc.) |
| `for` loop | Exhaustive input sweep, sequential stimulus |
| `zip()` | Pairing input sequences with expected output sequences |
| `range()` | Driving n clock cycles worth of incrementing test values |
| `random.randint()` | Random stimulus generation |
| `assert` | Every output check in every test |
| f-strings | Every assertion message and log statement |
| Decorator `@cocotb.test()` | Registering a function as a cocotb test |
| `cocotb.start_soon()` | Forking background tasks (clock, monitor, driver) |
| `await task` | Joining a forked task (waiting for it to finish) |
| `try / except` | Catching timeout errors from `with_timeout` |
