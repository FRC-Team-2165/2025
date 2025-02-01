import wpilib
import commands2
import commands2.button as button

from subsystems import DriveSubsystem,\
    GrabberSubsystem,\
    PickerSubsystem,\
    SlideSubsystem

from commands import DriveControllerCommand,\
    GrabberAngleControllerCommand,\
    RunPickerCommand,\
    ToggleGrabberCommand,\
    TogglePickerCommand,\
    ToggleSlideCommand,\
    WatchTagCommand

from components import LocationDataClientManager

class Robot(wpilib.TimedRobot):
    def robotInit(self):
        self.main_controller = button.CommandXboxController(0)
        self.drive = DriveSubsystem()
        self.grabber = GrabberSubsystem()
        self.picker = PickerSubsystem()
        self.slide = SlideSubsystem()

        address = ""
        port = ""
        self.LDC = LocationDataClientManager(address, port)

        self.drive.setDefaultCommand(DriveControllerCommand(self.drive, self.main_controller))
        self.grabber.setDefaultCommand(GrabberAngleControllerCommand(self.grabber, self.main_controller))
        
        self.main_controller.leftBumper().onTrue(ToggleGrabberCommand(self.grabber))
        self.main_controller.rightBumper().onTrue(TogglePickerCommand(self.picker))
        self.main_controller.y().onTrue(ToggleSlideCommand(self.slide))
        self.main_controller.rightTrigger().whileTrue(RunPickerCommand(self.picker))

        self.main_controller.leftTrigger().whileTrue(WatchTagCommand(self.drive, self.LDC, 3))

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