"""Task 3: functions, arguments, loops, range, and zip."""


def multiply(a, b):
    return a * b


def reset_device(cycles=4):
    print(f"Resetting for {cycles} cycles")


def compare(a, b):
    return a > b, a < b, a == b


print(f"6 * 7 = {multiply(6, 7)}")
reset_device()
reset_device(cycles=2)
greater, less, equal = compare(9, 3)
print(f"compare(9, 3): gt={greater}, lt={less}, eq={equal}")

for a in range(2):
    for b in range(3):
        print(f"pair: a={a}, b={b}")

inputs = [0, 1, 1, 0]
expected_states = [0b0010, 0b0100, 0b1000, 0b0001]
for bit, state in zip(inputs, expected_states):
    print(f"input {bit} -> state {state:04b}")
