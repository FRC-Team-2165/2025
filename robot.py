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

from commands import AutoGrabberAngleCommand,\
    AutoDriveCommand,\
    AutoGrabCommand,\
    AutoReleaseCommand,\
    AutoLoadCommand,\
    AutoDumpCommand,\
    ResetDriveCommand,\
    AngleTrackCommand,\
    GotoTagCommand

from components import LocationDataClientManager

fwd_upper_stream_address = "vision-2165-working.local"
fwd_upper_stream_port = 1181

fwd_lower_stream_address = "vision-2165-working.local"
fwd_lower_stream_port = 1183

grabber_stream_address = "vision-2165-working.local"
grabber_stream_port = 1185

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

        self.fwd_upper_stream = LocationDataClientManager(fwd_upper_stream_address, fwd_upper_stream_port)
        self.fwd_lower_stream = LocationDataClientManager(fwd_lower_stream_address, fwd_lower_stream_port)
        self.grabber_stream = LocationDataClientManager(grabber_stream_address, grabber_stream_port)

        self.main_controller.a().whileTrue(GotoTagCommand(self.drive, self.fwd_upper_stream, 7, drive_proportional= 1, y_offset= 1))

        self.auto_leave_algae_coral = commands2.SequentialCommandGroup(
            AutoDriveCommand(self.drive, angle=90, reset_angle= True),
            AutoGrabberAngleCommand(self.grabber, self.grabber.presets.REEF_GRAB),
            commands2.WaitCommand(0.25),
            AutoReleaseCommand(self.grabber),
            AutoDriveCommand(self.drive, y_dist= 1.7, move_speed= 0.3),
            commands2.WaitCommand(0.25),
            AutoGrabCommand(self.grabber),
            commands2.WaitCommand(0.5),
            AutoGrabberAngleCommand(self.grabber, self.grabber.presets.STORE),
            commands2.WaitCommand(0.5),
            AutoDriveCommand(self.drive, y_dist= -0.5, move_speed= 0.3),
            AutoDriveCommand(self.drive, angle= -90),
            AutoDriveCommand(self.drive, y_dist= 0.55, move_speed= 0.3),
            AutoDriveCommand(self.drive, x_dist= 0.05, move_speed= 0.15),
            AutoDumpCommand(self.slide)
        )

        self.auto_leave = commands2.SequentialCommandGroup(
            AutoDriveCommand(self.drive, y_dist= 1.7, move_speed= 0.3)
        )

        self.auto_command = self.auto_leave_algae_coral

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()
        pass
    
    def autonomousInit(self):
        self.auto_command.schedule()
    
    def autonomousPeriodic(self):
        return super().autonomousPeriodic()

    def teleopInit(self):
        self.grabber.grabber_angle = self.grabber.grabber_angle
        if self.auto_command is not None and self.auto_command.isScheduled():
            self.auto_command.cancel()
    
    def teleopPeriodic(self):
        return super().teleopPeriodic()
    
if __name__ == "__main__":
    wpilib.run(Robot)