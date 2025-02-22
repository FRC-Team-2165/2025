from commands2 import Command
from subsystems import PickerSubsystem

class IntakePickerCommand(Command):
    def __init__(self, subsystem: PickerSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.subsystem.startMotor()

    def execute(self):
        return super().execute()

    def end(self, interrupted):
        self.subsystem.stopMotor()

    def isFinished(self):
        if self.subsystem.hasObject():
            return True