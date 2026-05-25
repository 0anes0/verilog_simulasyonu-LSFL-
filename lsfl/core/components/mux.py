"""
Multiplexer ve Demultiplexer bileşenleri
"""

from core.component import Component


class Mux2to1(Component):
    def __init__(self, x=0, y=0):
        super().__init__("MUX 2:1", x, y, 90, 70)
        self.type = "MUX_2TO1"
        self.add_input_pin("I0")
        self.add_input_pin("I1")
        self.add_input_pin("Sel")
        self.add_output_pin("Y")
        
    def update(self):
        i0 = self.input_pins[0].value
        i1 = self.input_pins[1].value
        sel = self.input_pins[2].value
        
        self.output_pins[0].set_value(i1 if sel else i0)


class Mux4to1(Component):
    def __init__(self, x=0, y=0):
        super().__init__("MUX 4:1", x, y, 100, 100)
        self.type = "MUX_4TO1"
        
        for i in range(4):
            self.add_input_pin(f"I{i}")
        self.add_input_pin("S0")
        self.add_input_pin("S1")
        self.add_output_pin("Y")
        
    def update(self):
        inputs = [pin.value for pin in self.input_pins[:4]]
        s0 = self.input_pins[4].value
        s1 = self.input_pins[5].value
        
        sel = (s1 << 1) | s0
        self.output_pins[0].set_value(inputs[sel])
