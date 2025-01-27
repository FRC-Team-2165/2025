from commands2 import Command
from subsystems import PickerSubsystem

class TogglePickerCommand(Command):
    def __init__(self, subsystem: PickerSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.subsystem.toggleIntakePosition()
    
    def execute(self):
        return super().execute()
    
    def end(self, interrupted):
        return super().end(interrupted)
    
    def isFinished(self):
        return True