import os  # to be able to escape full screen
import math
import random  # to randomize initial orbit and velocity
import pygame as pg

# color variables
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LT_BLUE = (173, 216, 230)


class Satellite(pg.sprite.Sprite):  # inherits from a pygame base class for game objects
    """
    Satellite object that rotates to face the planet, and crashes andd burns.
    """

    def __init__(self, background):
        # path of satellite will be drawn on the background object
        super().__init__()
        # background object on which the satellite path will be drawn
        self.background = background
        # convert images to a pygame format
        self.image_sat = pg.image.load(
            "satellite.png").convert()  # default image
        # converting is much more efficient thaan leaving as png
        self.image_crash = pg.image.load("satellite_crash_40x33.png").convert()
        self.image = self.image_sat
        self.rect = self.image.get_rect()  # pygame places sprites on rectangular objects
        # sets black to be transparent so as not to cover the planet image
        self.image.set_colorkey(BLACK)

        # initialize range of intial satellite position
        self.x = random.randrange(315, 425)
        # gravity will determine the y direction
        self.y = random.randrange(70, 180)
        # initial velocity low enough that satellite can't escape
        # < 0: counterclockwise     > 0: clockwise
        self.dx = random.choice([-3, 3])
        self.dy = 0
        self.heading = 0  # initialize dish orientation
        self.fuel = 100
        self.mass = 1  # mass factor of satellite in gravity equation
        self.distance = 0  # initializes distance between satellite and planet
        self.thrust = pg.mixer.Sound("thrust_audio.ogg")  # thrust sound
        self.thrust.set_volume(0.07)  # between 0 and 1

    def thruster(self, dx, dy):
        """
        Execute actions associated with firing thrusters.
        """
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()

    def check_keys(self):
        """
        Check if user press arrow key to caall thruster() method.
        """

        keys = pg.key.get_pressed()

        # fire thrusters, update velocities
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)

    def locate(self, planet):
        """
        Calculate the distance and heading (used to point satellite dish at planet) from the satellite to the planet.
        """

        px, py = planet.x, planet.y  # position of planet
        dist_x = self.x - px
        dist_y = self.y - py

        '''
           dist_x
        S - - --        S: satellite
         \     |
          \    |
           \ t | dist_y
            \  |
             \ |
              \|
               P        P: planet
        '''
        planet_dir_radians = math.atan2(
            dist_x, dist_y)  # get the angle t in the diagram above in radians
        self.heading = planet_dir_radians * 180 / math.pi  # convert angle to degrees
        # bottom of satellite image points toward planet by default so rotate to point the dish at the planet (clockwise)
        # note: this just changes the heading attribute, the actual image is rotated accordingly in the rotate() method
        self.heading -= 90
        # calculate the distance between satellite and planet (hypotenuse of triangle in above diagram)
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        """
        Rotate satellite so the dish faces the planet.
        """
        # rotate image and store in separate variable so as not to degrade original
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        """
        Update satellite's position and draw a line to trace its orbital path.
        """

        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        # draw on the sprite background object a line connecting the sprite's last and current locations
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        """
        Update the satellite object during the game.
        """

        self.check_keys()  # check if keys were pressed
        self.rotate()  # keep satellite facing the planet
        self.path()  # draw satellite orbit path
        # keep track of satellite sprite location
        self.rect.center = (self.x, self.y)

        # change satellite image to red if in atmosphere
        if self.dx == 0 and self.y == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)


class Planet(pg.sprite.Sprite):
    """
    Planet object that rotates and projects gravity field.
    """

    def __init__(self):
        super().__init__()
        # load and convert images to pygame format
        self.image_mars = pg.image.load("mars.png").convert()
        self.image_water = pg.image.load("mars_water.png").convert()

        # scale down planet image and store in separate variable so as not to degrade original
        self.image_copy = pg.transform.scale(self.image_mars, (100, 100))
        self.image_copy.set_colorkey(BLACK)
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy

        self.mass = 2000
        # set center of planet image to be center of game screen size
        self.x = 400
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        """
        Rotate the planet image with each game loop.
        """

        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        # because of the rectangular image, the rect object will expand as the planet rotates so we reassign the center
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        """
        Calculate impact of planet's gravity on the satellite.
        """

        G = 1.0  # gravitational constant for the game
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y

        distance = math.hypot(dist_x, dist_y)
        dist_x /= distance
        dist_y /= distance

        # apply gravity
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)

    def update(self):
        """
        Call the rotate method.
        """
        self.rotate()
