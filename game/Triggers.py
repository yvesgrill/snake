import random, time, pygame, sys, os
from pygame.locals import *
import pygame.time
import logging

class Trigger:
    def check(self):
        pass
    def update(self):
        pass
    def reset(self):
        pass
    def start(self):
        pass
    
class FrameCountTrigger(Trigger):
    def __init__(self, frameFreq):
        self.frameFreq = frameFreq
        self.frameCount = 0
    def check(self):
        return self.frameCount >= self.frameFreq
    def update(self):
        if self.check():
            self.frameCount = 0
        self.frameCount += 1
    def reset(self):
        self.frameCount = 0
    def start(self):
        self.frameCount = 0
class TimeTrigger(Trigger):
    def __init__(self, delay):
        self.delay = delay
        self.time = 0
    def start(self):
        self.clock = pygame.time.Clock()
    def check(self):
        return self.time >= self.delay
    def update(self):
        logging.debug("Time=%d",self.time)
        if self.check():
            self.time = self.time - self.delay
        self.time += self.clock.tick() 
    def reset(self):
        self.clock = pygame.time.Clock()
        self.time = 0