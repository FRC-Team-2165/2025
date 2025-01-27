from commands2 import Command
from subsystems import PickerSubsystem

class RunPickerCommand(Command):
    def __init__(self, subsystem: PickerSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.subsystem.startMotor()

    def execute(self):
        if self.subsystem.hasObject():
            self.subsystem.stopMotor()
        else:
            self.subsystem.startMotor()

    def end(self, interrupted):
        self.subsystem.stopMotor()

    def isFinished(self):
        return super().isFinished()