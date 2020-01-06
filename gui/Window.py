import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
from gui.NamedColors import *
from gui.Container import *
from gui.Application import *
from gui.Commons import *


class Window(Container):
    def __init__(self, id, position=None, dimension=None):
        super().__init__(id, position, dimension)
        self.application = None
    def run(self):
        if not self.realized:
            self.realize()
        flag = self.is_current()
        while flag :
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.application.quit()
                self.on_handle_event(event)
            event = pygame.event.Event(pygame.USEREVENT, code="refresh", pos=(0,0), description="Sketch startup")
            self.on_handle_event(event)
            self.update()
            self.draw()
            #pygame.display.update()
            self.application.fpsClock.tick(Application.fps)   
            flag = self.is_current()  
    def is_current(self):
        return self.application.get_current_window() == self
    def hide(self):
        self.application.desactivate_window(self)
    def show(self):
        self.set_dirty(True)
        self.realize()
        self.application.activate_window(self)
    def get_application(self):
        return self.application
    def draw(self):       
        #super().draw()
        layers = []
        self.collect_layers(layers)
        #print("Nb layers=",len(layers))
        #for layer in layers:
        #    print(layer)
        surfaces = []
        areas = []
        for layer in layers:
            surfaces.append(layer.to_tuple())
            areas.append(layer.area)
        self.application.display.blits(surfaces)
        pygame.display.update(areas)

