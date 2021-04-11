from Robot import Robot
from Display import Display
import json

if __name__ == "__main__":
    # load json and initialize execution
    with open('map.json') as json_file:
        map = json.load(json_file)

    display = Display(map["dimensions"]["width"], map["dimensions"]["height"], map["msec_per_frame"])
    robot = Robot(map, display)

    # random moves
    robot.random_moves()
    robot.random_moves()
    robot.random_moves()

    # main loop
    robot.begin()

    # end execution
    robot.finish()
