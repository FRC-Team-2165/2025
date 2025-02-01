from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
import math

class WatchTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, LDC: LocationDataClientManager, tag_id: int):
        super().__init__()

        self.subsystem = subsystem
        self.LDC = LDC
        self.target_id = tag_id

        self.addRequirements(self.subsystem)

        self.target = None
    
    def initialize(self):
        self.LDC.startRequest()
    
    def execute(self):
        tag_list: list[Location] = self.LDC.getData()
        for t in tag_list:
            if t.id_num == self.target_id:
                self.target = t

        if self.target and self.target.y != 0:
            angle = math.degrees(math.atan(abs(self.target.x) / self.target.y))
            rotate = (angle / 90) * self.subsystem.speed_modifier

            if angle > 5:
                self.subsystem.drive(0, 0, rotate, True)

    
    def end(self, interrupted):
        self.LDC.stopRequest()
    
    def isFinished(self):
        return super().isFinished()