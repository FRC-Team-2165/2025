from commands2 import Command
from subsystems import GrabberSubsystem, SlideSubsystem
from wpilib import Timer

class BirdCatchCommand(Command):
    def __init__(self, subsystem: GrabberSubsystem, slide: SlideSubsystem):
        super().__init__()

        self.subsystem = subsystem
        self.slide = slide

        self.grab_timer = Timer()

        self.grab_delay = 1.5
        self.move_delay = 1

        self.addRequirements(subsystem)
    
    def initialize(self):
        self.slide.setToDump()
        self.subsystem.openGrabber()
        self.subsystem.extendBird()
        self.grab_timer.reset()
        self.grab_timer.start()

    def execute(self):
        if self.grab_timer.hasElapsed(self.move_delay):
            # self.subsystem.grabber_angle = self.subsystem.upper_limit_val_open
            self.subsystem.grabber_angle = 105

    def end(self, interrupted):
        # self.subsystem.closeGrabber()
        self.subsystem.retractBird()
        self.grab_timer.stop()
        self.grab_timer.reset()
        self.subsystem.grabber_angle = self.subsystem.presets.STORE

    def isFinished(self):
        if self.grab_timer.hasElapsed(self.move_delay + self.grab_delay):
            return True