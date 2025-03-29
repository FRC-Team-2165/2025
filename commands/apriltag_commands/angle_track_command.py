from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from math import degrees, atan
from time import process_time

class AngleTrackCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int, loss_timeout = 0.2):
        super().__init__()
        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        self.has_target = False
        self.target_angle = 0

        self.deadband = 5
        self.loss_timeout = loss_timeout
        self.last_seen = process_time()
        self.rot_speed = 0

        self.addRequirements(subsystem)

    
    def initialize(self):
        self.has_target = False
        self.stream.startRequest()


    def execute(self):
        data = self.stream.getData()
        self.has_target = False

        for i in data:
            i: Location
            if i.id_num == self.target_id:
                self.has_target = True
                self.target_angle = degrees(atan(i.x / i.y)) + self.subsystem.getAngle()
                break
        
        if self.has_target or process_time() - self.last_seen < self.loss_timeout:
            current = self.subsystem.getAngle()
            target = self.target_angle
            self.last_seen = process_time()

            rot_speed = 0
            if abs(current - target) < self.deadband:
                pass
            else:
                error = target - current
                rot_speed = error / abs(error) * 0.2
            self.rot_speed = rot_speed
            # self.subsystem.drive(0, 0, rot_speed)
        else:
            self.rot_speed = 0
            # self.subsystem.stop()
        self.subsystem.drive(0,0, self.rot_speed)
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()