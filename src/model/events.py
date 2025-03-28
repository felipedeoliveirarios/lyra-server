from objects import *
from enums import *
from typing import List, Dict, Optional

class Event:
    def __init__(self, timestamp: str, event: EventType):
        self.timestamp = timestamp
        self.event = event

class CargoEvent(Event):
    def __init__(self, timestamp: str, Vessel: str, Inventory: List[CargoItem]):
        super().__init__(timestamp, EventType.CARGO)
        self.Vessel = Vessel
        self.Inventory = Inventory

class ClearSavedGameEvent(Event):
    def __init__(self, timestamp: str, Name: str, FID: str):
        super().__init__(timestamp, EventType.CLEARSAVEDGAME)
        self.Name = Name
        self.FID = FID
        
class LoadoutEvent(Event):
    def __init__(self, timestamp: str, Ship: str, ShipID: int, ShipName: Optional[str], ShipIdent: Optional[str],
                 HullValue: Optional[int], ModulesValue: Optional[int], HullHealth: float, UnladenMass: float,
                 FuelCapacity: Dict[str, float], CargoCapacity: int, MaxJumpRange: float, Rebuy: int, Hot: Optional[bool],
                 Modules: List[Module]):
        super().__init__(timestamp, EventType.LOADOUT)
        self.Ship = Ship
        self.ShipID = ShipID
        self.ShipName = ShipName
        self.ShipIdent = ShipIdent
        self.HullValue = HullValue
        self.ModulesValue = ModulesValue
        self.HullHealth = HullHealth
        self.UnladenMass = UnladenMass
        self.FuelCapacity = FuelCapacity
        self.CargoCapacity = CargoCapacity
        self.MaxJumpRange = MaxJumpRange
        self.Rebuy = Rebuy
        self.Hot = Hot
        self.Modules = Modules

class MaterialsEvent(Event):
    def __init__(self, timestamp: str, Raw: List[Material], Manufactured: List[Material], Encoded: List[Material]):
        super().__init__(timestamp, EventType.MATERIALS)
        self.Raw = Raw
        self.Manufactured = Manufactured
        self.Encoded = Encoded

class MissionsEvent(Event):
    def __init__(self, timestamp: str, Active: List[Mission], Failed: List[Mission], Complete: List[Mission]):
        super().__init__(timestamp, EventType.MISSIONS)
        self.Active = Active
        self.Failed = Failed
        self.Complete = Complete

class NewCommanderEvent(Event):
    def __init__(self, timestamp: str, Name: str, FID: str, Package: str):
        super().__init__(timestamp, EventType.NEWCOMMANDER)
        self.Name = Name
        self.FID = FID
        self.Package = Package

class LoadGameEvent(Event):
    def __init__(self, timestamp: str, Commander: str, FID: str, Horizons: bool, Odyssey: bool, Ship: str, ShipID: int,
                 StartLanded: Optional[bool] = None, StartDead: Optional[bool] = None, GameMode: str = "Open",
                 Group: Optional[str] = None, Credits: int = 0, Loan: int = 0, ShipName: Optional[str] = None,
                 ShipIdent: Optional[str] = None, FuelLevel: float = 0.0, FuelCapacity: float = 0.0):
        super().__init__(timestamp, EventType.LOADGAME)
        self.Commander = Commander
        self.FID = FID
        self.Horizons = Horizons
        self.Odyssey = Odyssey
        self.Ship = Ship
        self.ShipID = ShipID
        self.StartLanded = StartLanded
        self.StartDead = StartDead
        self.GameMode = GameMode
        self.Group = Group
        self.Credits = Credits
        self.Loan = Loan
        self.ShipName = ShipName
        self.ShipIdent = ShipIdent
        self.FuelLevel = FuelLevel
        self.FuelCapacity = FuelCapacity