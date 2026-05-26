"""
Temel mantık kapıları
"""

from core.component import Component


class ANDGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("AND", x, y, 80, 60)
        self.type = "AND"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        """AND mantığı: Y = A AND B"""
        try:
            a = bool(self.input_pins[0].value) if len(self.input_pins) > 0 else False
            b = bool(self.input_pins[1].value) if len(self.input_pins) > 1 else False
            result = a and b
            self.output_pins[0].set_value(result)
        except (IndexError, AttributeError):
            self.output_pins[0].set_value(False)


class ORGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("OR", x, y, 80, 60)
        self.type = "OR"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        """OR mantığı: Y = A OR B"""
        try:
            a = bool(self.input_pins[0].value) if len(self.input_pins) > 0 else False
            b = bool(self.input_pins[1].value) if len(self.input_pins) > 1 else False
            result = a or b
            self.output_pins[0].set_value(result)
        except (IndexError, AttributeError):
            self.output_pins[0].set_value(False)


class NOTGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("NOT", x, y, 60, 50)
        self.type = "NOT"
        self.add_input_pin("A")
        self.add_output_pin("Y")
        
    def update(self):
        """NOT mantığı: Y = NOT A"""
        try:
            a = bool(self.input_pins[0].value) if len(self.input_pins) > 0 else False
            result = not a
            self.output_pins[0].set_value(result)
        except (IndexError, AttributeError):
            self.output_pins[0].set_value(True)


class NANDGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("NAND", x, y, 80, 60)
        self.type = "NAND"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        self.output_pins[0].set_value(not (a and b))


class NORGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("NOR", x, y, 80, 60)
        self.type = "NOR"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        self.output_pins[0].set_value(not (a or b))


class XORGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("XOR", x, y, 80, 60)
        self.type = "XOR"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        self.output_pins[0].set_value(a != b)


class XNORGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("XNOR", x, y, 80, 60)
        self.type = "XNOR"
        self.add_input_pin("A")
        self.add_input_pin("B")
        self.add_output_pin("Y")
        
    def update(self):
        a = self.input_pins[0].value
        b = self.input_pins[1].value
        self.output_pins[0].set_value(a == b)


class BufferGate(Component):
    def __init__(self, x=0, y=0):
        super().__init__("BUFFER", x, y, 60, 50)
        self.type = "BUFFER"
        self.add_input_pin("A")
        self.add_output_pin("Y")
        
    def update(self):
        self.output_pins[0].set_value(self.input_pins[0].value)
