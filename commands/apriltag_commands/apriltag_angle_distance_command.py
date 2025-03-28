from commands2 import Command
from subsystems import DriveSubsystem
from components import TargetTracker, Position, LocationDataClientManager, Location
from math import degrees, atan

class ApriltagAngleDistanceCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int,\
      move_distance: bool = False, move_angle: bool = False, distance_offset: float = 0, distance_deadband: float = 0.25, angle_offset: float = 0, angle_deadband: float = 5):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        start_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
        self.tracker = TargetTracker(start_pos)

        self.has_target = False
        self.target_data = Position()

        self.move_distance = move_distance
        self.move_angle = move_angle

        self.distance_offset = distance_offset
        self.distance_deadband = distance_deadband
        self.angle_offset = angle_offset
        self.angle_deadband = angle_deadband

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.stream.startRequest()
        self.subsystem.stop()
        self.has_target = False
        start_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
        self.tracker = TargetTracker(start_pos)

    def execute(self):
        if not self.has_target or True:
            data = self.stream.getData()
            self.has_target = False

            for i in data:
                i: Location
                if i.id_num == self.target_id:
                    self.has_target = True
                    # target_pos = Position(i.x, i.y + self.distance_offset, angle = degrees(atan(i.x/i.y)) + self.angle_offset)
                    # self.tracker.updateTargetPosition(target_pos)
                    self.target_data = degrees(atan(i.x/i.y)) + self.subsystem.getAngle()
                    break
        
        if self.has_target:
            current = self.subsystem.getAngle()
            target = self.target_data

            # rot_speed = 0
            # if current > target + self.angle_deadband:
            #     rot_speed = -0.25
            # elif current < target - self.angle_deadband:
            #     rot_speed = 0.25
            # self.subsystem.drive(0, 0, rot_speed)

            rot_speed = 0
            if abs(current - target) < self.angle_deadband:
                pass
            else:
                error = target - current
                rot_speed = error / abs(error) * 0.25
            self.subsystem.drive(0, 0, rot_speed)
        else:
            self.subsystem.stop()
        
        # if self.has_target and False:
        #     current_pos = Position(self.subsystem.getPosition().X(), self.subsystem.getPosition().Y(), angle= self.subsystem.getAngle())
        #     self.tracker.updateCurrentPosition(current_pos)
            
        #     x_speed = 0
        #     y_speed = 0
        #     rot_speed = 0

        #     relative_pos = self.tracker.getTargetRelativePosition()
        #     if self.move_distance:
        #         if relative_pos.x > self.distance_deadband:
        #             x_speed = -0.5
        #         elif relative_pos.x < -self.distance_deadband:
        #             x_speed = 0.5
        #         if  relative_pos.y > self.distance_deadband:
        #             y_speed = 0.5
        #         elif relative_pos.y < -self.distance_deadband:
        #             y_speed = -0.5
        #     if self.move_angle:
        #         if relative_pos.angle > self.angle_deadband:
        #             rot_speed = 0.25
        #         elif relative_pos.angle < -self.angle_deadband:
        #             rot_speed = -0.25
            
        #     self.subsystem.drive(x_speed, y_speed, rot_speed)
        # else:
        #     pass
        #     # self.subsystem.stop()
    
    def end(self, interrupted):
        self.stream.stopRequest()
        self.subsystem.stop()
    
    def isFinished(self):
        return super().isFinished()