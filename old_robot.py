import wpilib
import commands2
import commands2.button as button
import commands2.cmd as cmd
from wpilib import SmartDashboard as sd

import os

from subsystems import DriveSubsystem

class Robot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.main_controller = button.CommandXboxController(0)
        self.secondary_controller = button.CommandXboxController(1)
        # TODO adapt controls for guitar hero controller
        self.arm = ArmSubsystem()
        self.climb = ClimbSubsystem()
        self.drive = DriveSubsystem()
        self.hand = HandSubsystem()
        self.match_data_stream = MatchDataStreamClient("vision-2165.local", 1181)
        self.match_data_stream.start()


        self.arm.setDefaultCommand(ArmControllerCommand(self.arm, self.secondary_controller))
        self.drive.setDefaultCommand(DriveControllerCommand(self.drive, self.main_controller))
        self.main_controller.back().and_(self.main_controller.start()).onTrue(ResetDriveCommand(self.drive))
        
        self.main_controller.a().whileTrue(AutoPickupCommand(self.drive, self.hand, self.match_data_stream))
        # self.main_controller.a().whileTrue(AutoCollectCommand()) # TODO finish command
        self.secondary_controller.povDown().toggleOnTrue(SetArmAngleCommand(self.arm, 0))
        self.secondary_controller.povDownLeft().toggleOnTrue(SetArmAngleCommand(self.arm, 0))
        self.secondary_controller.povDownRight().toggleOnTrue(SetArmAngleCommand(self.arm, 0))
        self.secondary_controller.povLeft().toggleOnTrue(SetArmAngleCommand(self.arm, 9))
        self.secondary_controller.povUp().toggleOnTrue(SetArmAngleCommand(self.arm, 50))
        self.secondary_controller.povRight().toggleOnTrue(SetArmAngleCommand(self.arm, 80))
        # self.main_controller.b().toggleOnTrue(AutoAmpCommand()) # TODO finish command
        # self.main_controller.rightBumper().toggleOnTrue(AutoAimCommand()) # TODO finish command

        self.secondary_controller.y().onTrue(ToggleClimbCommand(self.climb))
        self.secondary_controller.x().toggleOnTrue(SpitCommand(self.hand))
        self.secondary_controller.leftTrigger().toggleOnTrue(CollectCommand(self.hand))
        self.secondary_controller.rightTrigger().toggleOnTrue(ShootCommand(self.hand))
        # self.secondary_controller.leftTrigger().toggleOnTrue(SpitCommand(self.hand))

        self.auto_interpreter = generate_auto_interpreter(self.arm, self.climb, self.drive, self.hand)
        self.auto_command = self.auto_interpreter

        self.auto_instructions = sd.getEntry("auto instructions")
        self.auto_instructions.setPersistent()

        try:
            os.mkdir(wpilib.getDeployDirectory())
        except:
            #exists
            pass
        try:
            with open(wpilib.getDeployDirectory() + "/auto_code.txt", "r+") as auto_file:
                self.auto_instructions.setString(auto_file.read())
        except FileNotFoundError:
            with open(wpilib.getDeployDirectory() + "/auto_code.txt", "w+") as auto_file:
                auto_file.write("print \"Nothing doing\"")
            self.auto_instructions.setString("print \"Nothing doing\"")

        self.update = sd.getEntry("update auto")
        self.update.setBoolean(False)
        self.update.setPersistent()

        self.auto_command = commands2.SequentialCommandGroup(
            DriveDistCommand(self.drive),
            DriveDistCommand(self.drive)
        )


    def robotPeriodic(self) -> None:
        commands2.CommandScheduler.getInstance().run()

        # sd.putNumber("arm angle", self.arm.screw_angle)

        # sd.putNumber("arm motor angle", self.arm.screw_encoder.getPosition())

        sd.putBoolean("holding ring", not self.hand.lb_sensor.get())
        sd.putNumber("robot angle", self.drive.getAngle())
        # sd.putNumber("pos x", self.drive.getPosition().X())
        # sd.putNumber("pos y", self.drive.getPosition().Y())
        # sd.putNumber("robot angle", self.drive.getAngle())

        sd.putBoolean("sensor", self.hand.sensor.get())

        # sd.putString("Autonomous instructions", "")
        # sd.setPersistent("Autonomous instructions")

        if self.update.getBoolean(False):
            self.update.setBoolean(False)
            insts = self.auto_instructions.getString("print \"Nothing doing\"")
            print(insts)
            with open(wpilib.getDeployDirectory() + "/auto_code.txt", "w+") as auto_file:
                auto_file.write(insts)

            
    
    def autonomousInit(self) -> None:
        if self.auto_command is not None:
        #     try:
        #         with open(wpilib.getDeployDirectory() + "/auto_code.txt", "r+") as auto_file:
        #             instructions = auto_file.read()
        #             self.auto_interpreter.load_program(instructions)
        #             if not self.auto_interpreter.current_program_valid():
        #                 print("========================================")
        #                 print("Interpreter Dump - auto program invalid!")
        #                 print("    Code    \n----------")
        #                 print("instructions")
        #                 print("  Errors  \n---------")
        #                 print(self.auto_interpreter.errors)
        #                 print("========================================")
            self.auto_interpreter.load_program("""set -2
drive dist 0 0.1 0
wait for 1 seconds
spit
set 50
drive dist 0 2 0""")
            self.auto_command.schedule()
        #     except:
        #         print("Something went wrong loading autonomous!")

                    
    def autonomousPeriodic(self) -> None:
        return super().autonomousPeriodic()
    
    def teleopInit(self) -> None:
        # if self.auto_command is not None and self.auto_command.is
        if self.auto_command is not None and self.auto_command.isScheduled():
            self.auto_command.cancel()
        
    def teleopPeriodic(self) -> None:
        return super().teleopPeriodic()
    
if __name__ == "__main__":
    wpilib.run(Robot)
