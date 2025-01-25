from commands2 import Command
from subsystems import GrabberSubsystem
from wpimath import applyDeadband
from wpilib import XboxController
import wpilib

class GrabberAngleControllerCommand(Command):
    def __init__(self, subsystem: GrabberSubsystem, controller: XboxController):
        super().__init__()
        self.controller = controller
        self.subsystem = subsystem
        self.addRequirements(subsystem)
    
    def execute(self):
        speed = -self.controller.getRightY()
        speed = applyDeadband(speed, 0.1)
        self.subsystem.move(speed)