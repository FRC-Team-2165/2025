from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from time import process_time
from math import atan, degrees, sqrt, sin, cos
from wpimath.geometry import Translation2d


class GotoTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int, loss_timeout: float = 0.2, drive_speed: float = 0, x_offset: float = 0, y_offset: float = 0, deadband: float = 0.03):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        self.drive_speed = drive_speed
        self.deadband = deadband
        self.loss_timeout = loss_timeout
        self.last_seen = process_time()
        self.has_target = False

        self.x_offset = x_offset
        self.y_offset = y_offset
        self.target_pos = Translation2d()
        self.x_speed = 0
        self.y_speed = 0

        self.addRequirements(subsystem)
    

    def initialize(self):
        self.subsystem.resetPosition()
        self.has_target = False
        self.stream.startRequest()
    

    def execute(self):
        data = self.stream.getData()
        self.has_target = False

        for i in data:
            i: Location
            if i.id_num == self.target_id:
                self.has_target = True
                
                robot_angle = self.subsystem.getAngle()
                i.x += self.x_offset
                i.y += self.y_offset
                tag_angle = degrees(atan(i.x / i.y))
                hyp = sqrt((i.x ** 2) + (i.y ** 2))
                target_x = cos(robot_angle + tag_angle) * hyp
                target_y = sin(robot_angle + tag_angle) * hyp
                # self.target_pos = Translation2d(target_x, target_y)
                self.target_pos = Translation2d(i.x, i.y)

                print("got target")
                break
        
        if self.has_target or abs(process_time() - self.last_seen) < self.loss_timeout:
            # current = self.subsystem.getPosition()
            # current = Translation2d(current.y, current.x)
            # print(self.target_pos)

            # x_speed = 0
            # if abs(self.target_pos.x - current.x) < self.deadband:
            #     pass
            # else:
            #     error = self.target_pos.x - current.x
            #     x_speed = error / abs(error) * self.drive_speed
            # self.x_speed = x_speed

            # y_speed = 0
            # if abs(current.y - self.target_pos.y) < self.deadband:
            #     pass
            # else:
            #     error = self.target_pos.y - current.y
            #     y_speed = error / abs(error) * self.drive_speed
            # self.y_speed = y_speed

            x_speed = 0
            if abs(self.target_pos.x) < self.deadband:
                pass
            else:
                x_speed = self.target_pos.x / abs(self.target_pos.x) * self.drive_speed
            self.x_speed = x_speed
            y_speed = 0
            if abs(self.target_pos.y) < self.deadband:
                pass
            else:
                y_speed = self.target_pos.y / abs(self.target_pos.y) * self.drive_speed
            self.y_speed = y_speed
        else:
            self.x_speed = 0
            self.y_speed = 0
        self.subsystem.drive(self.x_speed, self.y_speed, 0, False)
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()