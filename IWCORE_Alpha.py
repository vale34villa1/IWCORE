import customtkinter as ctk
import cv2
import hashlib
import threading
import time
from PIL import Image, ImageTk
from datetime import datetime
import tkinter.messagebox as messagebox

# --- CONFIGURACIÓN DE BRANDING ---
COLOR_BG = "#020617"        # Deep Space
COLOR_BLUE = "#3b82f6"      # Action Blue (Objetos)
COLOR_YELLOW = "#fbbf24"    # Warning Gold (Lugars)
COLOR_RED = "#ef4444"       # Critical Red (Peligro)

class IWCORE_App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de Ventana
        self.title("IWCORE™ | Tactical Safety OS")
        self.geometry("1280x800")
        self.configure(fg_color=COLOR_BG)
        
        # Variables de Control
        self.current_user = None
        self.blockchain = []
        self.is_running = True
        self.risk_detected = False
        
        self.show_login_screen()

    # --- SECCIÓN 1: SISTEMA DE AUTENTICACIÓN ---
    def show_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=20, fg_color="#0f172a")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="IWCORE ACCESS", font=("Orbitron", 28, "bold"), text_color=COLOR_BLUE).pack(pady=(50, 20))
        
        self.user_entry = ctk.CTkEntry(self.login_frame, placeholder_text="OPERATOR_ID", width=280, height=45, border_color=COLOR_BLUE)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="PASSWORD", show="*", width=280, height=45)
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(self.login_frame, text="INITIALIZE PROTOCOL", fg_color=COLOR_BLUE, hover_color="#2563eb",
                      command=self.handle_login, height=45, width=280, font=("Orbitron", 12)).pack(pady=30)

    def handle_login(self):
        user = self.user_entry.get()
        if len(user) > 3:
            self.current_user = user
            self.register_event("AUTH_SUCCESS_SESSION_START")
            self.login_frame.destroy()
            self.setup_main_interface()
        else:
            messagebox.showwarning("Access Denied", "ID de operador no válido (Min. 4 caracteres).")

    # --- SECCIÓN 2: INTERFAZ TÁCTICA (DASHBOARD) ---
    def setup_main_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar: Ledger Inmutable
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#000000")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="SAFETY LEDGER", font=("Orbitron", 14), text_color=COLOR_BLUE).pack(pady=20)
        
        self.ledger_view = ctk.CTkTextbox(self.sidebar, fg_color="#050505", font=("Consolas", 11), text_color=COLOR_BLUE, border_width=1)
        self.ledger_view.pack(fill="both", expand=True, padx=15, pady=10)

        # Monitor Principal (Viewport)
        self.viewport = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.viewport.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.video_lbl = ctk.CTkLabel(self.viewport, text="")
        self.video_lbl.pack(expand=True, fill="both")

        # Controles Inferiores
        self.controls = ctk.CTkFrame(self.viewport, fg_color="transparent")
        self.controls.pack(fill="x", pady=10)
        
        ctk.CTkButton(self.controls, text="FORZAR ALERTA DE RIESGO", fg_color=COLOR_RED, 
                      command=self.simulate_danger, font=("Orbitron", 10)).pack(side="right", padx=20)

        # Iniciar Hilo de Video
        self.cap = cv2.VideoCapture(0)
        threading.Thread(target=self.video_stream_thread, daemon=True).start()

    # --- SECCIÓN 3: MOTOR DE VISIÓN Y HUD (COLORES) ---
    def video_stream_thread(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret: break

            h, w, _ = frame.shape

            # 1. Identificación de OBJETO (AZUL)
            cv2.rectangle(frame, (100, 100), (300, 350), (246, 130, 59), 2) # BGR
            cv2.putText(frame, "OBJ: MAQUINARIA_A1", (100, 90), 1, 1, (246, 130, 59), 2)

            # 2. Identificación de LUGAR (AMARILLO)
            cv2.line(frame, (0, h-100), (w, h-100), (36, 191, 251), 3)
            cv2.putText(frame, "LOC: ZONA_DE_CARGA", (20, h-110), 1, 1, (36, 191, 251), 1)

            # 3. Identificación de PELIGRO (ROJO)
            if self.risk_detected:
                # Efecto visual de alerta
                overlay = frame.copy()
                cv2.rectangle(overlay, (0,0), (w,h), (68, 68, 239), -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
                
                cv2.rectangle(frame, (w//2-150, h//2-50), (w//2+150, h//2+50), (68, 68, 239), cv2.FILLED)
                cv2.putText(frame, "RIESGO CRITICO", (w//2-120, h//2+10), 1, 2, (255, 255, 255), 3)

            # Conversión de Imagen para la UI
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            ctk_img = ctk.CTkImage(img, size=(850, 550))
            
            try:
                self.video_lbl.configure(image=ctk_img)
                self.video_lbl.image = ctk_img
            except: break

    # --- SECCIÓN 4: BLOCKCHAIN Y EVENTOS ---
    def register_event(self, event_type):
        ts = datetime.now().strftime("%H:%M:%S")
        prev_hash = self.blockchain[-1]['hash'] if self.blockchain else "0"*64
        
        # Generar Hash SHA-256
        raw_data = f"{ts}{event_type}{self.current_user}{prev_hash}"
        new_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        
        block = {"ts": ts, "event": event_type, "user": self.current_user, "hash": new_hash}
        self.blockchain.append(block)
        
        # Actualizar Ledger en UI
        if hasattr(self, 'ledger_view'):
            entry = f"[{ts}] {event_type}\nUSER: {self.current_user}\nHASH: {new_hash[:16]}...\n\n"
            self.ledger_view.insert("0.0", entry)

    def simulate_danger(self):
        self.risk_detected = True
        self.register_event("DANGER_LOG_EVENT")
        # El riesgo se limpia automáticamente tras 4 segundos
        self.after(4000, self.clear_danger)

    def clear_danger(self):
        self.risk_detected = False
        self.register_event("SAFETY_RESTORED")

if __name__ == "__main__":
    app = IWCORE_App()
    app.mainloop()
