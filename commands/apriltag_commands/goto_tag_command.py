from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from wpimath.geometry import Translation2d
from math import degrees, atan


class GotoTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_ids: int|list[int], drive_proportional: float = 1, rotation_proportional: float = 1, x_offset: float = 0, y_offset: float = 0, distance_deadband: float = 0.05, rotation_deadband: float = 1):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        if target_ids is int:
            target_ids = [target_ids]
        self.target_ids = target_ids

        self.drive_proportional = drive_proportional
        self.rotation_proportional = rotation_proportional
        self.distance_deadband = distance_deadband
        self.rotation_deadband = rotation_deadband
        self.has_target = False

        self.x_offset = x_offset
        self.y_offset = y_offset
        self.target_pos = Translation2d()
        self.target_angle = 0

        self.x_speed = 0
        self.y_speed = 0
        self.rot_speed = 0

        self.addRequirements(subsystem)
    

    def initialize(self):
        self.subsystem.resetPosition()
        self.has_target = False
        self.stream.startRequest()
    

    def execute(self):
        data = self.stream.getData()
        self.has_target = False

        valid_targets = []

        for i in data:
            i: Location
            if i.id_num in self.target_ids:
                self.has_target = True
                
                valid_targets.append(i)
        
        if self.has_target:
            positions = []
            for i in valid_targets:
                positions.append(Translation2d(i.x, i.y))
            self.target_pos =  Translation2d().nearest(positions)
            target = valid_targets[positions.index(self.target_pos)]
            self.target_angle = (degrees(atan((target.x) / (target.y))) + self.subsystem.getAngle()) % 360
            print("got target")
        
        if self.has_target:
            x_speed = 0
            x_error = self.target_pos.x - self.x_offset
            if abs(x_error) < self.distance_deadband:
                pass
            else:
                speed = x_error * self.drive_proportional * 1.5
                x_speed = speed + 0.1 * (x_error / abs(x_error))
            self.x_speed = x_speed

            y_speed = 0
            y_error = self.target_pos.y - self.y_offset
            if abs(y_error) < self.distance_deadband:
                pass
            else:
                speed = y_error * self.drive_proportional
                y_speed = speed + 0.1 * (y_error / abs(y_error))
            self.y_speed = y_speed

            rot_speed = 0
            rot_error = self.target_angle
            if abs(y_error) < self.rotation_deadband:
                pass
            else:
                speed = rot_error * self.rotation_proportional
                rot_speed = speed + 0.1 * (rot_error / abs(rot_error))
            self.rot_speed = rot_speed
            print(rot_error, rot_speed)
        else:
            self.x_speed = 0
            self.y_speed = 0
            self.rot_speed = 0
        self.subsystem.drive(self.x_speed, self.y_speed, self.rot_speed, False)
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()