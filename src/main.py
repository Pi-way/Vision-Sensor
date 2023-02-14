# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       S133020710                                                   #
# 	Created:      2/3/2023, 12:54:01 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()
controller1 = Controller()

ball = Signature (1, 957, 3277, 2117, -5771, -5265, -5518, 5, 0)
Vis = Vision(Ports.PORT18, 50, ball)

Right = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
Left = Motor(Ports.PORT1, GearSetting.RATIO_18_1)

Lift = Motor(Ports.PORT14, GearSetting.RATIO_18_1)
#---------------Functions----------------------

def GetSign(n):
    return 1 if n > 0 else -1

def get_dist(ball_y, ball_width):
    #first get the distance from the ball_y location:

    #variables for rational functions:
    #ball_y
    a_y = 204.574
    b_y = 1.43518
    c_y = 17.918

    #ball_width
    a_w = 83.0135
    b_w = 1.26997
    c_w = -1.59619

    #plug into rationals
    distance_y = (a_y - b_y*(ball_y     - c_y)) / (ball_y     - c_y)
    distance_w = (a_w - b_w*(ball_width - c_w)) / (ball_width - c_w)

    #return average
    return (distance_y + distance_w) / 2

def get_expected_x(distance):
    #first get the expected centerX from distance

    #variables for rational function:
    a = 49.8234
    b = 1.29971
    c = 147.8

    return (a / (distance + b)) + c

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

    def liftDown(self):
        Lift.spin_to_position(-608,DEGREES)

    def liftUp(self):
        Lift.spin_to_position(-60,DEGREES)

    def clawOpen(self):
        pass

    def clawClosed(self):
        pass


def find_Ball():

    Vis.take_snapshot(ball)
    object = Vis.largest_object()

    if object:

        distance = get_dist(object.centerY, object.width)
        expectedX = get_expected_x(distance)
        differenceOfX = object.centerX - expectedX

        return (distance, differenceOfX)

    else:

        return False

# while True:

#     #find ball

#     Right.spin(FORWARD)
#     Left.spin(FORWARD)

#     Right.set_velocity(-10, PERCENT)
#     Left.set_velocity(10, PERCENT)

#     Vis.take_snapshot(ball)
#     object = Vis.largest_object()

#     while not object:
#         Vis.take_snapshot(ball)
#         object = Vis.largest_object()
#         wait(20, MSEC)

#     # Turn to ball
#     brain.screen.set_pen_color(Color.YELLOW)

#     turn_correction = 0.25
#     porportional_drive = 60

#     OutputRight = 0
#     OutputLeft = 0

#     ActualAccel = 0
#     MaxAccel = 300

#     RequestedRight = 0
#     RequestedLeft = 0

#     ThisTime = brain.timer.time(SECONDS)
#     LastTime = ThisTime

#     DeltaTime = 0.0

#     wait(20, MSEC)

#     while True:

#         LastTime = ThisTime
#         ThisTime = brain.timer.time(SECONDS)

#         DeltaTime = ThisTime - LastTime

#         #get expected x
#         if object:
#             distance = get_dist(object.centerY, object.width)
#             expectedX = get_expected_x(distance)

#             differenceOfX = object.centerX - expectedX

#             RequestedRight = distance * porportional_drive - differenceOfX * turn_correction
#             RequestedLeft = distance * porportional_drive + differenceOfX * turn_correction

#         else:
#             RequestedRight = -10
#             RecursionError = 10



#         ActualAccel = (RequestedRight - OutputRight) / DeltaTime

#         if abs(ActualAccel) > MaxAccel:
#             OutputRight += MaxAccel * DeltaTime * GetSign(ActualAccel)
#         else:
#             OutputRight = RequestedRight


#         ActualAccel = (RequestedLeft - OutputLeft) / DeltaTime
#         if abs(ActualAccel) > MaxAccel:
#             OutputLeft += MaxAccel * DeltaTime *  GetSign(ActualAccel)
#         else:
#             OutputLeft = RequestedLeft

#         Right.set_velocity(OutputRight, PERCENT)
#         Left.set_velocity(OutputLeft, PERCENT)

#         wait(20, MSEC)

#         brain.screen.clear_screen()
#         brain.screen.set_cursor(1, 1)

#         brain.screen.draw_rectangle(object.originX, object.originY, object.width, object.height)

#         brain.screen.print(round(distance, 3))

#         null = Vis.take_snapshot(ball)
#         object = Vis.largest_object()

def go_to_ball(robot: Robot):
    
    ballWithinReach = False

    while not ballWithinReach:

        ballData = find_Ball()

        if not ballData:
            robot.setRightVel(-25)
            robot.setLeftVel(25)

def pick_up_ball(robot: Robot):
    pass

def go_to_basket(robot: Robot):
    pass

def drop_ball_in_basket(robot: Robot):
    pass

if __name__ == "main":

    robot = Robot(Right, Left, 300)

    while True:
        go_to_ball(robot)
        pick_up_ball(robot)
        go_to_basket(robot)
        drop_ball_in_basket(robot)