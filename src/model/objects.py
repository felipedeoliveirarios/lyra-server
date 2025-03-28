from typing import Optional, Dict

class CargoItem:
    def __init__(self, Name: str, Count: int, Stolen: int, MissionID: Optional[int] = None, Name_Localised: Optional[str] = None):
        self.Name = Name
        self.Count = Count
        self.Stolen = Stolen
        self.MissionID = MissionID
        self.Name_Localised = Name_Localised

class Module:
    def __init__(self, Slot: str, Item: str, On: bool, Priority: int, Health: float, Value: Optional[int] = None,
                 AmmoInClip: Optional[int] = None, AmmoInHopper: Optional[int] = None, Engineering: Optional[Dict] = None):
        self.Slot = Slot
        self.Item = Item
        self.On = On
        self.Priority = Priority
        self.Health = Health
        self.Value = Value
        self.AmmoInClip = AmmoInClip
        self.AmmoInHopper = AmmoInHopper
        self.Engineering = Engineering

class Material:
    def __init__(self, Name: str, Count: int):
        self.Name = Name
        self.Count = Count

class Mission:
    def __init__(self, MissionID: int, Name: str, PassengerMission: bool, Expires: int):
        self.MissionID = MissionID
        self.Name = Name
        self.PassengerMission = PassengerMission
        self.Expires = Expires