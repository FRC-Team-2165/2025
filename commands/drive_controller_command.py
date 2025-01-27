from commands2 import Command
from subsystems import DriveSubsystem
import wpilib

class DriveControllerCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, controller: wpilib.XboxController):
        super().__init__()

        self.drive = subsystem
        self.controller = controller

        self.addRequirements(self.drive)

    def initialize(self):
        return super().initialize()

    def execute(self):
        drive_x = self.controller.getLeftX() * self.drive.speed_modifier
        drive_y = -self.controller.getLeftY() * self.drive.speed_modifier
        rotate = self.controller.getRightX() * self.drive.speed_modifier

        if self.controller.getRightTriggerAxis() > 0.5:
            self.drive.speed_modifier = 1
        else:
            self.drive.speed_modifier = 0.7

        # print(f"controller x: {drive_x}, controller y: {drive_y}, controller rotate: {rotate}")

        self.drive.drive(drive_x, drive_y, rotate, True)

    def end(self, interrupted: bool):
        return super().end(interrupted)
    
    def isFinished(self) -> bool:
        return False