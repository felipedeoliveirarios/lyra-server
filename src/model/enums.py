from enum import StrEnum

class EventType(StrEnum):
    CARGO = "Cargo"
    CLEARSAVEDGAME = "ClearSavedGame"
    COMMANDER = "Commander"
    LOADOUT = "Loadout"
    MATERIALS = "Materials"
    MISSIONS = "Missions"
    NEWCOMMANDER = "NewCommander"
    LOADGAME = "LoadGame"
    
class Vessel(StrEnum):
    SHIP = "Ship"
    SRV = "SRV"
    FIGHTER = "Fighter"
    UNKNOWN = "Unknown"