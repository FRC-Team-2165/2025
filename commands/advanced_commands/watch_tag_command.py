from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location,\
  TargetTracker, Position
import math
from wpimath.geometry import Translation2d

class WatchTagCommand(Command):
    def __init__(self, drive: DriveSubsystem, LDC: LocationDataClientManager, target_id: int, deadband: float = 5, stop_on_lost: bool = True):
        super().__init__()

        self.drive = drive
        self.LDC = LDC
        self.target_id = target_id
        self.deadband = deadband
        self.stop_on_lost = stop_on_lost

        self.tracker = TargetTracker(Position())

        self.has_target = False

        self.addRequirements(self.drive)
    
    def initialize(self):
        pos = self.drive.getPosition()
        angle = self.drive.getAngle()
        position = Position(pos.X(), pos.Y(), pos.Z(), angle)
        self.tracker = TargetTracker(position)

        self.LDC.startRequest()

    def execute(self):
        tag_list: list[Location] = self.LDC.getData()
        for t in tag_list:
            if t.id_num == self.target_id:
                self.has_target = True

                target = Position(t.x, t.y, t.z, math.degrees(math.atan(t.x/t.y)))
                self.tracker.updateTargetPosition(target)
            else:
                self.has_target = False
        
        
        pos = self.drive.getPosition()
        angle = self.drive.getAngle()
        current = Position(pos.X(), pos.Y(), pos.Z(), angle)
        self.tracker.updateCurrentPosition(current)

        if self.stop_on_lost and not self.has_target:
            self.drive.stop()
        else:
            relative = self.tracker.getTargetRelativePosition()
            if abs(relative.angle) > self.deadband:
                speed = 0.5 * (abs(relative.angle) / relative.angle)
                self.drive.drive(0, 0, speed, True)
            else:
                self.drive.stop()
    
    def end(self, interrupted):
        self.drive.stop()
        self.LDC.stopRequest()
    
    def isFinished(self):
        return super().isFinished()