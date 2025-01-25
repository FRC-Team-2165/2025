from commands2 import Subsystem
from wpilib import DoubleSolenoid
import wpilib
import phoenix5
from wpimath.controller import PIDController

#TODO add motor IDs
#TODO add solenoid channels
#TODO verify solenoid positions
#TODO add sensor ID
#TODO verify PID setup and calibration

class GrabberSubsystem(Subsystem):
    def __init__(self):
        super().__init__()

        self.solenoid = DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 0, 0)
        self.motor = phoenix5.WPI_VictorSPX(0)
        self.upper_limit = wpilib.DigitalInput(0)
        self.lower_limit = wpilib.DigitalInput(0)

        self.encoder = wpilib.DutyCycleEncoder(0)

        self.lower_limit_val = 0
        self.upper_limit_val = 0
        self.target_angle = 0

        p = 1/30
        i = 0
        d = 0
        self.pid = PIDController(p, i, d)
        self.pid.setTolerance(0.5)
    


    def closeGrabber(self) -> None:
        self.solenoid.set(DoubleSolenoid.Value.kReverse)
    
    def openGrabber(self) -> None:
        self.solenoid.set(DoubleSolenoid.Value.kForward)
    
    def toggleGrabber(self) -> None:
        self.solenoid.toggle()
    
    def getGrabberState(self) -> DoubleSolenoid.Value:
        return self.solenoid.get()



    @property
    def grabber_angle(self):
        return self.encoder.get()
    
    @grabber_angle.setter
    def grabber_angle(self, angle: float):
        self.target_angle = angle
    
    def stopMotor(self) -> None:
        self.motor.set(0)
    
    def _limitMovement(self, speed: float) -> float:
        if speed > 0 and self.upper_limit.get() or\
          speed < 0 and self.lower_limit.get():
            speed = 0
        return speed

    def move(self, speed: float) -> None:
        speed = self._limitMovement(speed)
        if speed == 0:
            self.target_angle = self.grabber_angle
        else:
            self.target_angle += 0.525 * speed
        
    def periodic(self) -> None:
        self.pid.setSetpoint(self.target_angle)
        current_angle = self.grabber_angle
        speed = self.pid.calculate(current_angle)

        speed = self._limitMovement(speed)

        self.motor.set(speed)