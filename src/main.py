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

ball = Signature (1, 1659, 2589, 2124, -4639, -4325, -4482, 5, 0)
Vis = Vision(Ports.PORT18)


brain.screen.print("Hello V5")

avg_width = 0
avg_y = 0

samples = 0

while brain.timer.value() < 10:
    objects = Vis.take_snapshot(ball, 1)

    if(not objects):
        continue
    
    brain.screen.clear_screen()
    brain.screen.set_fill_color(Color.YELLOW)
    brain.screen.draw_rectangle(objects[0].originX, objects[0].originY, objects[0].width, objects[0].height)

    samples += 1

    avg_y += objects[0].centerY
    avg_width += objects[0].width

    wait(0.0625, SECONDS)

print("\nWidth: {}\nY: {}".format(round(avg_width / samples, 3), round(avg_y / samples, 3)))


