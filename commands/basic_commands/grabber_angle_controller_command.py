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

        self.last_input = 0
    
    def initialize(self):
        return super().initialize()
    
    def execute(self):
        speed = -self.controller.getRightY()
        speed = applyDeadband(speed, 0.1)

        if speed != 0:
            self.subsystem.move(speed)
        elif self.last_input == 0:
            pass
        elif self.last_input != 0:
            self.subsystem.target_angle = self.subsystem.grabber_angle
        
        self.last_input = speed
    
    def end(self, interrupted):
        return super().end(interrupted)
    
    def isFinished(self):
        return super().isFinished()