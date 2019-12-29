import random, time, pygame, sys, os
from gui.Colors import *
from gui.Component import *
from pygame.locals import *
import pygame.mixer


class Container(Component):
    def __init__(self, id, position,dimension):
        super().__init__(id, position, dimension)
        self.components = []
    def add_component(self, component):
       self.components.append(component)
       component.container = self
       if self.realized:
           component.realize()
    def remove_component(self, component):
        if component in self.components:
           self.components.remove(component)
           component.container = None
    def realize(self):
        super().realize()
        for component in self.components:
            component.realize()
    def draw(self):
        for component in self.components:
            component.draw()
        super().draw()
    def on_handle_event(self, event):
        for component in self.components:
            component.on_handle_event(event)

