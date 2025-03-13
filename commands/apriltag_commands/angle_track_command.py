from commands2 import Command
from subsystems import DriveSubsystem
from components import LocationDataClientManager, Location
from math import degrees, atan

class AngleTrackCommand(Command):
    def __init__(self, subsystem: DriveSubsystem, location_stream: LocationDataClientManager, target_id: int):
        super().__init__()
        self.subsystem = subsystem
        self.stream = location_stream
        self.target_id = target_id

        self.has_target = False
        self.target_angle = 0

        self.deadband = 5

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
        
        if self.has_target:
            current = self.subsystem.getAngle()
            target = self.target_angle

            rot_speed = 0
            if abs(current - target) < self.deadband:
                pass
            else:
                error = target - current
                rot_speed = error / abs(error) * 0.25
            self.subsystem.drive(0, 0, rot_speed)
        else:
            self.subsystem.stop()
    

    def end(self, interrupted):
        self.stream.stopRequest()
    

    def isFinished(self):
        return super().isFinished()