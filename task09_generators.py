"""Task 9: yielding values from a generator."""


def even_counter(limit):
    for value in range(0, limit, 2):
        yield value


generator = even_counter(10)
print(f"first={next(generator)}")
print(f"second={next(generator)}")
print("remaining:")
for value in generator:
    print(value)
