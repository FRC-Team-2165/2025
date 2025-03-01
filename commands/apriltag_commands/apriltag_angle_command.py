from commands2 import Command
from subsystems import DriveSubsystem
from components import TargetTracker, Position, LocationDataClientManager, Location
from math import degrees, atan

class ApriltagAngleCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        start_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
        self.tracker = TargetTracker(start_pos)

        self.has_target = False

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.stream.startRequest()

    def execute(self):
        if not self.has_target:
            data = self.stream.getData()
            self.has_target = False
            for i in data:
                i: Location
                if i.id_num == self.target_id:
                    self.has_target = True
                    target_pos = Position(i.x, i.y + 2, angle = degrees(atan(i.x/i.y)))
                    self.tracker.updateTargetPosition(target_pos)
                    break
        
        if self.has_target:
            current_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
            self.tracker.updateCurrentPosition(current_pos)
            
            x_speed = 0
            y_speed = 0
            rot_speed = 0

            relative_pos = self.tracker.getTargetRelativePosition()
            if relative_pos.angle > 3:
                rot_speed = -0.5
            elif relative_pos.angle < -3:
                rot_speed = 0.5
            
            self.subsystem.drive(x_speed, y_speed, rot_speed)
        else:
            self.subsystem.stop()
    
    def end(self, interrupted):
        self.subsystem.stop()
    
    def isFinished(self):
        return super().isFinished()