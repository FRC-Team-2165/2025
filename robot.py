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
    ResetDriveCommand

from commands import AngleTrackCommand,\
    GotoTagCommand,\
    AutoGotoTagCommand,\
    DriveCommand

from components import LocationDataClientManager

import socket

fwd_upper_stream_address = "vision-2165-working.local"
fwd_upper_stream_port = 1181

fwd_lower_stream_address = "vision-2165-working.local"
fwd_lower_stream_port = 1183

grabber_stream_address = "vision-2165-working.local"
grabber_stream_port = 1185

coral_tags = [6, 7, 8, 9, 10, 11, 17, 18, 19, 20, 21, 22]

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

        self.main_controller.povUp().and_(self.main_controller.a().not_()).onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.BIRD))
        self.main_controller.povDown().and_(self.main_controller.a().not_()).onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.PROCESSOR))
        self.main_controller.povLeft().and_(self.main_controller.a().not_()).onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.STORE))
        self.main_controller.povRight().and_(self.main_controller.a().not_()).onTrue(GrabberAnglePresetCommand(self.grabber, self.grabber.presets.REEF_GRAB))

        self.fwd_upper_stream = LocationDataClientManager(fwd_upper_stream_address, fwd_upper_stream_port)
        self.fwd_lower_stream = LocationDataClientManager(fwd_lower_stream_address, fwd_lower_stream_port)
        self.grabber_stream = LocationDataClientManager(grabber_stream_address, grabber_stream_port)

        self.main_controller.a().and_(self.main_controller.povUp()).whileTrue(DriveCommand(self.drive, y_speed= 0.25))
        self.main_controller.a().and_(self.main_controller.povLeft()).whileTrue(GotoTagCommand(self.drive, self.fwd_lower_stream, coral_tags, drive_proportional= 1/3, rotation_proportional= 1/270, x_offset= 0.17, y_offset= 1.25, angle_offset= 5))
        self.main_controller.a().and_(self.main_controller.povRight()).whileTrue(GotoTagCommand(self.drive, self.fwd_lower_stream, coral_tags, drive_proportional= 1/3, rotation_proportional= 1/270, x_offset= -0.15, y_offset= 1.25, angle_offset= -1))

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
            commands2.ParallelCommandGroup(
            AutoDriveCommand(self.drive, x_dist= 0.05, move_speed= 0.15),
            AutoDumpCommand(self.slide)
            ),
            commands2.WaitCommand(0.5),
            AutoDriveCommand(self.drive, y_dist= -0.5, angle= 180, turn_speed= 0.4, angle_deadband= 10),
            AutoDriveCommand(self.drive, reset_angle= True)
        )

        self.auto_leave = commands2.SequentialCommandGroup(
            AutoDriveCommand(self.drive, y_dist= 1.7, move_speed= 0.3),
            AutoDriveCommand(self.drive, angle= 180),
            AutoDriveCommand(self.drive, reset_angle= True)
        )

        self.auto_tagged = commands2.SequentialCommandGroup(
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
            AutoDriveCommand(self.drive, y_dist= -1.25, move_speed= 0.3),
            AutoDriveCommand(self.drive, angle= -90),
            AutoGotoTagCommand(self.drive, self.fwd_lower_stream, coral_tags, drive_proportional= 1/3, rotation_proportional= 1/270, x_offset= -0.15, y_offset= 1.25, angle_offset= -1),
            AutoDriveCommand(self.drive, y_dist= 1.25, move_speed= 0.3),
            AutoDumpCommand(self.slide),
            commands2.WaitCommand(1),
            AutoDriveCommand(self.drive, y_dist= -0.5, angle= 180, turn_speed= 0.4, angle_deadband= 10),
            AutoDriveCommand(self.drive, reset_angle= True)
        )

        self.auto_command = self.auto_tagged
        self.auto_command = self.auto_leave_algae_coral
        self.eyes_n_ears_controller = None

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()
        pass
    
    def autonomousInit(self):
        if self.eyes_n_ears_controller is None:
            # This is an error streamroller. This is intentional. Do not try to make this less bad
            try:
                controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                controller.connect(("vision-2165-working.local", 5810))
                self.eyes_n_ears_controller = controller
            except:
                pass

        self.auto_command.schedule()
    
    def autonomousPeriodic(self):
        return super().autonomousPeriodic()

    def teleopInit(self):
        if self.eyes_n_ears_controller is None:
            # This is an error streamroller. This is intentional. Do not try to make this less bad
            try:
                controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                controller.connect(("vision-2165-working.local", 5810))
                self.eyes_n_ears_controller = controller
            except:
                pass
        
        self.grabber.grabber_angle = self.grabber.grabber_angle
        if self.auto_command is not None and self.auto_command.isScheduled():
            self.auto_command.cancel()
    
    def teleopPeriodic(self):
        return super().teleopPeriodic()

    def disabledInit(self):
        if self.eyes_n_ears_controller is not None:
            try:
                control_code = 0xc20015a4.to_bytes(4, byte_order="big", signed=False)
                self.eyes_n_ears_controller.sendall(control_code)
            except:
                pass
            finally:
                self.eyes_n_ears_controller = None
    
if __name__ == "__main__":
    wpilib.run(Robot)
