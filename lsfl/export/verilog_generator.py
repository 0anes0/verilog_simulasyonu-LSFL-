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
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            d = self.get_pin_signal(comp.input_pins[0])
            clk = self.get_pin_signal(comp.input_pins[1])
            rst = self.get_pin_signal(comp.input_pins[2])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    {q}_reg <= 1'b0;")
            code.append(f"  else")
            code.append(f"    {q}_reg <= {d};")
            code.append(f"end")
        
        elif comp.type == "JK_FLIPFLOP":
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            j = self.get_pin_signal(comp.input_pins[0])
            k = self.get_pin_signal(comp.input_pins[1])
            clk = self.get_pin_signal(comp.input_pins[2])
            rst = self.get_pin_signal(comp.input_pins[3])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    {q}_reg <= 1'b0;")
            code.append(f"  else begin")
            code.append(f"    case ({{{j}, {k}}})")
            code.append(f"      2'b00: {q}_reg <= {q}_reg;")
            code.append(f"      2'b01: {q}_reg <= 1'b0;")
            code.append(f"      2'b10: {q}_reg <= 1'b1;")
            code.append(f"      2'b11: {q}_reg <= ~{q}_reg;")
            code.append(f"    endcase")
            code.append(f"  end")
            code.append(f"end")
        
        elif comp.type == "T_FLIPFLOP":
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            t = self.get_pin_signal(comp.input_pins[0])
            clk = self.get_pin_signal(comp.input_pins[1])
            rst = self.get_pin_signal(comp.input_pins[2])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    {q}_reg <= 1'b0;")
            code.append(f"  else if ({t})")
            code.append(f"    {q}_reg <= ~{q}_reg;")
            code.append(f"end")
        
        elif comp.type == "SR_FLIPFLOP":
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            s = self.get_pin_signal(comp.input_pins[0])
            r = self.get_pin_signal(comp.input_pins[1])
            clk = self.get_pin_signal(comp.input_pins[2])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(posedge {clk}) begin")
            code.append(f"  case ({{{s}, {r}}})")
            code.append(f"    2'b00: {q}_reg <= {q}_reg;")
            code.append(f"    2'b01: {q}_reg <= 1'b0;")
            code.append(f"    2'b10: {q}_reg <= 1'b1;")
            code.append(f"    2'b11: {q}_reg <= {q}_reg; // Undefined, hold")
            code.append(f"  endcase")
            code.append(f"end")
        
        elif comp.type == "LATCH_SR":
            # SR Latch - Cross-coupled NOR gates (structural)
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            s = self.get_pin_signal(comp.input_pins[0])
            r = self.get_pin_signal(comp.input_pins[1])
            
            # Asenkron SR Latch - always @(*) ile kombinasyonel
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(*) begin")
            code.append(f"  case ({{{s}, {r}}})")
            code.append(f"    2'b00: {q}_reg = {q}_reg;")
            code.append(f"    2'b01: {q}_reg = 1'b0;")
            code.append(f"    2'b10: {q}_reg = 1'b1;")
            code.append(f"    2'b11: {q}_reg = {q}_reg; // Undefined")
            code.append(f"  endcase")
            code.append(f"end")
        
        elif comp.type == "LATCH_D":
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            d = self.get_pin_signal(comp.input_pins[0])
            en = self.get_pin_signal(comp.input_pins[1])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(*) begin")
            code.append(f"  if ({en})")
            code.append(f"    {q}_reg = {d};")
            code.append(f"end")
        
        elif comp.type == "LATCH_SR":
            # SR Latch - Cross-coupled NOR gates (structural)
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            s = self.get_pin_signal(comp.input_pins[0])
            r = self.get_pin_signal(comp.input_pins[1])
            
            # Asenkron SR Latch - always @(*) ile kombinasyonel
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(*) begin")
            code.append(f"  case ({{{s}, {r}}})")
            code.append(f"    2'b00: {q}_reg = {q}_reg;")
            code.append(f"    2'b01: {q}_reg = 1'b0;")
            code.append(f"    2'b10: {q}_reg = 1'b1;")
            code.append(f"    2'b11: {q}_reg = {q}_reg; // Undefined")
            code.append(f"  endcase")
            code.append(f"end")
        
        elif comp.type == "LATCH_D":
            q = self.get_pin_signal(comp.output_pins[0])
            qn = self.get_pin_signal(comp.output_pins[1]) if len(comp.output_pins) > 1 else None
            d = self.get_pin_signal(comp.input_pins[0])
            en = self.get_pin_signal(comp.input_pins[1])
            
            code.append(f"reg {q}_reg;")
            code.append(f"assign {q} = {q}_reg;")
            if qn:
                code.append(f"assign {qn} = ~{q}_reg;")
            code.append(f"always @(*) begin")
            code.append(f"  if ({en})")
            code.append(f"    {q}_reg = {d};")
            code.append(f"end")
        
        elif comp.type == "MUX_4TO1":
            out = self.get_pin_signal(comp.output_pins[0])
            inputs = [self.get_pin_signal(comp.input_pins[i]) for i in range(4)]
            s0 = self.get_pin_signal(comp.input_pins[4])
            s1 = self.get_pin_signal(comp.input_pins[5])
            
            code.append(f"wire [1:0] sel = {{{s1}, {s0}}};")
            code.append(f"assign {out} = (sel == 2'd0) ? {inputs[0]} :")
            code.append(f"               (sel == 2'd1) ? {inputs[1]} :")
            code.append(f"               (sel == 2'd2) ? {inputs[2]} : {inputs[3]};")
        
        elif comp.type == "MUX_8TO1":
            out = self.get_pin_signal(comp.output_pins[0])
            inputs = [self.get_pin_signal(comp.input_pins[i]) for i in range(8)]
            s0 = self.get_pin_signal(comp.input_pins[8])
            s1 = self.get_pin_signal(comp.input_pins[9])
            s2 = self.get_pin_signal(comp.input_pins[10])
            
            code.append(f"wire [2:0] sel = {{{s2}, {s1}, {s0}}};")
            code.append(f"assign {out} = (sel == 3'd0) ? {inputs[0]} :")
            code.append(f"               (sel == 3'd1) ? {inputs[1]} :")
            code.append(f"               (sel == 3'd2) ? {inputs[2]} :")
            code.append(f"               (sel == 3'd3) ? {inputs[3]} :")
            code.append(f"               (sel == 3'd4) ? {inputs[4]} :")
            code.append(f"               (sel == 3'd5) ? {inputs[5]} :")
            code.append(f"               (sel == 3'd6) ? {inputs[6]} : {inputs[7]};")
        
        elif comp.type == "ADDER_4BIT":
            # 4-bit Ripple Carry Adder
            a_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(4)]
            b_bits = [self.get_pin_signal(comp.input_pins[4+i]) for i in range(4)]
            cin = self.get_pin_signal(comp.input_pins[8])
            s_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
            cout = self.get_pin_signal(comp.output_pins[4])
            
            code.append(f"wire [3:0] a = {{{a_bits[3]}, {a_bits[2]}, {a_bits[1]}, {a_bits[0]}}};")
            code.append(f"wire [3:0] b = {{{b_bits[3]}, {b_bits[2]}, {b_bits[1]}, {b_bits[0]}}};")
            code.append(f"wire [4:0] sum = a + b + {cin};")
            code.append(f"assign {{{s_bits[3]}, {s_bits[2]}, {s_bits[1]}, {s_bits[0]}}} = sum[3:0];")
            code.append(f"assign {cout} = sum[4];")
        
        elif comp.type == "ADDER_8BIT":
            # 8-bit Ripple Carry Adder
            a_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(8)]
            b_bits = [self.get_pin_signal(comp.input_pins[8+i]) for i in range(8)]
            cin = self.get_pin_signal(comp.input_pins[16])
            s_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(8)]
            cout = self.get_pin_signal(comp.output_pins[8])
            
            a_vec = ", ".join(reversed(a_bits))
            b_vec = ", ".join(reversed(b_bits))
            s_vec = ", ".join(reversed(s_bits))
            
            code.append(f"wire [7:0] a = {{{a_vec}}};")
            code.append(f"wire [7:0] b = {{{b_vec}}};")
            code.append(f"wire [8:0] sum = a + b + {cin};")
            code.append(f"assign {{{s_vec}}} = sum[7:0];")
            code.append(f"assign {cout} = sum[8];")
        
        elif comp.type == "COUNTER_4BIT":
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
            clk = self.get_pin_signal(comp.input_pins[0])
            rst = self.get_pin_signal(comp.input_pins[1])
            en = self.get_pin_signal(comp.input_pins[2])
            
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [3:0] count_reg;")
            code.append(f"assign {{{q_vec}}} = count_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    count_reg <= 4'd0;")
            code.append(f"  else if ({en})")
            code.append(f"    count_reg <= count_reg + 4'd1;")
            code.append(f"end")
        
        elif comp.type == "COUNTER_8BIT":
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(8)]
            clk = self.get_pin_signal(comp.input_pins[0])
            rst = self.get_pin_signal(comp.input_pins[1])
            en = self.get_pin_signal(comp.input_pins[2])
            
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [7:0] count_reg;")
            code.append(f"assign {{{q_vec}}} = count_reg;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    count_reg <= 8'd0;")
            code.append(f"  else if ({en})")
            code.append(f"    count_reg <= count_reg + 8'd1;")
            code.append(f"end")
        
        elif comp.type == "REGISTER_4BIT":
            d_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(4)]
            clk = self.get_pin_signal(comp.input_pins[4])
            rst = self.get_pin_signal(comp.input_pins[5])
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
            
            d_vec = ", ".join(reversed(d_bits))
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [3:0] reg_data;")
            code.append(f"assign {{{q_vec}}} = reg_data;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    reg_data <= 4'd0;")
            code.append(f"  else")
            code.append(f"    reg_data <= {{{d_vec}}};")
            code.append(f"end")
        
        elif comp.type == "REGISTER_8BIT":
            d_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(8)]
            clk = self.get_pin_signal(comp.input_pins[8])
            rst = self.get_pin_signal(comp.input_pins[9])
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(8)]
            
            d_vec = ", ".join(reversed(d_bits))
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [7:0] reg_data;")
            code.append(f"assign {{{q_vec}}} = reg_data;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    reg_data <= 8'd0;")
            code.append(f"  else")
            code.append(f"    reg_data <= {{{d_vec}}};")
            code.append(f"end")
        
        elif comp.type == "SHIFT_REGISTER":
            si = self.get_pin_signal(comp.input_pins[0])
            clk = self.get_pin_signal(comp.input_pins[1])
            rst = self.get_pin_signal(comp.input_pins[2])
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
            
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [3:0] shift_data;")
            code.append(f"assign {{{q_vec}}} = shift_data;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    shift_data <= 4'd0;")
            code.append(f"  else")
            code.append(f"    shift_data <= {{shift_data[2:0], {si}}};")
            code.append(f"end")
        
        elif comp.type == "UP_DOWN_COUNTER":
            clk = self.get_pin_signal(comp.input_pins[0])
            rst = self.get_pin_signal(comp.input_pins[1])
            up = self.get_pin_signal(comp.input_pins[2])
            en = self.get_pin_signal(comp.input_pins[3])
            q_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
            
            q_vec = ", ".join(reversed(q_bits))
            
            code.append(f"reg [3:0] updown_count;")
            code.append(f"assign {{{q_vec}}} = updown_count;")
            code.append(f"always @(posedge {clk} or posedge {rst}) begin")
            code.append(f"  if ({rst})")
            code.append(f"    updown_count <= 4'd0;")
            code.append(f"  else if ({en}) begin")
            code.append(f"    if ({up})")
            code.append(f"      updown_count <= updown_count + 4'd1;")
            code.append(f"    else")
            code.append(f"      updown_count <= updown_count - 4'd1;")
            code.append(f"  end")
            code.append(f"end")
        
        elif comp.type in ["SUBTRACTOR", "MULTIPLIER", "COMPARATOR"]:
            # Aritmetik bileşenler için temel implementasyon
            code.append(f"// {comp.type} - Basic implementation")
            if comp.type == "SUBTRACTOR":
                a_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(4)]
                b_bits = [self.get_pin_signal(comp.input_pins[4+i]) for i in range(4)]
                bin_val = self.get_pin_signal(comp.input_pins[8])
                d_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(4)]
                bout = self.get_pin_signal(comp.output_pins[4])
                
                a_vec = ", ".join(reversed(a_bits))
                b_vec = ", ".join(reversed(b_bits))
                d_vec = ", ".join(reversed(d_bits))
                
                code.append(f"wire [3:0] a = {{{a_vec}}};")
                code.append(f"wire [3:0] b = {{{b_vec}}};")
                code.append(f"wire [4:0] diff = a - b - {bin_val};")
                code.append(f"assign {{{d_vec}}} = diff[3:0];")
                code.append(f"assign {bout} = diff[4];")
            elif comp.type == "MULTIPLIER":
                a_bits = [self.get_pin_signal(comp.input_pins[i]) for i in range(4)]
                b_bits = [self.get_pin_signal(comp.input_pins[4+i]) for i in range(4)]
                p_bits = [self.get_pin_signal(comp.output_pins[i]) for i in range(8)]
                
                a_vec = ", ".join(reversed(a_bits))
                b_vec = ", ".join(reversed(b_bits))
                p_vec = ", ".join(reversed(p_bits))
                
                code.append(f"wire [3:0] a = {{{a_vec}}};")
                code.append(f"wire [3:0] b = {{{b_vec}}};")
                code.append(f"wire [7:0] product = a * b;")
                code.append(f"assign {{{p_vec}}} = product;")
        
        else:
            code.append(f"// Component {comp.type} not yet implemented in Verilog generator")
            
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
