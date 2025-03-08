import wpilib
import commands2
import commands2.button as button

from subsystems import DriveSubsystem,\
    GrabberSubsystem,\
    PickerSubsystem,\
    SlideSubsystem

from commands import DriveControllerCommand,\
    GrabberAngleControllerCommand,\
    IntakePickerCommand,\
    SpitPickerCommand,\
    ToggleGrabberCommand,\
    TogglePickerCommand,\
    ToggleSlideCommand,\
    ToggleBirdCommand,\
    GrabberAnglePresetCommand,\
    ResetDriveCommand,\
    BirdCatchCommand

class Robot(wpilib.TimedRobot):
    def robotInit(self):
        self.main_controller = button.CommandXboxController(0)
        self.drive = DriveSubsystem()
        self.grabber = GrabberSubsystem()
        self.picker = PickerSubsystem()
        self.slide = SlideSubsystem()

        self.drive.setDefaultCommand(DriveControllerCommand(self.drive, self.main_controller))
        self.main_controller.back().and_(self.main_controller.start()).onTrue(ResetDriveCommand(self.drive))
        self.grabber.setDefaultCommand(GrabberAngleControllerCommand(self.grabber, self.main_controller))
        
        self.main_controller.leftBumper().onTrue(ToggleGrabberCommand(self.grabber))
        self.main_controller.rightBumper().onTrue(TogglePickerCommand(self.picker))
        self.main_controller.x().onTrue(ToggleSlideCommand(self.slide))
        self.main_controller.y().onTrue(ToggleBirdCommand(self.grabber))
        self.main_controller.b().onTrue(BirdCatchCommand(self.grabber, self.slide))
        self.main_controller.leftTrigger().whileTrue(SpitPickerCommand(self.picker))
        self.main_controller.rightTrigger().whileTrue(IntakePickerCommand(self.picker))

        self.main_controller.povUp().onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.BIRD))
        self.main_controller.povDown().onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.PROCESSOR))
        self.main_controller.povLeft().onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.STORE))
        self.main_controller.povRight().onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.REEF_GRAB))

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()
    
    def autonomousInit(self):
        return super().autonomousInit()
    
    def autonomousPeriodic(self):
        return super().autonomousPeriodic()

    def teleopInit(self):
        self.grabber.grabber_angle = self.grabber.grabber_angle
    
    def teleopPeriodic(self):
        return super().teleopPeriodic()
    
if __name__ == "__main__":
    wpilib.run(Robot)