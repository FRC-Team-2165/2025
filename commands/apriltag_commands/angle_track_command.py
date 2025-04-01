from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from math import degrees, atan
from time import process_time

class AngleTrackCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_ids: int|list[int], loss_timeout = 0.2, deadband: float = 5):
        super().__init__()
        self.subsystem = subsystem
        self.stream = location_stream
        if target_ids is int:
            target_ids = [target_ids]
        self.target_ids = target_ids

        self.has_target = False
        self.target_angle = 0

        self.deadband = deadband
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

        valid_targets = []

        for i in data:
            i: Location
            if i.id_num in self.target_ids:
                self.has_target = True
                
                valid_targets.append(degrees(atan(i.x / i.y)) + self.subsystem.getAngle())
        
        if self.has_target:
            valid_targets.sort()
            self.target_angle =  valid_targets[0]
            print("got target")
        
        if self.has_target:
            current = self.subsystem.getAngle()
            target = self.target_angle
            self.last_seen = process_time()

            rot_speed = 0
            if abs(current - target) < self.deadband:
                pass
            else:
                error = target - current
                rot_speed = (error * 0.5) / abs(error * 0.5) * 0.2
            self.rot_speed = rot_speed
        else:
            self.rot_speed = 0
        self.subsystem.drive(0,0, self.rot_speed)
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()