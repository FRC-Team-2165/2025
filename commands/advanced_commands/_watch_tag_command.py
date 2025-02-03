from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
import math

class WatchTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, LDC: LocationDataClientManager, tag_id: int, deadband: float = 5, stop_on_lost: bool = True):
        super().__init__()

        self.subsystem = subsystem
        self.LDC = LDC
        self.target_id = tag_id
        self.deadband = deadband
        self.stop_on_lost = stop_on_lost

        self.target: Location = None
        self.has_target = False

        self.addRequirements(self.subsystem)
    
    def initialize(self):
        self.LDC.startRequest()
    
    def execute(self):
        tag_list: list[Location] = self.LDC.getData()
        for t in tag_list:
            if t.id_num == self.target_id:
                self.target = t
                self.has_target = True
            else:
                self.has_target = False
        
        if self.stop_on_lost and not self.has_target:
            self.subsystem.stop()
        else:
            relative_angle = math.degrees(math.atan(self.target.x / self.target.y))
            target_angle = self.subsystem.getAngle() + relative_angle

            angle = self.subsystem.getAngle()
            if angle < target_angle - self.deadband:
                self.subsystem.drive(0, 0, 0.5, True)
            elif angle > target_angle + self.deadband:
                self.subsystem.drive(0, 0, -0.5, True)
            else:
                self.subsystem.stop()
            
    def end(self, interrupted):
        self.LDC.stopRequest()
        self.subsystem.stop()
    
    def isFinished(self):
        return super().isFinished()