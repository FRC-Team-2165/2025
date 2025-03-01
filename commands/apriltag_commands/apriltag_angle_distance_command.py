from commands2 import Command
from subsystems import DriveSubsystem
from components import TargetTracker, Position, LocationDataClientManager, Location
from math import degrees, atan

class ApriltagAngleCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int, distance: float, distance_deadband: float, angle: float, angle_deadband: float):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        start_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
        self.tracker = TargetTracker(start_pos)

        self.has_target = False

        self.distance = distance
        self.distance_deadband = distance_deadband
        self.angle = angle
        self.angle_deadband = angle_deadband

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
                    target_pos = Position(i.x, i.y + self.distance, angle = degrees(atan(i.x/i.y)) + self.angle)
                    self.tracker.updateTargetPosition(target_pos)
                    break
        
        if self.has_target:
            current_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
            self.tracker.updateCurrentPosition(current_pos)
            
            x_speed = 0
            y_speed = 0
            rot_speed = 0

            relative_pos = self.tracker.getTargetRelativePosition()
            if relative_pos.x > self.distance_deadband:
                x_speed = -0.5
            elif relative_pos.x < -self.distance_deadband:
                x_speed = 0.5
            if  relative_pos.y > self.distance_deadband:
                y_speed = 0.5
            elif relative_pos.y < -self.distance_deadband:
                y_speed = -0.5
            if relative_pos.angle > self.angle_deadband:
                rot_speed = -0.5
            elif relative_pos.angle < -self.angle_deadband:
                rot_speed = 0.5
            
            self.subsystem.drive(x_speed, y_speed, rot_speed)
        else:
            self.subsystem.stop()
    
    def end(self, interrupted):
        self.subsystem.stop()
    
    def isFinished(self):
        return super().isFinished()