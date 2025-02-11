from components.swerve.module import Polar, Cartesian, SwerveModuleConfig, SwerveModule

from wpimath import applyDeadband
from wpimath.geometry import Translation2d, Rotation2d

from wpilib.drive import RobotDriveBase

class SwerveDrive(RobotDriveBase):
    def __init__(self, front_left_cfg: SwerveModuleConfig,
                       front_right_cfg: SwerveModuleConfig,
                       rear_left_cfg: SwerveModuleConfig,
                       rear_right_cfg: SwerveModuleConfig,
                       deadband: float = 0):
        super().__init__()
        self.front_left = SwerveModule(front_left_cfg)
        self.front_right = SwerveModule(front_right_cfg)
        self.rear_left = SwerveModule(rear_left_cfg)
        self.rear_right = SwerveModule(rear_right_cfg)

        self.modules = [self.front_left, self.front_right, self.rear_left, self.rear_right]

        self.deadband = deadband

        self._position = Polar(0, 0)

    def setDeadband(self, deadband: float):
        self.deadband = deadband

    def getDescription(self):
        return "SwerveDrive"
    
    def drive(self, x_speed: float, y_speed: float, rotation: float, current_angle: float = 0, square_inputs: bool = False):
        if square_inputs:
            x_speed *= abs(x_speed)
            y_speed *= abs(y_speed)
            rotation *= abs(rotation)
        
        x_speed = applyDeadband(x_speed, self.deadband)
        y_speed = applyDeadband(y_speed, self.deadband)
        rotation = applyDeadband(rotation, self.deadband)

        target_vector = Cartesian(x_speed, -y_speed).to_Polar()
        target_vector.theta -= current_angle

        max_module_distance = max(m.offset_from_center() for m in self.modules)

        module_states: list[Polar] = []
        for m in self.modules:
            rotation_angle = m.rotation_angle()
            if rotation > 0:
                rotation_angle = (rotation_angle + 180) % 360
            rotation_speed = abs(rotation) * (m.offset_from_center() / max_module_distance)
            rotation_vector = Polar(rotation_speed, rotation_angle)

            module_states.append(target_vector + rotation_vector)
        
        top_speed = max(m.magnitude for m in module_states)
        if top_speed > 1:
            for m in module_states:
                m.magnitude /= top_speed

        for i, s in enumerate(module_states):
            if s.magnitude == 0:
                self.modules[i].setTargetSpeed(0)
            else:
                s.theta += 90
                self.modules[i].setState(s)
        
        self.feed()

        net_vector = sum((m.get_state_mps() for m in self.modules), start= Polar(0, 0))
        net_vector.theta += current_angle
        net_vector.magnitude *= 0.02 / len(self.modules)
        self._position += net_vector

    def initialize(self):
        for m in self.modules:
            m.setState(Polar(0, 90))
        self.feed()

    def brace(self):
        self.front_left.setState(Polar(0, -45))
        self.front_right.setState(Polar(0, 45))
        self.rear_left.setState(Polar(0, 45))
        self.rear_right.setState(Polar(0, -45))
        self.feed()

    def stopMotor(self):
        for m in self.modules:
            m.stopMotor()
        self.feed()

    def reset_position(self):
        self._position = Polar(0, 0)
    
    def position(self):
        trans = self._position.to_Translation2d()
        return Translation2d(-trans.X(), trans.Y())