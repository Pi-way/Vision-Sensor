
class Robot:
    def __init__(self, right_motor, left_motor, max_accel) -> None:

        self.rightMotor = right_motor
        self.leftMotor = left_motor

        self.maxAccel = max_accel

        self.targetRight = 0
        self.currentRight = 0

        self.targetLeft = 0
        self.currentLeft = 0

    def setRightVel(self, velocity: float) -> None:
        self.targetRight = velocity

    def setLeftVel(self, velocity: float) -> None:
        self.targetLeft = velocity

    def updateDrive(self, dt) -> None:

        ActualAccel = (self.targetRight - self.currentRight) / dt
        if abs(ActualAccel) > self.maxAccel:
            self.currentRight += self.maxAccel * dt * GetSign(ActualAccel)
        else:
            self.currentRight = self.targetRight

        ActualAccel = (self.targetLeft - self.currentLeft) / dt
        if abs(ActualAccel) > self.maxAccel:
            self.currentLeft += self.maxAccel * dt * GetSign(ActualAccel)
        else:
            self.currentLeft = self.targetLeft

        self.rightMotor.set_velocity(self.currentRight, PERCENT)
        self.rightMotor.set_velocity(self.currentLeft, PERCENT)