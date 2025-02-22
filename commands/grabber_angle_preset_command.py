from commands2 import Command
from subsystems import GrabberSubsystem

class GrabberAnglePresetCommand(Command):
    def __init__(self, subsystem: GrabberSubsystem, angle: float):
        super().__init__()

        self.subsystem = subsystem
        self.angle = angle
        self.addRequirements(subsystem)
    
    def initialize(self):
        self.subsystem.grabber_angle = self.angle
    
    def execute(self):
        return super().execute()
    
    def end(self, interrupted):
        return super().end(interrupted)

    def isFinished(self):
        return True