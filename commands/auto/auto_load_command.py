from commands2 import Command
from subsystems import SlideSubsystem

class AutoLoadCommand(Command):
    def __init__(self, subsystem: SlideSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)

    
    def initialize(self):
        self.subsystem.setToLoad()
    

    def execute(self):
        return super().execute()
    

    def end(self, interrupted):
        return super().end(interrupted)
    

    def isFinished(self):
        return True