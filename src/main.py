# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Ren Hunter and Caleb Carlson                                 #
# 	Created:      2/3/2023, 12:54:01 PM                                        #
# 	Description:  A program that utilizes the V5 Vision sensor to pick up      #
#                 yellow balls and deliver them to a red box repeatedly.       #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

brain=Brain()
controller1 = Controller()

#signatures for box and ball:
ball = Signature (1, 957, 3277, 2117, -5771, -5265, -5518, 5, 0)
box = Signature (2, 11423, 14765, 13094, -1347, -415, -881, 5.4, 0)
Vis = Vision(Ports.PORT18, 50, ball, box)

Right = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
Left = Motor(Ports.PORT1, GearSetting.RATIO_18_1)

Lift = Motor(Ports.PORT20, GearSetting.RATIO_18_1)
Claw = Motor(Ports.PORT19, GearSetting.RATIO_18_1)
#---------------Functions----------------------

#global maximum porportional speed cap:
sc = 100

#Miscellaneous functions:
def GetSign(n):
    return 1 if n > 0 else -1

def Cap(n, c):
    return c * GetSign(n) if abs(n) > c else n

#function that will take vision sensor data and return the distance, in feet from the object:
def get_dist(y_value, width_value, ball = True):
    '''
    To make these rational functions, We used desmos to create a rational regression equation for data.
    the desmos graph isn't explained... but this is what we used:
    https://www.desmos.com/calculator/8ssznrxz4i
    '''
    if ball:

        #variables for rational functions:
        #y_value
        a_y = 204.574
        b_y = 1.43518
        c_y = 17.918

        #width_value
        a_w = 83.0135
        b_w = 1.26997
        c_w = -1.59619

        #plug into rationals
        distance_y = (a_y - b_y*(y_value     - c_y)) / (y_value     - c_y)
        distance_w = (a_w - b_w*(width_value - c_w)) / (width_value - c_w)

        #return average
        return (distance_y + distance_w) / 2

    else:
        #variables for rational functions:
        #y_value
        a_y = 146.157
        b_y = 1.31922
        c_y = 19.2805

        #width_value
        a_w = 213.159
        b_w = 0.981797
        c_w = 0.735323

        #plug into rationals
        distance_y = (a_y - b_y*(y_value     - c_y)) / (y_value     - c_y)
        distance_w = (a_w - b_w*(width_value - c_w)) / (width_value - c_w)

        #return average
        return (distance_y + distance_w) / 2

#function that takes a distance, and returns what x_value the object should be if it is directly in front of the robot
def get_expected_x(distance, ball = True):

    if ball:

        #variables for rational function:
        a = 49.8234
        b = 1.29971
        c = 147.8

        return (a / (distance + b)) + c
    else:

        #variables for rational function:
        a = 53.6009
        b = 1.34625
        c = 147.449

        return (a / (distance + b)) + c

#robot class to handle lifting, opening and closing claw, and also acceleration
class Robot:
    def __init__(self, right_motor: Motor, left_motor: Motor, claw_motor: Motor, lift_motor: Motor, max_accel, turn_correction, porportional_drive) -> None:

        self.rightMotor = right_motor
        self.leftMotor = left_motor
        self.lift = lift_motor
        self.claw = claw_motor

        self.maxAccel = max_accel

        self.targetRight = 0
        self.currentRight = 0

        self.targetLeft = 0
        self.currentLeft = 0

        self.turnCorrection = turn_correction
        self.porportionalDrive = porportional_drive

        self.thisTime = brain.timer.time(SECONDS)
        self.lastTime = self.thisTime

    def setRightVel(self, velocity: float) -> None:
        self.targetRight = velocity

    def setLeftVel(self, velocity: float) -> None:
        self.targetLeft = velocity

    def updateDrive(self) -> None:
        '''
        This update drive function will determine how fast the motors should spin based on target velocity, current velocity, and target acceleration
        The idea behind this is to prevent the robot from 'peeling out' by gently accelerating the robot
        '''

        self.lastTime = self.thisTime
        self.thisTime = brain.timer.time(SECONDS)

        dt: float = self.thisTime - self.lastTime

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
        self.leftMotor.set_velocity(self.currentLeft, PERCENT)

    def liftDown(self):
        Lift.spin_to_position(-608,DEGREES)

    def liftUp(self):
        Lift.spin_to_position(-180,DEGREES)

    def clawOpen(self):

        self.claw.spin(REVERSE, 6, VoltageUnits.VOLT)

        #wait until the claw is drawing more than 1.5 Amps
        while abs(self.claw.current(CurrentUnits.AMP)) < 1.5:
            wait(20, MSEC)
            #do nothing

        self.claw.spin(FORWARD, 0, VoltageUnits.VOLT)


    def clawClose(self):
        
        self.claw.spin(FORWARD, 6, VoltageUnits.VOLT)

        #wait until the claw is drawing more than 1.5 Amps
        while abs(self.claw.current(CurrentUnits.AMP)) < 1.5:
            wait(20, MSEC)
            #do nothing

        self.claw.spin(FORWARD, 0.5, VoltageUnits.VOLT)

#this function will take a snapshot with the vision sensor and return relavant data about the desired object
def find_object(_ball_ = True):

    objects = Vis.take_snapshot(ball if _ball_ else box)

    if objects:
        object = objects[0]
    else:
        object = False
    
    if object:

        distance = get_dist(object.centerY, object.width, _ball_)
        distance = -1 if distance < -1 else distance
        expectedX = get_expected_x(distance, _ball_)
        differenceOfX = object.centerX - expectedX

        if distance > 8:  
            #too far away
            return False

        return (distance, differenceOfX)

    return False

#this function will go towards the desired object.
def go_to_object(robot: Robot, _ball_ = True):
    
    objectWithinReach = False
    objectReached = False
    objectReachedStart = 0

    while not objectWithinReach:

        objectData = find_object(_ball_)

        if not objectData:
            
            #object is not seen, spin in a circle
            robot.setRightVel(-15)
            robot.setLeftVel(15)

        else:
            
            #we can see the object, so drive towards the object porportionally, while correcting our angle based off of expected x vs actual x
            robot.setRightVel(Cap(objectData[0] * robot.porportionalDrive, sc) - objectData[1] * robot.turnCorrection)
            robot.setLeftVel(Cap(objectData[0] * robot.porportionalDrive, sc) + objectData[1] * robot.turnCorrection)

            #the below statements are simply logic to make sure that the ball is not moving (relative to the robot) before it is picked up
            if (objectData[0] < 1.0 / 24.0) and (objectData[0] > -1) and not objectReached:
                objectReached = True
                objectReachedStart = brain.timer.time(SECONDS)

            if not (objectData[0] < 1.0 / 24.0) and (objectData[0] > -1) and objectReached:
                objectReached = False

            if objectReached and brain.timer.time(SECONDS) - objectReachedStart > 0.75:
                objectWithinReach = True
                robot.setRightVel(0)
                robot.setLeftVel(0)

            print(objectData)
   
def pick_up_ball(robot: Robot):
    robot.clawOpen()
    robot.liftDown()
    robot.clawClose()
    robot.liftUp()

def drop_ball_in_basket(robot: Robot):
    robot.clawOpen()

#this function will continuously update the robot class to ensure that the motors are driving at the desired velocity
def driveTask(robot):
    while True:
        robot.updateDrive()
        wait(50, MSEC)

def turn_around(robot: Robot):
    robot.setLeftVel(-50)
    robot.setRightVel(-50)
    wait(0.25, SECONDS)
    robot.setLeftVel(50)
    robot.setRightVel(-50)
    wait(0.75, SECONDS)
    robot.setLeftVel(0)
    robot.setRightVel(0)

if __name__ == "__main__":

    robot = Robot(Right, Left, Claw, Lift, 175, 0.075, 60)

    Right.set_velocity(0, PERCENT)
    Left.set_velocity(0, PERCENT)

    Right.spin(FORWARD)
    Left.spin(FORWARD)

    Right.set_stopping(BRAKE)
    Left.set_stopping(BRAKE)

    robot.liftUp()

    #start the driving thread for motor velocities
    drive_task = Thread(driveTask, (robot,))

    does_not_have_ball = True
    attempts = 0

    while True:

        while does_not_have_ball:

            go_to_object(robot)
            pick_up_ball(robot)

            #check that we are holding a ball
            if Claw.position(DEGREES) > 230:
                does_not_have_ball = True
            else:
                does_not_have_ball = False
            
            attempts += 1

            #if the robot has attempted too many times, turn around and look for a different ball
            if attempts >= 3:

                #nock balls around
                robot.liftDown()
                robot.setLeftVel(50)
                robot.setRightVel(50)
                wait(0.25, SECONDS)
                robot.setLeftVel(0)
                robot.setRightVel(0)

                #then turn around!
                turn_around(robot)
                robot.liftUp()
                attempts = 0
        
        attempts = 0

        does_not_have_ball = True
        go_to_object(robot, False)
        drop_ball_in_basket(robot)
        turn_around(robot)