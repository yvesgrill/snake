import random, time, pygame, sys, os
from gui.Colors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *



class Label(Component):
    def __init__(self, name, position, dimension, text='') :
        super().__init__(name, position, dimension)
        self.__text = text
    def update(self):
        super().update()
        font = self.get_font()
        surf = font.render(self.__text,0,(0,0,0),None)
        x = int((self.dimension.width-surf.get_width())/2)
        y = int((self.dimension.height-surf.get_height())/2)
        self.surface.blit(surf, (x, y))
    def set_text(self,text) :
        self.__text = text


