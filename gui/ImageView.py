import random, time, pygame, sys, os
from gui.NamedColors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *


class ImageView(Component):
    def __init__(self, name, position, dimension, image):
        super().__init__(name, position, dimension)
        self.image = image
    def update(self):
        super().update()
        icon = pygame.transform.scale(pygame.image.load(os.path.join('images', self.image)), self.get_dimension())
        self.backgroundLayer.blit(icon, (0, 0))
