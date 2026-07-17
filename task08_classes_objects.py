"""Task 8: defining and using a class."""


class Register:
    def __init__(self, name, width=8):
        self.name = name
        self.width = width
        self.value = 0

    def write(self, value):
        self.value = value & ((1 << self.width) - 1)

    def display(self):
        print(f"{self.name}={self.value:0{self.width}b}")


status = Register("STATUS", width=8)
status.write(0x1A3)
status.display()
