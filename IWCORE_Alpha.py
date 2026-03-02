import customtkinter as ctk
import cv2
import hashlib
import threading
from PIL import Image, ImageTk
from datetime import datetime
import tkinter.messagebox as messagebox

# --- CONFIGURATION & BRANDING ---
COLOR_BG = "#020617"
COLOR_BLUE = "#3b82f6"   # Objects/Tools
COLOR_GOLD = "#fbbf24"   # Locations/Zones
COLOR_RED = "#ef4444"    # Hazards/Risks
COLOR_SAFE = "#10b981"   # Success/Safe

class IWCORE_SST(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IWCORE™ | Workforce Safety & Health OS")
        self.geometry("1300x850")
        self.configure(fg_color=COLOR_BG)

        # --- DATABASE & WORKER STATE ---
        self.worker_profile = {
            "id": "",
            "name": "",
            "ppe": {
                "Helmet": {"status": False, "info": "Impact protection. Use chin strap."},
                "Gloves": {"status": False, "info": "Electrical/Cut resistance. Check for holes."},
                "Harness": {"status": False, "info": "Fall arrest. Required above 1.8m."}
            },
            "height_mode": "LOW" # Simulated sensor: LOW or HIGH
        }
        self.is_camera_on = False
        self.show_registration()

    # --- SECTION 1: REGISTRATION & AUTH ---
    def show_registration(self):
        self.reg_frame = ctk.CTkFrame(self, width=450, height=600, fg_color="#0f172a", corner_radius=25)
        self.reg_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.reg_frame, text="IWCORE REGISTER", font=("Orbitron", 26, "bold"), text_color=COLOR_BLUE).pack(pady=(40, 20))
        
        self.name_in = ctk.CTkEntry(self.reg_frame, placeholder_text="FULL NAME", width=300, height=45)
        self.name_in.pack(pady=10)
        
        self.id_in = ctk.CTkEntry(self.reg_frame, placeholder_text="WORKER_ID", width=300, height=45)
        self.id_in.pack(pady=10)

        ctk.CTkButton(self.reg_frame, text="REGISTER & SIGN IN", fg_color=COLOR_BLUE, 
                      command=self.handle_auth, height=45, width=300, font=("Orbitron", 12)).pack(pady=30)

    def handle_auth(self):
        if len(self.name_in.get()) > 3 and len(self.id_in.get()) > 3:
            self.worker_profile["name"] = self.name_in.get()
            self.worker_profile["id"] = self.id_in.get()
            self.reg_frame.destroy()
            self.setup_main_ui()
        else:
            messagebox.showerror("Error", "Please fill all fields correctly.")

    # --- SECTION 2: MAIN CONTROL PANEL ---
    def setup_main_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Navigation Bar
        self.nav = ctk.CTkFrame(self, width=80, fg_color="#000", corner_radius=0)
        self.nav.grid(row=0, column=0, sticky="nsew")

        self.add_nav_icon("👤", self.show_profile_page, 40)
        self.add_nav_icon("📷", self.show_safety_cam, 120)
        self.add_nav_icon("🤖", self.show_safebot, 200)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        self.show_profile_page()

    def add_nav_icon(self, icon, cmd, y):
        btn = ctk.CTkButton(self.nav, text=icon, width=60, height=60, fg_color="transparent", 
                            hover_color="#1e293b", font=("Arial", 28), command=cmd)
        btn.place(x=10, y=y)

    # --- MODULE: PROFILE & EQUIPMENT (PPE) ---
    def show_profile_page(self):
        self.clear_content()
        self.is_camera_on = False
        
        header = ctk.CTkLabel(self.content, text=f"OPERATOR: {self.worker_profile['name']}", font=("Orbitron", 22), text_color=COLOR_BLUE)
        header.pack(pady=(0, 20), anchor="w")

        # PPE Checkbox Section
        ctk.CTkLabel(self.content, text="EQUIPMENT VERIFICATION (PPE)", font=("Arial", 14, "bold")).pack(anchor="w")
        
        self.ppe_frame = ctk.CTkFrame(self.content, fg_color="#0f172a", border_width=1, border_color="#1e293b")
        self.ppe_frame.pack(fill="x", pady=10)

        for item in self.worker_profile["ppe"]:
            f = ctk.CTkFrame(self.ppe_frame, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=10)
            
            check = ctk.CTkCheckBox(f, text=item, font=("Arial", 13), 
                                    command=lambda i=item: self.toggle_ppe(i))
            if self.worker_profile["ppe"][item]["status"]: check.select()
            check.pack(side="left")

            ctk.CTkButton(f, text="Usage & Benefits", width=120, height=24, fg_color="#334155",
                          command=lambda i=item: self.show_ppe_manual(i)).pack(side="right")

    def toggle_ppe(self, item):
        self.worker_profile["ppe"][item]["status"] = not self.worker_profile["ppe"][item]["status"]

    def show_ppe_manual(self, item):
        info = self.worker_profile["ppe"][item]["info"]
        messagebox.showinfo(f"{item} Manual", f"{info}\n\nWARNING: Do not use mobile phones while handling equipment.")

    # --- MODULE: SAFETY CAMERA (SST VISION) ---
    def show_safety_cam(self):
        # SECURITY RESTRICTION: Check if Harness is on for High Altitude
        if self.worker_profile["height_mode"] == "HIGH" and not self.worker_profile["ppe"]["Harness"]["status"]:
            messagebox.showerror("BLOCKADE", "DANGER: High altitude detected. Harness NOT equipped. Camera and tools locked.")
            return

        self.clear_content()
        self.is_camera_on = True
        
        self.cam_display = ctk.CTkLabel(self.content, text="")
        self.cam_display.pack(expand=True, fill="both")

        self.cap = cv2.VideoCapture(0)
        threading.Thread(target=self.run_vision, daemon=True).start()

    def run_vision(self):
        while self.is_camera_on:
            ret, frame = self.cap.read()
            if ret:
                # 1. CHROMATIC HUD LOGIC
                # Object (Blue)
                cv2.rectangle(frame, (150, 150), (350, 400), (246, 130, 59), 2)
                cv2.putText(frame, "OBJ: DRILL_UNIT", (150, 140), 1, 1, (246, 130, 59), 2)

                # Location (Gold)
                cv2.putText(frame, "LOC: SCAFFOLD_LEVEL_2", (20, 50), 1, 1.2, (36, 191, 251), 2)

                # Risk/Tip (Dynamic SST Tip)
                cv2.rectangle(frame, (0, 430), (640, 480), (0,0,0), -1)
                cv2.putText(frame, "SST TIP: Keep 3 points of contact on ladder.", (50, 460), 1, 1, (255,255,255), 1)

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                ctk_img = ctk.CTkImage(img, size=(800, 500))
                self.cam_display.configure(image=ctk_img)
            time.sleep(0.01)

    # --- MODULE: SAFE_BOT AGENT ---
    def show_safebot(self):
        self.clear_content()
        self.is_camera_on = False
        
        ctk.CTkLabel(self.content, text="🤖 SAFEBOT: AUTONOMOUS AGENT", font=("Orbitron", 20), text_color=COLOR_BLUE).pack(pady=10)
        
        chat = ctk.CTkTextbox(self.content, width=700, height=350, font=("Arial", 14))
        chat.pack(pady=10)
        
        msg = f"Hello {self.worker_profile['name']},\n\n"
        msg += "SYSTEM DIAGNOSIS:\n"
        msg += f"- Altitude: {self.worker_profile['height_mode']}\n"
        msg += "- Insurance: ACTIVE (SCTR Coverage for Family included)\n\n"
        msg += "TRAINING RECO: Since you are working at height, please complete the 'Fall Protection' module. Completion grants you 50 Safety Points."
        
        chat.insert("0.0", msg)
        ctk.CTkButton(self.content, text="START TRAINING MODULE", fg_color=COLOR_SAFE).pack(pady=20)

    def clear_content(self):
        for w in self.content.winfo_children(): w.destroy()

if __name__ == "__main__":
    app = IWCORE_SST()
    app.mainloop()
