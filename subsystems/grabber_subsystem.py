from commands2 import Subsystem
from wpilib import DoubleSolenoid
import wpilib
import phoenix5
from wpimath.controller import PIDController
import rev
from dataclasses import dataclass

class GrabberSubsystem(Subsystem):
    def __init__(self):
        super().__init__()

        self.grab_solenoid = DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 5, 4)
        self.bird_solenoid = DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 7, 6)
        self.motor = phoenix5.WPI_TalonSRX(14)
        self.motor.setInverted(True)

        self.presets = GrabberPresets()

        self.encoder = wpilib.DutyCycleEncoder(5)

        self.upper_limit_val_closed = 127
        self.upper_limit_val_open = 110
        self.lower_limit_val_extended = 85
        self.lower_limit_val_retracted = -54

        self.grabber_open = False
        self.bird_extended = False

        self.target_angle = self.grabber_angle
        self.grabber_angle = self.grabber_angle

        self.closeGrabber()
        self.retractBird()

        p = 0.03
        i = 0
        d = 0
        self.pid = PIDController(p, i, d)
        self.pid.setTolerance(0.5)

        self.last_input = 0
    


    def closeGrabber(self) -> None:
        self.grab_solenoid.set(DoubleSolenoid.Value.kForward)
        self.grabber_open = False
    
    def openGrabber(self) -> None:
        if self.grabber_angle < self.upper_limit_val_open and self.target_angle < self.upper_limit_val_open:
            self.grab_solenoid.set(DoubleSolenoid.Value.kReverse)
            self.grabber_open = True
    
    def toggleGrabber(self) -> None:
        if self.grabber_open:
            self.closeGrabber()
        else:
            self.openGrabber()
    
    def extendBird(self) -> None:
        if self.grabber_angle >= self.lower_limit_val_extended and self.target_angle >= self.lower_limit_val_extended:
            self.bird_solenoid.set(DoubleSolenoid.Value.kReverse)
            self.bird_extended = True
    
    def retractBird(self) -> None:
        self.bird_solenoid.set(DoubleSolenoid.Value.kForward)
        self.bird_extended = False
    
    def toggleBird(self) -> None:
        if self.bird_extended:
            self.retractBird()
        else:
            self.extendBird()



    @property
    def grabber_angle(self):
        return self.encoderValToAngle(self.encoder.get())
    
    @grabber_angle.setter
    def grabber_angle(self, angle: float):
        if angle > self.upper_limit_val_open and self.grabber_open:
            self.grabber_angle = self.upper_limit_val_open
        elif angle > self.upper_limit_val_closed and not self.grabber_open:
            self.grabber_angle = self.upper_limit_val_closed
        elif angle < self.lower_limit_val_extended and self.bird_extended:
            self.grabber_angle = self.lower_limit_val_extended
        elif angle < self.lower_limit_val_retracted and not self.bird_extended:
            self.grabber_angle = self.lower_limit_val_retracted
        else:
            self.target_angle = angle

    def angleToEncoderVal(self, angle: float):
        return (-angle / 360) + 0.590

    def encoderValToAngle(self, val: float):
        return -(val - 0.590) * 360
    
    def stopMotor(self) -> None:
        self.motor.set(0)

    def move(self, speed: float) -> None:
        self.grabber_angle = self.target_angle + (2 * speed)



    def periodic(self) -> None:
        self.pid.setSetpoint(self.target_angle)
        current_angle = self.grabber_angle
        speed = self.pid.calculate(current_angle)

        if abs(speed) > 1:
            speed /= abs(speed)

        self.motor.set(speed)

        # print(self.grabber_angle)

@dataclass
class GrabberPresets:
    START = 110
    STORE = 105
    REEF_GRAB = 40
    PROCESSOR = -20
    BIRD = 90