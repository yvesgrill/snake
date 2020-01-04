import random, time, pygame, sys, os
from pygame.locals import *
import pygame.time
import gui 
import getpass
import logging
from operator import attrgetter

class Score:
    def __init__(self, value, player):
        self.value = value
        self.player = player
    def __str__(self):
        return self.player+':'+str(self.value) 
class HighestScores:
    def __init__(self, filename, maxSavedScores=10):
        self.scores = []
        self.maxSavedScores = maxSavedScores
        self.filename = filename 
        if os.path.isfile(filename):
            file = open(filename,"r")
            for line in file:
                line = line.rstrip('\n')
                if len(line) > 0:
                    data = line.split(',') 
                    score = Score(int(data[1]), data[0])
                    self.scores.append(score)
                    logging.debug('High score : %s', str(score))
            file.close()
    def add_score(self, newScore):
        if newScore.value > 0 :
            if len(self.scores) <= self.maxSavedScores:
                self.scores.append(newScore)
            else:
                minScore = min(self.scores,key=attrgetter('value'))
                if newScore.value > minScore.value:
                    self.scores.append(newScore)
                    self.scores.remove(minScore)
    def get_highest_score(self):
        if len(self.scores) == 0:
            username = getpass.getuser()
            return Score(0,username)
        maxScore = max(self.scores,key=attrgetter('value'))
        if maxScore == None:
            username = getpass.getuser()
            maxScore = Score(0, username)
        return maxScore
    def save(self):
        self.scores.sort(key=lambda x: x.value, reverse=True)

        file = open(self.filename,"w")
        index = 0
        for score in self.scores:
            if index >= self.maxSavedScores:
                break
            file.write(score.player+','+str(score.value)+'\n')
            index += 1 
        file.close()

class Game:
    def __init__(self, level=None):
        self.player = None
        username = getpass.getuser()
        self.score = Score(0, username)
        self.set_level(level)
    def new_play(self):
        username = getpass.getuser()
        self.score = Score(0, username)
    def set_level(self, level):
        if level != None:
            self.highestScores = HighestScores(level+"-hightscore.txt")
            self.level = level



