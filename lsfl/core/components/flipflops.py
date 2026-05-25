"""
Flip-Flop bileşenleri
"""

from core.component import Component


class DFlipFlop(Component):
    def __init__(self, x=0, y=0):
        super().__init__("D FF", x, y, 90, 80)
        self.type = "D_FLIPFLOP"
        self.add_input_pin("D")
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        self.last_clk = False
        
    def update(self):
        d = self.input_pins[0].value
        clk = self.input_pins[1].value
        rst = self.input_pins[2].value
        
        if rst:
            self.state = False
        elif clk and not self.last_clk:  # Rising edge
            self.state = d
            
        self.last_clk = clk
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False
        self.last_clk = False


class JKFlipFlop(Component):
    def __init__(self, x=0, y=0):
        super().__init__("JK FF", x, y, 90, 90)
        self.type = "JK_FLIPFLOP"
        self.add_input_pin("J")
        self.add_input_pin("K")
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        self.last_clk = False
        
    def update(self):
        j = self.input_pins[0].value
        k = self.input_pins[1].value
        clk = self.input_pins[2].value
        rst = self.input_pins[3].value
        
        if rst:
            self.state = False
        elif clk and not self.last_clk:  # Rising edge
            if j and k:
                self.state = not self.state  # Toggle
            elif j:
                self.state = True
            elif k:
                self.state = False
                
        self.last_clk = clk
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False
        self.last_clk = False
