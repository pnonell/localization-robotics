# Localization simulation

This projects simulates the execution of a robot which has to go through all goal positions to take photos of plants. First, it takes some random moves to locate itself and then it moves goal to goal. The simulation uses a Particle Filter to localize the robot and it is displayed with the library **Pygame**.

### Prerequisites

- Pyhton 3 (tested in 3.7)
- Pygame
- Scipy
- Math & Numpy

### Execution

To execute the simulation, run:

``python3 main.py``

### Scripts and resources

- ``map.json``: JSON file that groups the simulation variables, which will be readed by the modules.
- ``Robot.py``: class that includes the motion model and the motion commands needed to move through the goals.
- ``Localization.py``: localization module that includes the sensor model, and controls the set of particles needed to estimate the positon of the robot.
- ``Display.py``: graphical module that calls the pygame library to illustrate the simulation.
- ``assets/``: folder with the pictures needed to illustrate the simulation.
- ``Localization_simulation.mp4``: Video of an example of execution of the simulation.
