import math
import numpy as np
from Localization import Localization


class Robot:

    def __init__(self, map, display):

        # environment inits
        self.landmarks = map["landmarks"]
        self.goals = map["goals"]
        self.currentGoal = 0
        self.currentPos = map["initial_position"]
        self.currentAngle = map["initial_angle"]

        self.num_particles = map["num_particles"]

        self.dist_per_frame = map["distance_per_frame"]
        self.rot_per_frame = math.radians(map["rotation_per_frame"])

        # noise stds
        self.move_std = map["noise"]["move_std"]
        self.rotate_std = map["noise"]["rotate_std"]

        # display init
        self.display = display
        self.cmd_msg = "Waiting for commands..."

        # localization
        self.localization = Localization(self.num_particles, map["dimensions"]["width"], map["dimensions"]["height"], map["noise"])

        #estimated positions
        self.estimatedPos, self.estimatedAngle = self.localization.estimate_position()


    def move(self, distance):
        frames = int(distance / self.dist_per_frame)

        # movement to the calculated point
        for i in range(frames):
            # error is added at each frame
            dist_with_noise = self.dist_per_frame + np.random.randn() * self.move_std

            incx = math.cos(self.currentAngle) * dist_with_noise
            incy = math.sin(self.currentAngle) * dist_with_noise

            # motion update (robot and particles)
            self.currentPos = [self.currentPos[0] + incx, self.currentPos[1] + incy]
            self.localization.motion_update(self.dist_per_frame, 0)
            self.estimatedPos, self.estimatedAngle = self.localization.estimate_position()

            self.display.drawFrame(self)

        # sense and update
        self.localization.sensor_update(self.landmarks, self.currentPos, self.currentAngle)
        self.localization.resample()

        # estimate position
        self.estimatedPos, self.estimatedAngle = self.localization.estimate_position()

    def rotate(self, angle):
        # calculate difference and direction of rotation
        if angle > self.estimatedAngle:
            if angle - self.estimatedAngle <= math.pi:
                dif_angle = angle - self.estimatedAngle
                dir_rot = 1
            else:
                dif_angle = 2 * math.pi - (angle - self.estimatedAngle)
                dir_rot = -1
        else:
            if self.estimatedAngle - angle <= math.pi:
                dif_angle = self.estimatedAngle - angle
                dir_rot = -1
            else:
                dif_angle = 2 * math.pi - (self.estimatedAngle - angle)
                dir_rot = 1

        frames = int(dif_angle / self.rot_per_frame)

        # rotation to calculated angle
        for i in range(frames):
            # add noise
            rot_with_noise = self.rot_per_frame + np.random.randn() * self.rotate_std

            # motion update
            self.currentAngle = self.currentAngle + rot_with_noise * dir_rot
            if self.currentAngle < 0:
                self.currentAngle = self.currentAngle + math.pi * 2
            if self.currentAngle >= math.pi * 2:
                self.currentAngle = self.currentAngle - math.pi * 2

            self.localization.motion_update(0, self.rot_per_frame*dir_rot)
            self.estimatedPos, self.estimatedAngle = self.localization.estimate_position()

            self.display.drawFrame(self)

        # sense and update
        self.localization.sensor_update(self.landmarks, self.currentPos, self.currentAngle)
        self.localization.resample()

        # estimate position
        self.estimatedPos, self.estimatedAngle = self.localization.estimate_position()

    def random_moves(self):
        self.cmd_msg = "Taking random moves..."

        rand_rot = np.random.uniform(0, 2*math.pi)
        rand_dist = np.random.uniform(0, 100)
        self.rotate(rand_rot)
        self.move(rand_dist)

    # main execution loop
    def begin(self):

        while len(self.goals) > self.currentGoal:

            self.display.drawFrame(self)

            # check position
            difx = self.goals[self.currentGoal][0] - self.estimatedPos[0]
            dify = self.goals[self.currentGoal][1] - self.estimatedPos[1]

            if abs(difx) < 10 and abs(dify) < 10:
                print("Position reached, rotate to plant")
                orientated = False

                # rotate to plant
                while not orientated:
                    # get angle of orientation to plant
                    difx = self.landmarks[self.currentGoal][0] - self.estimatedPos[0]
                    dify = self.landmarks[self.currentGoal][1] - self.estimatedPos[1]

                    if difx != 0:
                        angle = math.atan(dify / difx)
                    else:
                        if dify < 0:
                            angle = -math.pi / 2
                        else:
                            angle = -math.pi / 2

                    # normalize angle between 0 and 2*pi
                    if difx < 0:
                        angle = math.pi + angle
                    if angle < 0:
                        angle = angle + math.pi * 2

                    self.cmd_msg = "Rotating to plant..."
                    self.rotate(angle)

                    if abs(self.estimatedAngle - angle) < math.pi / 50:
                        orientated = True

                print("Goal reached! Take photo.")
                self.cmd_msg = "Taking photo..."
                self.currentGoal += 1
            else:
                print("Move to goal")

                # rotate to position
                if difx != 0:
                    angle = math.atan(dify / difx)
                else:
                    if dify < 0:
                        angle = -math.pi/2
                    else:
                        angle = -math.pi / 2

                # normalize angle between 0 and 2*pi
                if difx < 0:
                    angle = math.pi + angle
                if angle < 0:
                    angle = angle + math.pi * 2

                self.cmd_msg = "Rotating to goal..."
                self.rotate(angle)

                # move to position
                distance = math.sqrt(difx ** 2 + dify ** 2)

                # cut long distances to avoid big decompensation with the estimated position
                if distance > 100:
                    distance = 100

                self.cmd_msg = "Moving to goal..."
                self.move(distance)

    def finish(self):
        self.cmd_msg = "All goals achieved!"

        # wait 50 frames before closing window
        for i in range(50):
            self.display.drawFrame(self)

        self.display.finish()
