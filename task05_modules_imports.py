"""Task 5: importing modules and selected functions."""

import random
from math import gcd

random.seed(25)
values = [random.randint(0, 31) for _ in range(5)]

print(f"seeded 5-bit values: {values}")
print(f"gcd(84, 30) = {gcd(84, 30)}")
