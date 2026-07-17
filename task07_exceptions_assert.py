"""Task 7: assertions and exception handling."""


def check_four_bit(value):
    assert 0 <= value <= 15, f"{value} is outside the 4-bit range"
    return value


for value in (7, 15, 21):
    try:
        checked = check_four_bit(value)
        print(f"Accepted value: {checked}")
    except AssertionError as error:
        print(f"Handled assertion: {error}")

try:
    quotient = 20 // 0
except ZeroDivisionError as error:
    print(f"Handled exception: {error}")
