"""
Aritmetik bileşenler
"""

from core.component import Component


class HalfAdder(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Half Adder", x, y, 100, 70)
        self.type = "HALF_ADDER"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Sum")
        self.add_output_pin("Carry")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        self.output_pins[0].set_value(a != b)  # Sum = A XOR B
        self.output_pins[1].set_value(a and b)  # Carry = A AND B


class FullAdder(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Full Adder", x, y, 100, 80)
        self.type = "FULL_ADDER"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_input_pin("Cin")
        self.add_output_pin("Sum")
        self.add_output_pin("Cout")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        cin = self.input_pins[2].value
        
        sum_val = a != b != cin
        cout = (a and b) or (cin and (a != b))
        
        self.output_pins[0].set_value(sum_val)
        self.output_pins[1].set_value(cout)


class Adder4Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("4-bit Adder", x, y, 120, 120)
        self.type = "ADDER_4BIT"
        
        # 4-bit girişler
        for i in range(4):
            self.add_input_pin(f"A{i}")
        for i in range(4):
            self.add_input_pin(f"B{i}")
        self.add_input_pin("Cin")
        
        # 4-bit çıkış + carry
        for i in range(4):
            self.add_output_pin(f"S{i}")
        self.add_output_pin("Cout")
        
    def update(self):
        # 4-bit toplama
        a = sum(self.input_pins[i].value << i for i in range(4))
        b = sum(self.input_pins[4+i].value << i for i in range(4))
        cin = self.input_pins[8].value
        
        result = a + b + cin
        
        for i in range(4):
            self.output_pins[i].set_value((result >> i) & 1)
        self.output_pins[4].set_value((result >> 4) & 1)


class Comparator(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Comparator", x, y, 100, 80)
        self.type = "COMPARATOR"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("A>B")
        self.add_output_pin("A=B")
        self.add_output_pin("A<B")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        
        self.output_pins[0].set_value(a and not b)  # A > B
        self.output_pins[1].set_value(a == b)        # A = B
        self.output_pins[2].set_value(not a and b)  # A < B
