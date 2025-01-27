from commands2 import Subsystem
from wpilib import DoubleSolenoid
import phoenix5
import wpilib

#TODO add motor IDs
#TODO add solenoid channels
#TODO verify solenoid positions
#TODO add sensor ID

class PickerSubsystem(Subsystem):
    def __init__(self):
        super().__init__()

        self.intake_motor = phoenix5.WPI_VictorSPX(0)
        self.intake_speed = 0

        self.sensor = wpilib.DigitalInput(0)

        self.solenoid = DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 0, 0)

        self.raiseIntake()
    
    def lowerIntake(self) -> None:
        """
        lower the intake subsystem
        """
        self.solenoid.set(DoubleSolenoid.Value.kForward)

    def raiseIntake(self) -> None:
        """
        raise the intake subsystem
        """
        self.solenoid.set(DoubleSolenoid.Value.kReverse)
    
    def toggleIntakePosition(self) -> None:
        """
        toggles the intake subsystem's position
        """
        self.solenoid.toggle()
    
    def startMotor(self, speed = 1) -> None:
        """
        start the intake motor to the given speed, default 1
        """
        self.intake_motor.set(speed)
        self.intake_speed = speed

    def stopMotor(self) -> None:
        """
        stop the intake motor
        """
        self.intake_motor.set(0)
        self.intake_speed = 0
    
    def isMotorOn(self) -> bool:
        """
        returns whether the intake motor is on
        """
        return bool(self.intake_speed)

    def hasObject(self) -> bool:
        """
        returns whether the intake subsystem has an object
        """
        return self.sensor.get()