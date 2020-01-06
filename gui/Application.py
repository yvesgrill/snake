import random, time, pygame, sys, os
from gui.NamedColors import *
from pygame.locals import *
import pygame.mixer
from gui.Commons import Theme
from gui.Commons import Dimension
import logging

class Application:
    fpsClock = None
    WINDOWWIDTH = 688
    WINDOWHEIGHT = 700
    fps = 60
    theme = None
    def __init__(self, name, fps, theme = Theme("Default")):
        self.name = name
        Application.theme = theme
        Application.fps = fps
        pygame.init()
        pygame.mixer.init()
        info = pygame.display.Info()
        logging.debug("Info: %d %d",info.current_w,info.current_h)
        Application.fpsClock = pygame.time.Clock()
        self.display = pygame.display.set_mode((Application.WINDOWWIDTH, Application.WINDOWHEIGHT) )
        pygame.display.set_caption(self.name )
        info = pygame.display.Info()
        logging.debug("Info: %d %d",info.current_w,info.current_h)
        self.windows = []
        self.activeWindows = []
    def get_window(self,id) :
        for window in self.windows:
            if window.id == id:
                return window
        return None
    def show_window(self,id) :
        window = self.get_window(id)
        if window != None:
            window.show()
    def hide_window(self,id) :
        window = self.get_window(id)
        if window != None:
            window.hide()
    def activate_window(self,window) :
        if window in self.activeWindows:
            while self.activeWindows[-1] != window:
                self.activeWindows.pop()
        else:
            self.activeWindows.append(window)
    def desactivate_window(self,window) :
        if window == self.activeWindows[-1]:
           self.activeWindows.pop()
        window = self.get_current_window()
        if window != None:
            window.set_dirty(True)

    def add_window(self, window, activate=False) :
        self.windows.append(window) 
        window.application = self
        if window.dimension == None:
            window.dimension = Dimension(*self.display.get_size())
        if activate:
            self.activate_window(window)
    def remove_window(self, window) :
        if window in self.windows: 
            self.windows.remove(window) 
    def get_current_window(self):
        if len(self.activeWindows) == 0:
            return None
        return self.activeWindows[-1]
    def run(self):
        while self.get_current_window() != None:
            self.get_current_window().run()
        pygame.quit()
    def quit(self):
        self.activeWindows.clear()
