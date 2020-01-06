import random, time, pygame, sys, os
from gui.NamedColors import *
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
    def update(self):
        super().update()
        for component in self.components:
            component.update()
    def draw(self):
        for component in self.components:
            component.draw()
        super().draw()
        layers = []
        self.collect_layers(layers,['background','foreground','overlay'])
    def on_handle_event(self, event):
        super().on_handle_event(event)
        for component in self.components:
            component.on_handle_event(event)
    def collect_layers(self,layers, id=None):
        super().collect_layers(layers, ['background','foreground'])
        for component in self.components:
            component.collect_layers(layers,['background','foreground','overlay'])
        super().collect_layers(layers, ['overlay'])
    def set_dirty(self, dirty):
        super().set_dirty(dirty)
        for component in self.components:
            component.set_dirty(dirty)
