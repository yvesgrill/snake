import random, time, pygame, sys, os
from gui.Colors import *
from pygame.locals import *
from gui.Commons import *
from gui.Application import *


class Component:
    def __init__(self, id, position, dimension, className=None):
        self.container = None
        self.id = id
        self.className = className
        themeStyle = Application.theme.get_style(self.get_id(),self.get_class(),self.__class__.__name__)
        if position != None:
            self.position = Position(*position)
        else:
            self.position = Position(0,0)
        if dimension != None:
            self.dimension = Dimension(*dimension)    
        else:
            self.dimension = themeStyle.dimension
        self.style = Style()
        self.style.color = themeStyle.color
        self.style.font.copy(themeStyle.font)
        self.style.background.copy(themeStyle.background)
        self.realized = False
        self.__font = None
        self.enabled = True
    def realize(self):
        print("Realize component ",self.id)
        if not self.realized:
            self.surface = pygame.Surface(self.get_dimension())
            self.update()
            self.realized = True
    def update(self):
        self.surface.fill(self.style.background.color.to_tuple())
        if self.style.background.image != None:
            image = pygame.transform.scale(pygame.image.load(os.path.join('images', self.style.background.image)).convert(), self.get_dimension())
            self.surface.blit(image, (0, 0))
    def draw(self):
        print("Draw component ",self.id, self.style.background.color.to_tuple(), self.style.background.image)
        if self.container == None:
            self.get_application().display.blit(self.surface, (self.absoluteX(), self.absoluteY()))
        else:
            self.container.surface.blit(self.surface, self.get_position())
    def handle_event(self, event):
        if self.enabled :
            self.on_handle_event(event)
    def on_handle_event(self, event):
        pass
    def absoluteX(self):
        if self.container == None:
            return self.position.x
        else:
            return self.position.x+self.container.position.x
    def absoluteY(self):
        if self.container == None:
            return self.position.y
        else:
            return self.position.y+self.container.position.y
    def get_position(self):
        return self.position.to_tuple()
    def get_dimension(self):
        return self.dimension.to_tuple()
    def get_bounds(self):
        return (self.position.x,self.position.y,self.dimension.width,self.dimension.height)
    def get_font(self):
        if self.style.font == None:
            return self.container.get_font()
        if self.__font == None:
            self.__font = Application.theme.get_font(self.style.font)
        return self.__font
    def get_application(self):
        if self.container != None:
            return self.container.get_application()
        return None
    def get_id(self):
        return '#'+self.id
    def get_class(self):
        if self.className != None:
            return '.'+self.className
        return None
