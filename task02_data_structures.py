"""Task 2: lists, tuples, and dictionaries."""

test_cases = [(0, 0, 0), (0, 1, 1), (1, 0, 1)]
test_cases.append((1, 1, 1))

print(f"first={test_cases[0]}")
print(f"middle={test_cases[1:3]}")

case = (7, 4, 11)
a_val, b_val, expected = case
print(f"tuple: {a_val}+{b_val}={expected}")

opcodes = {"ADD": 0b00, "SUB": 0b01, "XOR": 0b10, "SHIFT": 0b11}
for name, code in opcodes.items():
    print(f"{name} -> {code:02b}")
