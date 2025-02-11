from dataclasses import dataclass

from wpimath.geometry import Translation2d, Rotation2d
from wpilib import MotorSafety
import math

import phoenix5
import phoenix5.sensors
import rev

@dataclass
class Polar:
    magnitude: float
    theta: float

    def to_Cartesian(self):
        r = self.magnitude
        theta = self.theta

        theta *= math.pi / 180

        x = r * math.cos(theta)
        y = r * math.sin(theta)

        return Cartesian(x, y)
    
    def __add__(self, vector: "Polar"):
        return (self.to_Cartesian() + vector.to_Cartesian()).to_Polar()

    def to_Translation2d(self):
        return Translation2d(distance= self.magnitude, angle= Rotation2d.fromDegrees(self.theta))

@dataclass
class Cartesian:
    x: float
    y: float

    def to_Polar(self):
        x = self.x
        y = self.y
        r = math.sqrt(x ** 2 + y ** 2)
        if x == 0:
            if y > 0:
                return Polar(y, 90)
            elif y < 0:
                return Polar(-y, 270)
            else:
                return Polar(0, 0)
        else:
            theta = math.atan(y/x) * 180 / math.pi
        if x < 0:
            theta += 180
        elif y < 0:
            theta += 360
        return Polar(r, theta)

    def to_Tranlation2d(self):
        return Translation2d(self.x, self.y)
    
    def __add__(self, vector: "Cartesian"):
        return Cartesian(self.x + vector.x, self.y + vector.y)

@dataclass
class SwerveModuleConfig:
    dmotor_id: int
    tmotor_id: int
    tencoder_id: int
    relative_position: Translation2d
    dwheel_circumference = 0.0508 * 2 * math.pi
    inverted: bool = False
    gear_ratio: float = 1

class SwerveModule(MotorSafety):
    def __init__(self, module_config: SwerveModuleConfig):
        super().__init__()
        self.drive_motor = rev.SparkMax(module_config.dmotor_id, rev.SparkMax.MotorType.kBrushless)
        self.drive_encoder = self.drive_motor.getEncoder()
        # self.drive_encoder.setVelocityConversionFactor(module_config.dwheel_circumference / (module_config.gear_ratio * 60.0))
        self.velocity_conversion_factor = module_config.dwheel_circumference / (module_config.gear_ratio * 60.0)
        # self.drive_encoder.setPositionConversionFactor(module_config.dwheel_circumference / module_config.gear_ratio)

        self.turn_motor = phoenix5.WPI_TalonSRX(module_config.tmotor_id)
        self.turn_encoder = phoenix5.sensors.CANCoder(module_config.tencoder_id)

        self.drive_motor.setInverted(module_config.inverted)

        self.relative_position = module_config.relative_position

    def getInverted(self):
        return self.drive_motor.getInverted()
    
    def setInverted(self, inverted: bool):
        self.drive_motor.setInverted(inverted)

    def offset_from_center(self) -> float:
        return self.relative_position.distance(Translation2d())

    def getWheelAngle(self) -> float:
        return self.turn_encoder.getAbsolutePosition()

    def getTargetSpeed(self) -> float:
        return self.drive_motor.get()

    def setWheelAngle(self, angle: float):
        angle = self.optimizeAngle(angle)
        self.turn_motor.set(phoenix5.ControlMode.Position, (4096 / 360.0 * angle))
        self.feed()

    def setTargetSpeed(self, speed):
        if abs(speed) > 1:
            speed /= abs(speed)
        self.drive_motor.set(speed)
        self.feed()

    def stopMotor(self):
        self.drive_motor.stopMotor()
        self.turn_motor.stopMotor()
        self.feed()
    
    def setState(self, vector: Polar):
        state = self.optimize(vector)
        self.setWheelAngle(state.theta)
        self.setTargetSpeed(state.magnitude)
    
    def getState(self):
        return Polar(self.drive_motor.get(), self.getWheelAngle())

    def optimizeAngle(self, angle: float):
        offset = self.turn_encoder.getPosition() // 360
        angle = angle % 360 + offset * 360
        target_angles = (angle + n * 180 for n in range(-2, 3))
        return min(target_angles, key = lambda a: abs(self.turn_encoder.getPosition() - a))
    
    def optimize(self, state: Polar):
        a = self.optimizeAngle(state.theta)
        speed = state.magnitude
        if abs(a % 360 - state.theta % 360) > 0.01:
            speed = -speed
        return Polar(speed, a)
    
    def set_state_mps(self, state: Polar):
        vector = Polar(state.magnitude / 3.55, state.theta)
        self.setState(vector)

    def get_state_mps(self):
        return Polar(self.drive_encoder.getVelocity() * self.velocity_conversion_factor, self.getWheelAngle())
    
    def rotation_angle(self):
        base = self.relative_position.angle().degrees() + 90
        return base