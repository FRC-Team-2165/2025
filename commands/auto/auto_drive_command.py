from commands2 import Command
from subsystems import DriveSubsystem
from wpimath.geometry import Translation2d

class AutoDriveCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, move_speed = 0.5, turn_speed = 0.2,  x_dist: float = 0, y_dist: float = 0, angle: float = 0, reset_angle: bool = False, angle_deadband: float = 5):
        super().__init__()

        self.subsystem = subsystem

        self.move_speed = move_speed
        self.turn_speed = turn_speed

        self.x_dist = x_dist
        self.y_dist = y_dist
        self.target_angle = 0

        self.angle_offset = angle
        self.reset_angle = reset_angle
        self.angle_deadband = angle_deadband

        self.x_met = False
        self.y_met = False
        self.angle_met = False

        self.addRequirements(subsystem)
    

    def initialize(self):
        self.subsystem.resetPosition()

        if self.reset_angle:
            self.subsystem.resetAngle()

        self.target_angle = self.subsystem.getAngle() + self.angle_offset

        self.x_met = False
        self.y_met = False
        self.angle_met = False
    

    def execute(self):
        pos = self.subsystem.getPosition()
        angle = self.subsystem.getAngle()

        if abs(pos.X()) > abs(self.y_dist):
            self.y_met = True
        if abs(pos.Y()) > abs(self.x_dist):
            self.x_met = True
        if abs(angle - self.target_angle) < self.angle_deadband:
            self.angle_met = True
        else:
            self.angle_met = False

        x_speed = 0
        if not self.x_met:
            x_err = self.x_dist - pos.X()
            if x_err != 0:
                x_speed = (x_err / abs(x_err)) * self.move_speed
        y_speed = 0
        if not self.y_met:
            y_err = self.y_dist - pos.Y()
            if y_err != 0:
                y_speed = (y_err / abs(y_err)) * self.move_speed
        rot_speed = 0
        if not self.angle_met:
            angle_err = self.target_angle - angle
            if angle_err != 0:
                rot_speed = (angle_err / abs(angle_err)) * self.turn_speed
        self.subsystem.drive(x_speed, y_speed, rot_speed)
            
    

    def end(self, interrupted):
        self.subsystem.stop()
    

    def isFinished(self):
        if self.x_met and self.y_met and self.angle_met:
            return True