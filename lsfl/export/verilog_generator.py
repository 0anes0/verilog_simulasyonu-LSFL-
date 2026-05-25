"""
Verilog kod üreteci - devreyi Verilog koduna çevirir
"""


class VerilogGenerator:
    def __init__(self, circuit):
        self.circuit = circuit
        self.module_name = "generated_circuit"
        
    def generate(self):
        """Tam Verilog kodu üret"""
        code = []
        
        # Modül başlığı
        code.append(f"module {self.module_name} (")
        
        # Port listesi
        ports = self.generate_ports()
        code.append("  " + ",\n  ".join(ports))
        code.append(");")
        code.append("")
        
        # Port tanımlamaları
        code.extend(self.generate_port_declarations())
        code.append("")
        
        # İç sinyaller
        code.extend(self.generate_internal_signals())
        code.append("")
        
        # Bileşen instansları
        code.extend(self.generate_component_instances())
        code.append("")
        
        code.append("endmodule")
        
        return "\n".join(code)
        
    def generate_ports(self):
        """Modül portlarını üret"""
        ports = []
        
        # Giriş portları (Switch, Button, Clock)
        for comp in self.circuit.components:
            if comp.type in ["SWITCH", "BUTTON", "CLOCK"]:
                for pin in comp.output_pins:
                    ports.append(f"input {self.sanitize_name(comp.name)}_{pin.name}")
                    
        # Çıkış portları (LED, Display)
        for comp in self.circuit.components:
            if comp.type in ["LED", "SEVEN_SEGMENT", "HEX_DISPLAY"]:
                for pin in comp.input_pins:
                    ports.append(f"output {self.sanitize_name(comp.name)}_{pin.name}")
                    
        return ports if ports else ["// No external ports"]
        
    def generate_port_declarations(self):
        """Port tanımlamalarını üret"""
        decls = []
        
        # Çıkış portları için wire/reg tanımlamaları
        for comp in self.circuit.components:
            if comp.type in ["LED", "SEVEN_SEGMENT", "HEX_DISPLAY"]:
                for pin in comp.input_pins:
                    decls.append(f"wire {self.sanitize_name(comp.name)}_{pin.name};")
                    
        return decls
        
    def generate_internal_signals(self):
        """İç sinyalleri üret"""
        signals = []
        signals.append("// Internal signals")
        
        # Her bileşenin çıkış pinleri için sinyal
        for comp in self.circuit.components:
            if comp.type not in ["SWITCH", "BUTTON", "CLOCK", "LED", "SEVEN_SEGMENT"]:
                for pin in comp.output_pins:
                    signal_name = f"{self.sanitize_name(comp.name)}_{pin.name}"
                    signals.append(f"wire {signal_name};")
                    
        return signals
        
    def generate_component_instances(self):
        """Bileşen instanslarını üret"""
        instances = []
        instances.append("// Component instances")
        
        for comp in self.circuit.components:
            if comp.type in ["SWITCH", "BUTTON", "CLOCK", "LED"]:
                continue  # I/O bileşenleri için instance oluşturma
                
            instances.append("")
            instances.append(f"// {comp.name}")
            instances.extend(self.generate_component_verilog(comp))
            
        return instances
        
    def generate_component_verilog(self, comp):
        """Tek bir bileşen için Verilog kodu üret"""
        code = []
        
        if comp.type == "AND":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = {in_a} & {in_b};")
            
        elif comp.type == "OR":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = {in_a} | {in_b};")
            
        elif comp.type == "NOT":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            code.append(f"assign {out} = ~{in_a};")
            
        elif comp.type == "NAND":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = ~({in_a} & {in_b});")
            
        elif comp.type == "NOR":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = ~({in_a} | {in_b});")
            
        elif comp.type == "XOR":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = {in_a} ^ {in_b};")
            
        elif comp.type == "XNOR":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {out} = ~({in_a} ^ {in_b});")
            
        elif comp.type == "BUFFER":
            out = self.get_pin_signal(comp.output_pins[0])
            in_a = self.get_pin_signal(comp.input_pins[0])
            code.append(f"assign {out} = {in_a};")
            
        elif comp.type == "HALF_ADDER":
            sum_out = self.get_pin_signal(comp.output_pins[0])
            carry_out = self.get_pin_signal(comp.output_pins[1])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            code.append(f"assign {sum_out} = {in_a} ^ {in_b};")
            code.append(f"assign {carry_out} = {in_a} & {in_b};")
            
        elif comp.type == "FULL_ADDER":
            sum_out = self.get_pin_signal(comp.output_pins[0])
            carry_out = self.get_pin_signal(comp.output_pins[1])
            in_a = self.get_pin_signal(comp.input_pins[0])
            in_b = self.get_pin_signal(comp.input_pins[1])
            cin = self.get_pin_signal(comp.input_pins[2])
            code.append(f"assign {sum_out} = {in_a} ^ {in_b} ^ {cin};")
            code.append(f"assign {carry_out} = ({in_a} & {in_b}) | ({cin} & ({in_a} ^ {in_b}));")
            
        elif comp.type == "MUX_2TO1":
            out = self.get_pin_signal(comp.output_pins[0])
            i0 = self.get_pin_signal(comp.input_pins[0])
            i1 = self.get_pin_signal(comp.input_pins[1])
            sel = self.get_pin_signal(comp.input_pins[2])
            code.append(f"assign {out} = {sel} ? {i1} : {i0};")
            
        elif comp.type == "D_FLIPFLOP":
            q = self.get_pin_signal(comp.output_pins[0])
            d = self.get_pin_signal(comp.input_pins[0])
            clk = self.get_pin_signal(comp.input_pins[1])
            rst = self.get_pin_signal(comp.input_pins[2])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    {q}_reg <= 1'b0;")
            code.append(f"  else")
            code.append(f"    {q}_reg <= {d};")
            code.append(f"end")
            
        else:
            code.append(f"// TODO: Implement {comp.type}")
            
        return code
        
    def get_pin_signal(self, pin):
        """Pin için sinyal adını al"""
        # Kabloya bağlı mı kontrol et
        for wire in self.circuit.wires:
            if wire.to_pin == pin:
                # Kaynak pin'in sinyalini kullan
                return self.get_pin_signal_name(wire.from_pin)
                
        return self.get_pin_signal_name(pin)
        
    def get_pin_signal_name(self, pin):
        """Pin için sinyal adı oluştur"""
        comp = pin.component
        
        # I/O bileşenleri için özel isimler
        if comp.type in ["SWITCH", "BUTTON", "CLOCK"]:
            return f"{self.sanitize_name(comp.name)}_{pin.name}"
        elif comp.type in ["LED", "SEVEN_SEGMENT"]:
            return f"{self.sanitize_name(comp.name)}_{pin.name}"
        else:
            return f"{self.sanitize_name(comp.name)}_{pin.name}"
            
    def sanitize_name(self, name):
        """İsmi Verilog için temizle"""
        # Boşlukları alt çizgi ile değiştir
        name = name.replace(" ", "_")
        # Özel karakterleri kaldır
        name = "".join(c for c in name if c.isalnum() or c == "_")
        # Sayı ile başlıyorsa önüne _ ekle
        if name and name[0].isdigit():
            name = "_" + name
        return name.lower()
