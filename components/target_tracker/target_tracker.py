from dataclasses import dataclass
import math

@dataclass
class Position:
    x: float = 0
    y: float = 0
    z: float = 0
    angle: float = 0

    def __add__(self, pos: "Position"):
        output = Position()
        output.x = self.x + pos.x
        output.y = self.y + pos.y
        output.z = self.z + pos.z
        output.angle = self.angle + pos.angle
        return output

class TargetTracker:
    def __init__(self, start_pos: Position):
        self.start_pos = start_pos
        self.current_pos = start_pos
        self.target_pos = start_pos
    
    def updateTargetPosition(self, target_pos: Position, relative: bool = True):
        if relative:
            # self.target_pos = self.current_pos + target_pos
            relative_pos = Position()
            angle = self.current_pos.angle + target_pos.angle
            hyp = math.sqrt(abs(target_pos.x) ** 2 + abs(target_pos.y) ** 2)
            relative_pos.angle = angle
            relative_pos.x = math.cos(angle) * hyp
            relative_pos.y = math.sin(angle) * hyp
            print(angle)

            self.target_pos = self.current_pos + relative_pos
        else:
            self.target_pos = target_pos
    
    def updateCurrentPosition(self, current_pos: Position):
        self.current_pos = current_pos
    
    def getTargetRelativePosition(self):
        output = Position()
        current = self.current_pos
        target = self.target_pos
        output.x = max(current.x, target.x) - min(current.x, target.x)
        output.y = max(current.y, target.y) - min(current.y, target.y)
        output.z = max(current.z, target.z) - min(current.z, target.z)
        output.angle = target.angle - current.angle
        return output