"""
Bileşen fabrikası - tüm bileşen tiplerini oluşturur
"""

from core.components.gates import *
from core.components.arithmetic import *
from core.components.mux import *
from core.components.flipflops import *
from core.components.io import *


class ComponentFactory:
    @staticmethod
    def create(component_type, x, y):
        """Verilen tipte bir bileşen oluştur"""
        
        # Mantık Kapıları
        if component_type == "AND":
            return ANDGate(x, y)
        elif component_type == "OR":
            return ORGate(x, y)
        elif component_type == "NOT":
            return NOTGate(x, y)
        elif component_type == "NAND":
            return NANDGate(x, y)
        elif component_type == "NOR":
            return NORGate(x, y)
        elif component_type == "XOR":
            return XORGate(x, y)
        elif component_type == "XNOR":
            return XNORGate(x, y)
        elif component_type == "BUFFER":
            return BufferGate(x, y)
            
        # Aritmetik
        elif component_type == "HALF_ADDER":
            return HalfAdder(x, y)
        elif component_type == "FULL_ADDER":
            return FullAdder(x, y)
        elif component_type == "ADDER_4BIT":
            return Adder4Bit(x, y)
        elif component_type == "COMPARATOR":
            return Comparator(x, y)
            
        # Multiplexer
        elif component_type == "MUX_2TO1":
            return Mux2to1(x, y)
        elif component_type == "MUX_4TO1":
            return Mux4to1(x, y)
            
        # Flip-Flops
        elif component_type == "D_FLIPFLOP":
            return DFlipFlop(x, y)
        elif component_type == "JK_FLIPFLOP":
            return JKFlipFlop(x, y)
            
        # I/O
        elif component_type == "SWITCH":
            return Switch(x, y)
        elif component_type == "LED":
            return LED(x, y)
        elif component_type == "CLOCK":
            return Clock(x, y)
        elif component_type == "INPUT_PIN":
            return InputPin(x, y)
        elif component_type == "OUTPUT_PIN":
            return OutputPin(x, y)
            
        else:
            # Varsayılan bileşen
            from core.component import Component
            comp = Component(component_type, x, y)
            comp.type = component_type
            return comp
            
    @staticmethod
    def from_dict(data):
        """Dictionary'den bileşen oluştur"""
        comp = ComponentFactory.create(data['type'], data['x'], data['y'])
        comp.name = data.get('name', comp.name)
        return comp
