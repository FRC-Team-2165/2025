from commands2 import Command
from subsystems import DriveSubsystem, GrabberSubsystem
from wpilib import Timer

class AlgaeFromCenterCommand(Command):
    def __init__(self, drive: DriveSubsystem, grabber: GrabberSubsystem):
        super().__init__()

        self.drive = drive
        self.grabber = grabber

        self.angle_timer = Timer()

        self.grabber_set = False

        self.addRequirements(drive, grabber)
    
    
    def initialize(self):
        self.drive.resetAngle()
        self.drive.resetPosition()

        self.grabber_opened = False

        self.grabber.grabber_angle = self.grabber.presets.BIRD

        self.angle_timer.reset()
        self.angle_timer.start()


    def execute(self):
        angle = self.drive.getAngle()

        rot_speed = 0
        if angle < 75:
            rot_speed = 0.2
        elif angle > 85:
            rot_speed = -0.2
        
        y_speed = 0
        if self.angle_timer.hasElapsed(1):
            if not self.grabber_opened:
                self.grabber_opened = True
                self.grabber.grabber_angle = self.grabber.presets.REEF_GRAB
                self.grabber.openGrabber()
            y_speed = 0.4

        self.drive.drive(0, y_speed, rot_speed)
    

    def end(self, interrupted):
        self.drive.stop()
        self.grabber.closeGrabber()
        self.grabber.grabber_angle = self.grabber.presets.STORE

        self.angle_timer.stop()
        self.angle_timer.reset()
    

    def isFinished(self):
        pos = self.drive.getPosition()
        if abs(pos.X()) > 1.5:
            return True