from commands2 import Subsystem
from wpilib import DoubleSolenoid
import wpilib

#TODO add solenoid channels
#TODO verify solenoid positions

class SlideSubsystem(Subsystem):
    def __init__(self):
        super().__init__() 

        self.solenoid = DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 0, 0)
    
        self.setToLoad()

    def getState(self) -> DoubleSolenoid.value:
        """
        returns the state of the slide
        """
        return self.solenoid.get()

    def setToLoad(self) -> None:
        """
        sets the slide to loading position
        """
        self.solenoid.set(DoubleSolenoid.Value.kReverse)

    def setToDump(self) -> None:
        """
        sets the slide to dumping position
        """
        self.solenoid.set(DoubleSolenoid.Value.kForward)

    def toggle(self) -> None:
        """
        toggles the slide between dumping and loading positions
        """
        self.solenoid.toggle()