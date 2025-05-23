from commands2 import Command
from subsystems import GrabberSubsystem

class AutoGrabCommand(Command):
    def __init__(self, subsystem: GrabberSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)

    
    def initialize(self):
        self.subsystem.closeGrabber()
    

    def execute(self):
        return super().execute()
    

    def end(self, interrupted):
        return super().end(interrupted)
    

    def isFinished(self):
        return True