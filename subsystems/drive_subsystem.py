from commands2 import Subsystem
import components.swerve.drive as drive
import components.swerve.module as swervemodule
import navx
import wpilib
from wpimath.geometry import Translation2d
from wpimath.filter import SlewRateLimiter

class DriveSubsystem(Subsystem):
    def __init__(self, starting_angle = 0):
        super().__init__()

        self.speed_modifier = 1

        front_left = swervemodule.SwerveModuleConfig(4, 3, 10, Translation2d(0.339725, 0.288925), True, gear_ratio= 8.14)
        rear_left = swervemodule.SwerveModuleConfig(2, 1, 9, Translation2d(0.339725, -0.288925), gear_ratio= 8.14)
        rear_right = swervemodule.SwerveModuleConfig(8, 7, 12, Translation2d(-0.339725, -0.288925), gear_ratio= 8.14)
        front_right = swervemodule.SwerveModuleConfig(6, 5, 11, Translation2d(-0.339725, 0.288925), gear_ratio=8.14)

        self.xLimiter = SlewRateLimiter(1.8)
        self.yLimiter = SlewRateLimiter(1.8)
        self.rotationLimiter = SlewRateLimiter(1.8)

        self.gyro = navx.AHRS(wpilib.SPI.Port.kMXP)
        self.swervedrive = drive.SwerveDrive(front_left, front_right, rear_left, rear_right, 0.1)

        self.yaw_offset = starting_angle
        self.roll_error = self.gyro.getRoll()
        self.pitch_error = self.gyro.getPitch()

    def drive(self, xSpeed: float, ySpeed: float, rotation: float, fieldrelative: bool = True):
        if self.roll_error == 0:
            self.roll_error = self.gyro.getRoll()
        if self.pitch_error == 0:
            self.pitch_error = self.gyro.getPitch()
        xSpeed = self.xLimiter.calculate(xSpeed)
        ySpeed = self.yLimiter.calculate(ySpeed)
        rotation = self.rotationLimiter.calculate(rotation)

        # print(f"x: {xSpeed} y: {ySpeed}")

        if fieldrelative:
            self.swervedrive.drive(-xSpeed, -ySpeed, rotation, self.getAngle())
        else:
            self.swervedrive.drive(-xSpeed, -ySpeed, rotation)

    def initialize(self):
        self.swervedrive.initialize()

    def brace(self):
        self.swervedrive.brace()
    
    def stop(self):
        self.swervedrive.stopMotor()

    def getAngle(self):
        return self.gyro.getAngle() - self.yaw_offset
    
    def resetAngle(self):
        self.yaw_offset = self.gyro.getAngle()
    
    def getPitch(self):
        return self.gyro.getPitch() - self.pitch_error

    def getRoll(self):
        return self.gyro.getRoll() - self.roll_error
    
    def getPosition(self):
        return self.swervedrive.position()
    
    def resetPosition(self):
        self.swervedrive.reset_position()