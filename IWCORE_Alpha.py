import customtkinter as ctk
import cv2
import hashlib
import time
import threading
from PIL import Image, ImageTk
from datetime import datetime

# --- CONFIGURACIÓN ESTÉTICA INDUSTRIAL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BlockchainCore:
    """Motor de Trazabilidad Inmutable SHA-256"""
    def __init__(self):
        self.chain = []
        self.add_block("SYSTEM_INITIALIZED", "ROOT_AUTH")

    def add_block(self, event, user):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prev_hash = self.chain[-1]['hash'] if self.chain else "0"*64
        block_data = f"{event}{user}{timestamp}{prev_hash}"
        new_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        block = {
            "ts": timestamp,
            "event": event,
            "user": user,
            "hash": new_hash
        }
        self.chain.append(block)
        return block

class IWCORE_App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IWCORE™ | Cognitive Safety OS")
        self.geometry("1200x800")
        
        self.engine = BlockchainCore()
        self.current_user = "OPERATOR_01"
        self.risk_active = False

        self.setup_ui()
        self.start_camera()

    def setup_ui(self):
        # Layout: Sidebar y Monitor Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR: Panel de Control y Ledger
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#0a0a0c")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="IWCORE v1.0", font=("Orbitron", 20, "bold"), text_color="#3b82f6").pack(pady=30)
        
        # Monitor de Estado
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="#1a1a1a", corner_radius=10)
        self.status_frame.pack(fill="x", padx=20, pady=10)
        self.status_lbl = ctk.CTkLabel(self.status_frame, text="● AI_CORE: ACTIVE", text_color="#10b981", font=("Consolas", 12, "bold"))
        self.status_lbl.pack(pady=10)

        # Blockchain Terminal
        ctk.CTkLabel(self.sidebar, text="IMMUTABLE_LEDGER", font=("Consolas", 10, "bold"), text_color="gray").pack(pady=(20, 5))
        self.ledger_txt = ctk.CTkTextbox(self.sidebar, fg_color="#000", font=("Consolas", 11), text_color="#3b82f6", height=400)
        self.ledger_txt.pack(fill="both", padx=15, pady=10)

        # Botón de Prueba de Riesgo
        self.risk_btn = ctk.CTkButton(self.sidebar, text="TRIGGER RISK TEST", fg_color="#ef4444", hover_color="#991b1b", 
                                      command=self.toggle_risk, font=("Orbitron", 12))
        self.risk_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        # MONITOR PRINCIPAL (Viewport AR)
        self.viewport = ctk.CTkFrame(self, fg_color="#000", corner_radius=15)
        self.viewport.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.video_lbl = ctk.CTkLabel(self.viewport, text="")
        self.video_lbl.pack(expand=True, fill="both", padx=5, pady=5)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def toggle_risk(self):
        self.risk_active = not self.risk_active
        if self.risk_active:
            block = self.engine.add_block("CRITICAL_RISK_DETECTED", self.current_user)
            self.update_ledger(block)
            self.risk_btn.configure(text="CLEAR HAZARD")
        else:
            self.risk_btn.configure(text="TRIGGER RISK TEST")

    def update_ledger(self, block):
        entry = f"[{block['ts']}] EVENT: {block['event']}\nID: {block['user']}\nHASH: {block['hash'][:16]}...\n\n"
        self.ledger_txt.insert("0.0", entry)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # --- RENDERIZADO DEL ESCUDO CROMÁTICO (AR) ---
            color = (0, 0, 255) if self.risk_active else (0, 255, 157) # BGR
            status_text = "DANGER: VOLTAGE ZONE" if self.risk_active else "ZONE_SECURE_ALPHA"

            # Marco de Seguridad
            cv2.rectangle(frame, (0,0), (frame.shape[1], frame.shape[0]), color, 20)
            
            # HUD Superior
            cv2.putText(frame, f"IWCORE_AI > {status_text}", (40, 60), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
            
            # HUD de Trazabilidad (Solo en riesgo)
            if self.risk_active:
                cv2.putText(frame, "BLOCKCHAIN_LOG: RECORDING...", (40, 100), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            # Conversión para CustomTkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(850, 550))
            
            self.video_lbl.configure(image=img_tk)
            self.video_lbl.image = img_tk

        self.after(15, self.update_frame)

if __name__ == "__main__":
    app = IWCORE_App()
    app.mainloop()
