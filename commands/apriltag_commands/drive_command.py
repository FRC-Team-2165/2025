from commands2 import Command
from subsystems import DriveSubsystem


class DriveCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, x_speed: float = 0, y_speed: float = 0):
        super().__init__()

        self.subsystem = subsystem

        self.x_speed = x_speed
        self.y_speed = y_speed

        self.addRequirements(subsystem)
    
    
    def initialize(self):
        return super().initialize()


    def execute(self):
        self.subsystem.drive(self.x_speed, self.y_speed, 0, False)
    

    def end(self, interrupted):
        self.subsystem.stop()
    

    def isFinished(self):
        return super().isFinished()