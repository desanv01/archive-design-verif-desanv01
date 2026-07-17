"""Task 4: f-strings and numeric formatting."""

a = 13
b = 0b1101

print(f"a = {a}, b = {b}")
print(f"binary: {b:08b}")
print(f"hex: {b:#04x}")
print(f"decimal: {b}")
print(f"bin()={bin(b)}, hex()={hex(b)}")

expected = 13
got = b
assert got == expected, f"Expected {expected}, got {got} ({got:08b})"
print("Formatted assertion check passed")
