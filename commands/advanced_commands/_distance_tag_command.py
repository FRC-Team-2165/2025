from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from wpimath.geometry import Translation2d

#TODO finish distance tracking

class DistanceTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, LDC: LocationDataClientManager, tag_id: int, distance: float, deadband: float = 0.5, stop_on_lost: bool = True):
        super().__init__()

        self.subsystem = subsystem
        self.LDC = LDC
        self.target_id = tag_id
        self.distance = distance
        self.deadband = deadband
        self.stop_on_lost = stop_on_lost

        self.target: Location = None
        self.has_target = False

        self.start_pos = Translation2d()

        self.addRequirements(self.subsystem)
    
    def initialize(self):
        self.LDC.startRequest()
        self.start_pos = self.subsystem.getPosition()
    
    def execute(self):
        tag_list: list[Location] = self.LDC.getData()
        for t in tag_list:
            if t.id_num == self.target_id:
                target = t
                self.has_target = True
            else:
                self.has_target = False
        
        if self.stop_on_lost and not self.has_target:
            self.subsystem.stop()
        else:
            pos = self.subsystem.getPosition()
            diff = Translation2d()
            diff.x = max(pos.x, self.start_pos.x) - min(pos.x, self.start_pos.x)
            diff.y = max(pos.y, self.start_pos.y) - min(pos.y, self.start_pos.y)

            # if 
    
    def end(self, interrupted):
        self.LDC.stopRequest()
        self.subsystem.stop()
    
    def isFinished(self):
        return super().isFinished()