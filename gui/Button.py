import random, time, pygame, sys, os
from gui.NamedColors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *
import logging

class Button(Component):
    def __init__(self, id, text, action, position=None, dimension=None, className=None):
        super().__init__(id, position, dimension, className)
        self.text = text
        self.action = action
    def update(self):
        mouse = pygame.mouse.get_pos()
        if self.absoluteX()+self.dimension.get_width() > mouse[0] > self.absoluteX() and self.absoluteY()+self.dimension.get_height() > mouse[1] > self.absoluteY():
            self.state = 'hover'
        else:
            self.state = None
        self.updateBackground()
        self.updateText(self.text, self.get_foreground_color())
    def on_handle_event(self, event):
        #for event in events:
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.absoluteX()+self.dimension.get_width() > event.pos[0] > self.absoluteX() and self.absoluteY()+self.dimension.get_height() > event.pos[1]> self.absoluteY():
                self.click()
        self.update()        
    def click(self):
        self.action()

