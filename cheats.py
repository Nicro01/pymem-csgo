import threading
import requests
import win32api
import time
import math
import pymem
import pymem.process
import ctypes
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

try:    
    hazedumper = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()
except (ValueError, requests.RequestException):
    exit("[-] Failed to fetch the latests offsets from hazedumper!")

try:
    csgo = pymem.Pymem("csgo.exe")
    module_base = pymem.process.module_from_name(csgo.process_handle, "client.dll").lpBaseOfDll

except:
    text = tk.Text(root, height=10, font=("Arial", 15))
    
    root.title("CSGO Bagulho")

    root.geometry("300x200")

    root.config(bg="#333")
    root.resizable(False, False)

    
    title_label = tk.Label(root, text="CSGO Bagulho", font=("Arial", 30), fg="#fff", bg="#333")
    title_label.pack(pady=20)
    
    
    title_labelErro = tk.Label(root, text="csgo.exe Não foi encontrado", font=("Arial", 15), fg="#fff", bg="#333")
    title_labelErro.pack(pady=20)

    root.mainloop()

if not module_base:
    exit("[-] Failed to load module: 'client.dll'")

class CEntity:

    def __init__(self, address) -> None:

        self.address = address

    def player_base(self):
        return csgo.read_int(self.address + hazedumper["signatures"]["dwEntityList"])

    def get_health(self) -> int:
        return csgo.read_int(self.address + hazedumper["netvars"]["m_iHealth"])
    
    def is_alive(self) -> bool:

        return self.get_health() > 0

    def is_dormant(self) -> bool:

        return csgo.read_bool(self.address + hazedumper["signatures"]["m_bDormant"])
    
    def get_team_number(self) -> int:
        
        return csgo.read_int(self.address + hazedumper["netvars"]["m_iTeamNum"])
    
    def spot(self) -> None:
       
        csgo.write_bool(self.address + hazedumper["netvars"]["m_bSpotted"], True)

    def is_defusing(self) -> bool:
        
        return csgo.read_bool(self.address + hazedumper["netvars"]["m_bIsDefusing"])

    def glow(self, r: float, g:float, b: float, a:float = 1) -> None:
        
        glow_manager = csgo.read_int(module_base + hazedumper["signatures"]["dwGlowObjectManager"])
        entity_glow = csgo.read_int(self.address + hazedumper["netvars"]["m_iGlowIndex"])
        entity = glow_manager + entity_glow * 0x38
        if entity +  0x8 < 0:
            return
        csgo.write_float(entity +  0x8, float(r))  # R
        csgo.write_float(entity + 0xC, float(g))   # G
        csgo.write_float(entity + 0x10, float(b))  # B
        csgo.write_float(entity + 0x14, float(a))  
        csgo.write_bool(entity + 0x28, True)       

    def glow_by_health(self) -> None:
       
        entity_health = self.get_health()
        if entity_health < 30:
            self.glow(1, 0, 0) 
        elif entity_health < 50:
            self.glow(1, 1, 0) 
        else:
            self.glow(0, 1, 0) 

class LocalPlayer(CEntity):
   
    def update(self):
       
        self.address = csgo.read_int(module_base + hazedumper["signatures"]["dwLocalPlayer"])

def toggle_wall():
    global wall_on
    wall_on = not wall_on
    if wall_on:
        
        threading.Thread(target=wall).start()
    else:
        
        global stop_wall
        stop_wall = True

def wall():
    localplayer = LocalPlayer(None)
    while wall_on == True:
        localplayer.update()
        if win32api.GetKeyState(117): # Kill switch (F6)
            break
        while localplayer.address <= 0: 
            localplayer.update()
            time.sleep(1.5)
        for i in range(0, 32):
            if not localplayer.is_alive():
                break
            entity = csgo.read_int(module_base + hazedumper["signatures"]["dwEntityList"] + i * 0x10)
            if entity <= 0 or entity is None: 
                continue
            c_entity = CEntity(entity)
            if c_entity is None or not c_entity.is_alive() or c_entity.is_dormant(): 
                continue
            if c_entity.get_team_number() == localplayer.get_team_number():
                c_entity.glow(0, 0, 1) 
            elif c_entity.is_defusing():
                
                c_entity.glow(1, 0, 1)
            else:
                
                c_entity.glow_by_health()
            c_entity.spot()
        

stop_distance = tk.BooleanVar(value=False)

# Define global variables
pm = None
client = None
stop_aimbot = False


class LocalPlayer:
    def __init__(self, base):
        self.base = base
        self.team = 0
        self.health = 0
        self.head_pos = [0, 0, 0]

    def update(self):
        global pm
        self.team = pm.read_int(self.base + ENTITY_TEAM_OFFSET)
        self.health = pm.read_int(self.base + ENTITY_HEALTH_OFFSET)

        bone_matrix = pm.read_bytes(self.base + ENTITY_BONE_MATRIX_OFFSET, ENTITY_BONE_SIZE * 128)
        head_bone_offset = ENTITY_BONE_SIZE * ENTITY_HEAD_BONE_ID + 0xC
        self.head_pos = [
            pm.read_float(self.base + ENTITY_BONE_MATRIX_OFFSET + head_bone_offset),
            pm.read_float(self.base + ENTITY_BONE_MATRIX_OFFSET + head_bone_offset + 4),
            pm.read_float(self.base + ENTITY_BONE_MATRIX_OFFSET + head_bone_offset + 8)
        ]

    def distance_to(self, other):
        dx = self.head_pos[0] - other.head_pos[0]
        dy = self.head_pos[1] - other.head_pos[1]
        dz = self.head_pos[2] - other.head_pos[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)


def Aim():
    pass

wall_on = tk.BooleanVar(value=False)
distance_on = tk.BooleanVar(value=False)

def main() -> None:

    root.title("CSGO Bagulho")
    root.geometry("350x350")

    # Define colors
    bg_color = "#F5F5F5"
    button_color = "#E0E0E0"
    button_hover_color = "#CCCCCC"
    button_pressed_color = "#B0B0B0"

    # Define button font
    button_font = ("Roboto", 14)

    # Define button function
    def button_click(button_num):
        print("Button {} clicked".format(button_num))

    # Create style for buttons
    style = ttk.Style()

    # Configure style for Checkbutton
    style.configure("WallHack.TCheckbutton",
                    background=button_color,
                    foreground="#333",
                    font=button_font,
                    bordercolor="#333",
                    lightcolor="#E0E0E0",
                    darkcolor="#B0B0B0",
                    highlightcolor="#CCCCCC",
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    width=150,
                    anchor="center")

    # Configure style for Button
    style.configure("TButton",
                    background=button_color,
                    foreground="#333",
                    font=button_font,
                    bordercolor="#333",
                    lightcolor="#E0E0E0",
                    darkcolor="#B0B0B0",
                    highlightcolor="#CCCCCC",
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    width=150,
                    anchor="center")

    # Create menu frame
    menu_frame = tk.Frame(root, bg=bg_color, borderwidth=0, highlightthickness=0)

    title_label = tk.Label(root, text="CSGO Bagulho", font=("Arial", 30), fg="#fff", bg="#333")
    title_label.pack(pady=20)

    # Create and add buttons to menu frame
    button1 = tk.Checkbutton(menu_frame, text="WallHack", variable=wall_on, background=button_color,foreground="#333",font=button_font,highlightcolor="#CCCCCC",relief="flat",borderwidth=0,highlightthickness=0,width=150,anchor="center", command=toggle_wall)
    button1.pack(side="left", padx=10, pady=10)

    button2 = tk.Checkbutton(menu_frame, text="Distância", variable=distance_on, background=button_color,foreground="#333",font=button_font,highlightcolor="#CCCCCC",relief="flat",borderwidth=0,highlightthickness=0,width=150,anchor="center", command=toggle_aimbot)
    button2.pack(padx=10, pady=10)


    # Add menu frame to root window
    menu_frame.pack(side="top", fill="x")

    # Create footer frame
    footer_frame = tk.Frame(root, bg=bg_color, borderwidth=0, highlightthickness=0)

    # Create and add buttons to footer frame
    button3 = ttk.Button(footer_frame, text="Button 3", style="TButton", command=aimbot)
    button3.pack(side="left", padx=10, pady=10)


    # Add footer frame to root window
    footer_frame.pack(side="bottom", fill="x")

    # Run root window
    root.mainloop()



   
    

if __name__ == '__main__':
    print("[*] Started CSGO cheats")
    main()