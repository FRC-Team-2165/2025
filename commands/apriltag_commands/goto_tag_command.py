from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from time import process_time
from math import atan, degrees, sqrt, sin, cos
from wpimath.geometry import Translation2d


class GotoTagCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int, drive_proportional: float, loss_timeout: float = 0.2, ignore_x: bool = False, ignore_y: bool = False, x_offset: float = 0, y_offset: float = 0, deadband: float = 0.05):
        super().__init__()

        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        self.drive_proportional = drive_proportional
        self.deadband = deadband
        self.loss_timeout = loss_timeout
        self.last_seen = process_time()
        self.has_target = False

        self.ignore_x = ignore_x
        self.ignore_y = ignore_y
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
                
                self.target_pos = Translation2d(i.x, i.y)

                print("got target")
                break
        
        if self.has_target or abs(process_time() - self.last_seen) < self.loss_timeout:
            x_speed = 0
            if not self.ignore_x:
                x_error = self.target_pos.x - self.x_offset
                if abs(x_error) < self.deadband:
                    pass
                else:
                    speed = x_error * self.drive_proportional * 1.5
                    x_speed = speed + 0.1 * (x_error / abs(x_error))
            self.x_speed = x_speed

            y_speed = 0
            if not self.ignore_y:
                y_error = self.target_pos.y - self.y_offset
                if abs(y_error) < self.deadband:
                    pass
                else:
                    speed = y_error * self.drive_proportional
                    y_speed = speed + 0.1 * (y_error / abs(y_error))
            self.y_speed = y_speed
        else:
            self.x_speed = 0
            self.y_speed = 0
        self.subsystem.drive(self.x_speed, self.y_speed, 0, False)
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()