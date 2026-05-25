"""
Bileşen fabrikası - tüm bileşen tiplerini oluşturur
"""

from core.components.gates import *
from core.components.arithmetic import *
from core.components.mux import *
from core.components.flipflops import *
from core.components.io import *
from core.components.advanced import *


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
        elif component_type == "ADDER_8BIT":
            return Adder8Bit(x, y)
        elif component_type == "SUBTRACTOR":
            return Subtractor(x, y)
        elif component_type == "MULTIPLIER":
            return Multiplier(x, y)
        elif component_type == "COMPARATOR":
            return Comparator(x, y)
            
        # Multiplexer/Demultiplexer
        elif component_type == "MUX_2TO1":
            return Mux2to1(x, y)
        elif component_type == "MUX_4TO1":
            return Mux4to1(x, y)
        elif component_type == "MUX_8TO1":
            return Mux8to1(x, y)
        elif component_type == "DEMUX_1TO2":
            return Demux1to2(x, y)
        elif component_type == "DEMUX_1TO4":
            return Demux1to4(x, y)
        elif component_type == "DEMUX_1TO8":
            return Demux1to8(x, y)
        
        # Encoder/Decoder
        elif component_type == "ENCODER_4TO2":
            return Encoder4to2(x, y)
        elif component_type == "ENCODER_8TO3":
            return Encoder8to3(x, y)
        elif component_type == "DECODER_2TO4":
            return Decoder2to4(x, y)
        elif component_type == "DECODER_3TO8":
            return Decoder3to8(x, y)
        elif component_type == "PRIORITY_ENCODER":
            return Encoder8to3(x, y)  # Priority encoder olarak kullan
            
        # Flip-Flops
        elif component_type == "D_FLIPFLOP":
            return DFlipFlop(x, y)
        elif component_type == "JK_FLIPFLOP":
            return JKFlipFlop(x, y)
        elif component_type == "T_FLIPFLOP":
            return TFlipFlop(x, y)
        elif component_type == "SR_FLIPFLOP":
            return SRFlipFlop(x, y)
        elif component_type == "LATCH_D":
            return DLatch(x, y)
        elif component_type == "LATCH_SR":
            return SRLatch(x, y)
        
        # Register/Counter
        elif component_type == "REGISTER_4BIT":
            return Register4Bit(x, y)
        elif component_type == "REGISTER_8BIT":
            return Register8Bit(x, y)
        elif component_type == "SHIFT_REGISTER":
            return ShiftRegister(x, y)
        elif component_type == "COUNTER_4BIT":
            return Counter4Bit(x, y)
        elif component_type == "COUNTER_8BIT":
            return Counter8Bit(x, y)
        elif component_type == "UP_DOWN_COUNTER":
            return UpDownCounter(x, y)
        
        # Memory
        elif component_type == "RAM_16X8":
            return RAM16x8(x, y)
        elif component_type == "RAM_256X8":
            return RAM256x8(x, y)
        elif component_type == "ROM_16X8":
            return ROM16x8(x, y)
        elif component_type == "ROM_256X8":
            return ROM256x8(x, y)
        
        # Diğer
        elif component_type == "SPLITTER":
            return Splitter(x, y)
        elif component_type == "MERGER":
            return Merger(x, y)
            
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
