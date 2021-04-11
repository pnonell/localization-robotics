import numpy as np
import scipy
import scipy.stats
import math

# auxiliar function
def compute_angular_diff(dist_x, dist_y, currentAngle):
    if dist_x != 0:
        angle = math.atan(dist_y / dist_x)
    else:
        if dist_y < 0:
            angle = -math.pi / 2
        else:
            angle = math.pi / 2

    # normalize angle between 0 and 2*pi
    if dist_x < 0:
        angle = math.pi + angle
    if angle < 0:
        angle = angle + math.pi * 2

    dif_angle = abs(currentAngle - angle)

    # normalize angle between 0 and pi
    if dif_angle > math.pi:
        dif_angle = 2*math.pi - dif_angle

    return math.degrees(dif_angle)

# Localization module
class Localization:
    def __init__(self, num, width, height, noise):

        # create uniform particles
        self.particles = np.empty([num, 3])
        self.particles[:, 0] = np.random.uniform(0, width, size=num)
        self.particles[:, 1] = np.random.uniform(0, height, size=num)
        self.particles[:, 2] = np.random.uniform(0, math.pi*2, size=num)

        # initialise weigths
        self.weights = np.ones(num)
        self.num_particles = num

        # noise stds
        self.move_std = noise["move_std"]
        self.rotate_std = noise["rotate_std"]
        self.sensor_std = noise["sensor_std"]

    def motion_update(self, dist, angle):
        # move particles
        dist_with_error = dist + np.random.randn(self.num_particles) * self.move_std
        self.particles[:, 0] = self.particles[:, 0] + np.cos(self.particles[:, 2]) * dist_with_error
        self.particles[:, 1] = self.particles[:, 1] + np.sin(self.particles[:, 2]) * dist_with_error

        # rotate particles
        self.particles[:, 2] = self.particles[:, 2] + angle + np.random.randn(self.num_particles) * self.rotate_std
        # normalize particle angles between 0 and 2*pi
        self.particles[self.particles[:,2] < 0, 2] += math.pi * 2
        self.particles[self.particles[:, 2] > math.pi * 2, 2] -= math.pi * 2

    def sensor_update(self, landmarks, currentPos, currentAngle):
        # sense landmarks
        measurements = np.empty(len(landmarks))
        for i, landmark in enumerate(landmarks):
            dist_x = currentPos[0] - landmark[0] + np.random.randn() * self.sensor_std
            dist_y = currentPos[1] - landmark[1] + np.random.randn() * self.sensor_std
            dif_angle = compute_angular_diff(dist_x, dist_y, currentAngle)
            # measured euclidean norm
            measurements[i] = np.sqrt(dist_x ** 2 + dist_y ** 2 + dif_angle ** 2)

        # update weights according to probabilities
        self.weights.fill(1.0)
        for i, landmark in enumerate(landmarks):
            dif_angles = np.empty(self.num_particles)
            for j, particle in enumerate(self.particles):
                dist_x = self.particles[j, 0] - landmark[0]
                dist_y = self.particles[j, 1] - landmark[1]
                dif_angles[j] = compute_angular_diff(dist_x, dist_y, self.particles[j, 2])

            # real euclidean norm
            real_distances = np.sqrt((self.particles[:, 0] - landmark[0]) ** 2 + (self.particles[:, 1] - landmark[1]) ** 2 + dif_angles ** 2)
            self.weights = self.weights * scipy.stats.norm(real_distances, 50).pdf(measurements[i])

        # normalize weights
        self.weights = self.weights/sum(self.weights)

    def resample(self):
        #compute indexes with higher probabilities
        new_indexes = np.random.choice(self.num_particles, self.num_particles, replace=True, p=self.weights)
        self.particles = self.particles[new_indexes]
        self.weights = self.weights[new_indexes]
        #normalize weights
        self.weights = self.weights/np.sum(self.weights)

    def estimate_position(self):
        # calculate estimated position with weighted average
        mean_x = np.average(self.particles[:, 0], weights=self.weights, axis=0)
        mean_y = np.average(self.particles[:, 1], weights=self.weights, axis=0)
        mean_angle = scipy.stats.circmean(self.particles[:, 2])

        return [mean_x, mean_y], mean_angle
