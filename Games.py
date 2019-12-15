import random, time, pygame, sys, os
from Env import *
from pygame.locals import *
import pygame.mixer

class Game:
    highScoreFilename = "hightscore.txt"
    window = None
    font= None
    fpsClock = None
    def __init__(self, name):
        self.name = name
        pygame.init()
        pygame.mixer.init()
        Game.font = pygame.font.Font(None, 32)
        Game.fpsClock = pygame.time.Clock()
        Game.window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption(self.name )
        self.screen = None
        self.screens={}
        return
    
    def setScreen(self,screen) :
        self.screen = self.screens[screen]
    def addScreen(self,screen) :
        self.screens[screen.name] = screen
        screen.game = self
    
    def run(self):

        while self.screen != None:
            self.screen.run()
        pygame.quit()

class Component:
    def __init__(self,name):
        self.parent = None
        self.name = name
    def draw(self):
        #print("Vous devez définir la méthode draw")
        pass
    def update(self, context):
        #print("Vous devez définir la méthode handleEvents")
        pass
        
class Position:
    def __init__(self, x, y):
        self.x = x
        self.xip = x*BOXSIZE+(GAMEAREA_ORIGINX+1)
        self.y = y
        self.yip = y*BOXSIZE+(GAMEAREA_ORIGINY+1)
    def xInPixel(self):
        return round(self.xip)
    def incrementXInPixel(self, n):
        self.xip = self.xip+n
#        return self.x*BOXSIZE+(GAMEAREA_ORIGINX+1)
    def yInPixel(self):
        return round(self.yip)
#        return self.y*BOXSIZE+(GAMEAREA_ORIGINY+1)
    def incrementYInPixel(self, n):
        self.yip = self.yip + n
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False
    def atRight(self):
        return Position(self.x+1,self.y)
    def atLeft(self):
        return Position(self.x-1,self.y)
    def atUp(self):
        return Position(self.x,self.y-1)
    def atDown(self):
        return Position(self.x,self.y+1)
    def setX(self, x) :
        self.x = x
        self.xip = x*BOXSIZE+(GAMEAREA_ORIGINX+1)
    def setY(self, y) :
        self.y = y
        self.yip = y*BOXSIZE+(GAMEAREA_ORIGINY+1)
    def reset(self):
        self.xip = self.x*BOXSIZE+(GAMEAREA_ORIGINX+1)
        self.yip = self.y*BOXSIZE+(GAMEAREA_ORIGINY+1)
    @staticmethod
    def convertPositionToPixel(x,y):
        return (x*BOXSIZE+(GAMEAREA_ORIGINX+1),y*BOXSIZE+(GAMEAREA_ORIGINY+1))

class Button(Component):
    def __init__(self, name, posx, posy, width, height, text, size, action):
        super().__init__(name)
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.Font(None, size)
        self.action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        box = pygame.Surface((self.width,self.height))
        if self.posx+self.width > mouse[0] > self.posx and self.posy+self.height > mouse[1] > self.posy:
            pygame.draw.rect(box, RED,(0,0,self.width,self.height))
        else:
            pygame.draw.rect(box, WHITE,(0,0,self.width,self.height))
        surf = self.font.render(self.text,0,(0,0,0),None)
        x = int((self.width-surf.get_width())/2)
        y = int((self.height-surf.get_height())/2)
        box.blit(surf, (x, y))
        self.parent.game.window.blit(box, (self.posx, self.posy))

    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and self.posx+self.width > event.pos[0] > self.posx and self.posy+self.height > event.pos[1]> self.posy:
                    self.click()

    def click(self):
        self.action()

class Screen:
    def __init__(self, name, width, height):
        self.components = []
        self.image = None
        self.game = None
        self.name = name
    def addComponent(self, component):
       self.components.append(component)
       component.parent = self
    def removeComponent(self, component):
        if component in self.components:
           self.components.remove(component)
           component.parent = None
    def draw(self):
        self.game.window.blit(self.image, (0,0))
        for component in self.components:
            component.draw()
    def update(self, context):
        for component in self.components:
            component.update(context)
    def run(self):
        self.flag = True
        while self.flag :
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.flag = False
                    self.game.screen = None
            self.update(events)
            self.draw()
            pygame.display.update()
            self.game.fpsClock.tick(FPS)     

class SpriteSheet:
    def __init__(self,filename, cellSize, n, m):
        self.sheetImage = pygame.image.load(filename).convert_alpha()
        self.cellSize = cellSize
        self.images = []
        for j in range(0,m):   
            self.images.append([])         
            for i in range(0,n):            
                x = i*32
                y = j*32
                self.images[j].append(self.sheetImage.subsurface(pygame.Rect(x,y,cellSize,cellSize)))
    def image(self,n,m) :
        return self.images[m][n]