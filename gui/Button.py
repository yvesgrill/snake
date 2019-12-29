import random, time, pygame, sys, os
from gui.Colors import *
from pygame.locals import *
import pygame.mixer
from gui.Component import *

class Button(Component):
    def __init__(self, id, position, dimension, text, action, className=None):
        super().__init__(id, position, dimension, className)
        self.text = text
        self.action = action
    def update(self):
        mouse = pygame.mouse.get_pos()
        if self.absoluteX()+self.dimension.width > mouse[0] > self.absoluteX() and self.absoluteY()+self.dimension.height > mouse[1] > self.absoluteY():
            pygame.draw.rect(self.surface, RED.to_tuple(),(0,0,self.dimension.width,self.dimension.height))
        else:
            pygame.draw.rect(self.surface, self.style.background.color.to_tuple(),(0,0,self.dimension.width,self.dimension.height))
        surf = self.get_font().render(self.text,0,(0,0,0),None)
        x = int((self.dimension.width-surf.get_width())/2)
        y = int((self.dimension.height-surf.get_height())/2)
        self.surface.blit(surf, (x, y))
    def on_handle_event(self, event):
        #for event in events:
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.absoluteX()+self.dimension.width > event.pos[0] > self.absoluteX() and self.absoluteY()+self.dimension.height > event.pos[1]> self.absoluteY():
                self.click()
        self.update()        
    def click(self):
        self.action()

