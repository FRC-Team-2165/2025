from commands2 import Command
from subsystems import DriveSubsystem

class ResetDriveCommand(Command):
    def __init__(self, subsystem: DriveSubsystem):
        self.subsystem = subsystem

    def initialize(self):
        self.subsystem.resetAngle()
    
    def execute(self):
        return super().execute()
    
    def end(self, interrupted: bool):
        return super().end(interrupted)
    
    def isFinished(self) -> bool:
        return True