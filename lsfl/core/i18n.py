"""
Çoklu dil desteği (i18n) modülü
"""

class Translator:
    def __init__(self):
        self.current_language = "tr_TR"
        self.translations = {
            "tr_TR": {
                # Ana Pencere
                "app_title": "LSFL - Logic Sim For Linux",
                "ready": "Hazır",
                
                # Menüler
                "file": "Dosya",
                "new": "Yeni",
                "open": "Aç",
                "save": "Kaydet",
                "save_as": "Farklı Kaydet",
                "exit": "Çıkış",
                
                "edit": "Düzenle",
                "undo": "Geri Al",
                "redo": "Yinele",
                "delete": "Sil",
                "select_all": "Tümünü Seç",
                
                "simulation": "Simülasyon",
                "start_stop": "Başlat/Durdur",
                "reset": "Sıfırla",
                "step": "Tek Adım",
                
                "export": "Export",
                "export_verilog": "Verilog Kodu Üret",
                "export_png": "PNG Olarak Kaydet",
                
                "help": "Yardım",
                "about": "Hakkında",
                
                # Toolbar
                "start_simulation": "▶ Simülasyon Başlat",
                "stop_simulation": "⏸ Simülasyon Durdur",
                "reset_sim": "⟲ Sıfırla",
                "generate_verilog": "📋 Verilog Kodu Üret",
                
                # Bileşen Grupları
                "io_components": "Giriş/Çıkış",
                "logic_gates": "Mantık Kapıları",
                "arithmetic": "Aritmetik",
                "mux_demux": "Mux/Demux",
                "encoder_decoder": "Encoder/Decoder",
                "flipflops": "Flip-Flops",
                "registers": "Register/Counter",
                "memory": "Bellek",
                "other": "Diğer",
                
                # Bileşenler
                "input_pin": "Input Pin",
                "output_pin": "Output Pin",
                "switch": "Switch",
                "clock": "Clock",
                "led": "LED",
                "and_gate": "AND Kapısı",
                "or_gate": "OR Kapısı",
                "not_gate": "NOT Kapısı",
                "nand_gate": "NAND Kapısı",
                "nor_gate": "NOR Kapısı",
                "xor_gate": "XOR Kapısı",
                "xnor_gate": "XNOR Kapısı",
                "buffer": "Buffer",
                
                # Dialoglar
                "new_circuit": "Yeni Devre",
                "confirm_close": "Mevcut devreyi kapatmak istediğinizden emin misiniz?",
                "circuit_created": "Yeni devre oluşturuldu",
                "circuit_loaded": "Devre yüklendi",
                "circuit_saved": "Devre kaydedildi",
                "error": "Hata",
                "success": "Başarılı",
                
                # Durum Mesajları
                "running": "▶ ÇALIŞIYOR - Clock otomatik, Input/Switch değiştirilebilir",
                "stopped": "⏹ DURDURULDU - Sadece devre düzenleme modu",
                "simulation_reset": "Simülasyon sıfırlandı",
                "verilog_generated": "Verilog kodu üretildi",
                
                # Welcome Screen
                "welcome": "Hoş Geldiniz",
                "new_project": "Yeni Proje",
                "open_project": "Proje Aç",
                "language": "Dil",
                "select_language": "Dil Seçin",
            },
            "en_US": {
                # Main Window
                "app_title": "LSFL - Logic Sim For Linux",
                "ready": "Ready",
                
                # Menus
                "file": "File",
                "new": "New",
                "open": "Open",
                "save": "Save",
                "save_as": "Save As",
                "exit": "Exit",
                
                "edit": "Edit",
                "undo": "Undo",
                "redo": "Redo",
                "delete": "Delete",
                "select_all": "Select All",
                
                "simulation": "Simulation",
                "start_stop": "Start/Stop",
                "reset": "Reset",
                "step": "Step",
                
                "export": "Export",
                "export_verilog": "Generate Verilog Code",
                "export_png": "Save as PNG",
                
                "help": "Help",
                "about": "About",
                
                # Toolbar
                "start_simulation": "▶ Start Simulation",
                "stop_simulation": "⏸ Stop Simulation",
                "reset_sim": "⟲ Reset",
                "generate_verilog": "📋 Generate Verilog",
                
                # Component Groups
                "io_components": "Input/Output",
                "logic_gates": "Logic Gates",
                "arithmetic": "Arithmetic",
                "mux_demux": "Mux/Demux",
                "encoder_decoder": "Encoder/Decoder",
                "flipflops": "Flip-Flops",
                "registers": "Registers/Counters",
                "memory": "Memory",
                "other": "Other",
                
                # Components
                "input_pin": "Input Pin",
                "output_pin": "Output Pin",
                "switch": "Switch",
                "clock": "Clock",
                "led": "LED",
                "and_gate": "AND Gate",
                "or_gate": "OR Gate",
                "not_gate": "NOT Gate",
                "nand_gate": "NAND Gate",
                "nor_gate": "NOR Gate",
                "xor_gate": "XOR Gate",
                "xnor_gate": "XNOR Gate",
                "buffer": "Buffer",
                
                # Dialogs
                "new_circuit": "New Circuit",
                "confirm_close": "Are you sure you want to close the current circuit?",
                "circuit_created": "New circuit created",
                "circuit_loaded": "Circuit loaded",
                "circuit_saved": "Circuit saved",
                "error": "Error",
                "success": "Success",
                
                # Status Messages
                "running": "▶ RUNNING - Clock automatic, Input/Switch editable",
                "stopped": "⏹ STOPPED - Circuit editing mode only",
                "simulation_reset": "Simulation reset",
                "verilog_generated": "Verilog code generated",
                
                # Welcome Screen
                "welcome": "Welcome",
                "new_project": "New Project",
                "open_project": "Open Project",
                "language": "Language",
                "select_language": "Select Language",
            }
        }
    
    def set_language(self, lang_code):
        """Dili değiştir"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False
    
    def tr(self, key):
        """Çeviri al"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def get_available_languages(self):
        """Mevcut dilleri al"""
        return {
            "tr_TR": "Türkçe",
            "en_US": "English"
        }

# Global translator instance
_translator = Translator()

def tr(key):
    """Global çeviri fonksiyonu"""
    return _translator.tr(key)

def set_language(lang_code):
    """Global dil değiştirme"""
    return _translator.set_language(lang_code)

def get_translator():
    """Translator instance'ını al"""
    return _translator
