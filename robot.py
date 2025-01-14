import wpilib
import commands2
import commands2.button as button

from subsystems import DriveSubsystem

from commands import DriveControllerCommand

class Robot(wpilib.TimedRobot):
    def robotInit(self):
        self.main_controller = button.CommandXboxController(0)
        self.drive = DriveSubsystem()

        self.drive.setDefaultCommand(DriveControllerCommand(self.drive, self.main_controller))

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()
    
    def autonomousInit(self):
        return super().autonomousInit()
    
    def autonomousPeriodic(self):
        return super().autonomousPeriodic()

    def teleopInit(self):
        return super().teleopInit()
    
    def teleopPeriodic(self):
        return super().teleopPeriodic()
    
if __name__ == "__main__":
    wpilib.run(Robot)