import random, time, pygame, sys, os
from gui.Colors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *

class TextInput(Component):
    def __init__(self, id, position, dimension, placeHolder, className=None):
        super().__init__(id, position, dimension, className)
        self.placeHolder = placeHolder
        self.text = ''
    def update(self):
        super().update()
        surf = self.get_font().render(self.text,0,(0,0,0),None)
        #x = int((self.dimension.width-surf.get_width())/2)
        y = int((self.dimension.height-surf.get_height())/2)
        self.foregroundLayer.blit(surf, (0, y))
    def on_handle_event(self, event):
        #for event in events:
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.absoluteX()+self.dimension.width > event.pos[0] > self.absoluteX() and self.absoluteY()+self.dimension.height > event.pos[1]> self.absoluteY():
                self.click()
        self.update()        

