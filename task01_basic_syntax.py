"""Task 1: basic syntax, operators, comparisons, and conditionals."""

a = 12
b = 0b0110
c = 0x3C

result = a + b
mask = c & 0x0F
shifted = 3 << 2
upper = (c >> 4) & 0x0F

print(f"result={result}, mask={mask}, shifted={shifted}, upper={upper}")
print(f"a==12: {a == 12}, a!=5: {a != 5}, a>10: {a > 10}")

if a > 10:
    print("a is greater than ten")
elif a == 10:
    print("a is ten")
else:
    print("a is less than ten")
