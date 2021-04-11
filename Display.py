import pygame
import math


class Display:

    def __init__(self, display_width, display_height, msec_per_frame):

        self.width = display_width
        self.height = display_height

        pygame.init()
        self.clock = pygame.time.Clock()
        self.gameDisplay = pygame.display.set_mode((self.width + 300, self.height))
        pygame.display.set_caption('Localization simulation')
        self.robotImg = pygame.transform.scale(pygame.image.load('assets/rd2d.png'), (50, 50))
        self.w_arrowImg = pygame.transform.scale(pygame.image.load('assets/particle.png'), (25, 25))
        self.r_arrowImg = pygame.transform.scale(pygame.image.load('assets/estimated.png'), (25, 25))
        self.g_arrowImg = pygame.transform.scale(pygame.image.load('assets/position.png'), (25, 25))
        self.plantImg = pygame.transform.scale(pygame.image.load('assets/plant.png'), (70, 70))

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20)
        self.font2 = pygame.font.SysFont("lucidasansroman", 16)

        self.msec_per_frame = msec_per_frame

    # draw everything
    def drawFrame(self, robot):
        self.gameDisplay.fill((127, 127, 127))

        # landmarks
        for i, landmark in enumerate(robot.landmarks):
            if i < robot.currentGoal:
                color = (0, 200, 0)
            else:
                color = (0, 0, 255)
            pygame.draw.circle(self.gameDisplay, color, landmark, 15)
            self.gameDisplay.blit(self.plantImg, (int(landmark[0] - self.plantImg.get_size()[0]/2), int(landmark[1] - self.plantImg.get_size()[1]/2)))

        # goals
        for goal in robot.goals:
            pygame.draw.circle(self.gameDisplay, (255, 255, 255), goal, 1)
            pygame.draw.circle(self.gameDisplay, (255, 255, 255), goal, 10, width=1)

        # robot
        self.blitRotate(self.gameDisplay, self.robotImg, (int(robot.currentPos[0]), int(robot.currentPos[1])),
                   (int(self.robotImg.get_size()[0] / 2), int(self.robotImg.get_size()[1] / 2)), robot.currentAngle)

        #particles
        for particle in robot.localization.particles:
            self.blitRotate(self.gameDisplay, self.w_arrowImg, (int(particle[0]), int(particle[1])),
                       (int(self.w_arrowImg.get_size()[0] / 2), int(self.w_arrowImg.get_size()[1] / 2)), particle[2])

        # real position
        self.blitRotate(self.gameDisplay, self.g_arrowImg, (int(robot.currentPos[0]), int(robot.currentPos[1])),
                        (int(self.g_arrowImg.get_size()[0] / 2), int(self.g_arrowImg.get_size()[1] / 2)),
                        robot.currentAngle)

        # estimated position
        self.blitRotate(self.gameDisplay, self.r_arrowImg, (int(robot.estimatedPos[0]), int(robot.estimatedPos[1])),
                        (int(self.r_arrowImg.get_size()[0] / 2), int(self.r_arrowImg.get_size()[1] / 2)), robot.estimatedAngle)


        #legend
        pygame.draw.rect(self.gameDisplay, (0,0,0), (self.width, 0, 300, self.height))
        pygame.draw.circle(self.gameDisplay, (0,0,255), (self.width + 50, 50), 15)
        self.gameDisplay.blit(self.font.render('Landmark', False, (255,255,255)), (self.width + 100, 37))
        pygame.draw.circle(self.gameDisplay, (0,127,0), (self.width + 50, 100), 15)
        self.gameDisplay.blit(self.font.render('Landmark visited', False, (255,255,255)), (self.width + 100, 87))
        pygame.draw.circle(self.gameDisplay, (255,255,255), (self.width + 50, 150), 1)
        pygame.draw.circle(self.gameDisplay, (255,255,255), (self.width + 50, 150), 10, width=1)
        self.gameDisplay.blit(self.font.render('Goal', False, (255,255,255)), (self.width + 100, 137))
        self.gameDisplay.blit(self.g_arrowImg, (self.width + 37, 180))
        self.gameDisplay.blit(self.font.render('Real position', False, (255, 255, 255)), (self.width + 100, 187))
        self.gameDisplay.blit(self.r_arrowImg, (self.width + 37, 230))
        self.gameDisplay.blit(self.font.render('Estimated position', False, (255, 255, 255)), (self.width + 100, 237))
        self.gameDisplay.blit(self.w_arrowImg, (self.width + 37, 280))
        self.gameDisplay.blit(self.font.render('Particle', False, (255, 255, 255)), (self.width + 100, 287))

        self.gameDisplay.blit(self.font2.render(robot.cmd_msg, False, (0, 200, 0)), (self.width + 50, 700))

        pygame.display.update()

        self.clock.tick(self.msec_per_frame)

    # source: https://stackoverflow.com/a/54714144/13549725
    def blitRotate(self, surf, image, pos, originPos, a):
        angle = 270 - math.degrees(a)

        # calculate the axis aligned bounding box of the rotated image
        w, h = image.get_size()
        box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

        # calculate the translation of the pivot
        pivot = pygame.math.Vector2(originPos[0], -originPos[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot

        # calculate the upper left origin of the rotated image
        origin = (pos[0] - originPos[0] + min_box[0] - pivot_move[0], pos[1] - originPos[1] - max_box[1] + pivot_move[1])

        # get a rotated image
        rotated_image = pygame.transform.rotate(image, angle)

        # rotate and blit the image
        surf.blit(rotated_image, origin)

    def finish(self):
        print("Finish")
        pygame.quit()
