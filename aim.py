import pymem
import pymem.process
import keyboard
import requests
from math import sqrt, pi, atan

try:    
    hazedumper = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()
except (ValueError, requests.RequestException):
    exit("[-] Failed to fetch the latests offsets from hazedumper!")

pm = pymem.Pymem("csgo.exe")

client = pymem.process.module_from_name(pm.process_handle,"client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle,"engine.dll").lpBaseOfDll

aimfov = 120

def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX < -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < 180:
        viewAngleY += 360
    return viewAngleX, viewAngleY

def checkAngles(x,y):

    if x > 89:
        return False
    elif x < -89:
        return False
    elif y > 360:
        return False
    elif y < -360:
        return False
    else:
        return True
    

def nanChecker(first, second):
    if math.isnan(first) or math.isnan(second):
        return False
    else:
        return True
    
def calcDistance(current_x, current_y, new_x, new_y):
    distancex = new_x - current_x
    if distancex < -89:
        distancex += 360
    elif distancex > 89:
        distancex -= 360
    if distancex < 0.0:
        distancex = -distancex

def calcAngle(localpos1,localpos2,localpos3,enemypos1,enemypos2,enemypos3):

    try:
        delta_x = localpos1 - enemypos1
        delta_y = localpos2 - enemypos2
        delta_z = localpos3 - enemypos3
        hyp = sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
        x = atan(delta_z/hyp) *180 /pi
        y = atan(delta_y/delta_x) * 180 / pi
        if delta_x > 0.0:
            y += 180.0
        return x,y
    except:
        pass

def main():
    player = pm.read_int(client + hazedumper["signatures"]["dwLocalPlayer"])
    engine_pointer = pm.read_int(engine + hazedumper["signatures"]["dwClientState"])
    localTeam = pm.read_int(player + hazedumper["netvars"]["m_iTeamNum"])

    while True:
        target = None
        olddistx = 111111111111
        olddisty = 111111111111

        for i in range(1,32):
            entity = pm.read_int(client + hazedumper["signatures"]["dwEntityState"] + i * 0x10)

            if entity:
                try:
                    entity_team_id = pm.read_int(entity + hazedumper["netvars"]["m_iTeamNum"])
                    entity_hp = pm.read_int(entity + hazedumper["netvars"]["m_iHealth"])
                    entity_dormant = pm.read_int(entity + hazedumper["netvars"]["m_bDormant"])
                except:
                    print("Finds Players Info Once")

                if localTeam != entity_team_id and entity_hp > 0:
                    