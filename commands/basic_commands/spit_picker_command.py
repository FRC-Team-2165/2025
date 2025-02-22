from commands2 import Command
from subsystems import PickerSubsystem

class SpitPickerCommand(Command):
    def __init__(self, subsystem: PickerSubsystem):
        super().__init__()

        self.subsystem = subsystem

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.subsystem.startMotor(-1)

    def execute(self):
        return super().execute()

    def end(self, interrupted):
        self.subsystem.stopMotor()

    def isFinished(self):
        return super().isFinished()