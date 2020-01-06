import random, time, pygame, sys, os
from gui.NamedColors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *



class Label(Component):
    def __init__(self, name, position, dimension, text='', className=None) :
        super().__init__(name, position, dimension, className)
        self.__text = text
    def update(self):
        super().update()
    def set_text(self,text) :
        self.__text = text
        self.updateText(self.__text, self.get_foreground_color())
    def realize(self):
        super().realize()
        self.updateText(self.__text, self.get_foreground_color())

