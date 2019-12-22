import random, time, pygame, sys, os
from Colors import *
from pygame.locals import *
import pygame.mixer

class Theme:
    BACKGROUND = "backgroung"
    FOREGROUND = "foregroung"
    def __init__(self, font = None, bgColor = NamedColors.WHITE, fgColor = NamedColors.BLACK):
        self.font = font
        self.colors = {}
        self.colors[Theme.BACKGROUND] = bgColor
        self.colors[Theme.FOREGROUND] = fgColor

class Game:
    highScoreFilename = "hightscore.txt"
    window = None
    font= None
    fpsClock = None
    WINDOWWIDTH = 800
    WINDOWHEIGHT = 840
    fps = 60
    theme = None
    def __init__(self, name, fps, theme = Theme()):
        self.name = name
        Game.theme = theme
        Game.fps = fps
        pygame.init()
        pygame.mixer.init()
        Game.font = pygame.font.Font(None, 32)
        Game.fpsClock = pygame.time.Clock()
        Game.window = pygame.display.set_mode((Game.WINDOWWIDTH, Game.WINDOWHEIGHT))
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
    def __init__(self, name, posx, posy, parent=None):
        self.parent = parent
        self.name = name
        self.x = posx
        self.y = posy    
    def draw(self):
        #print("Vous devez définir la méthode draw")
        pass
    def update(self, context):
        #print("Vous devez définir la méthode handleEvents")
        pass
    def absoluteX(self):
        if self.parent == None:
            return self.x
        else:
            return self.x+self.parent.x
    def absoluteY(self):
        if self.parent == None:
            return self.y
        else:
            return self.y+self.parent.y
        

class Button(Component):
    def __init__(self, name, posx, posy, width, height, text, size, action):
        super().__init__(name, posx, posy)
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.Font(None, size)
        self.action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        box = pygame.Surface((self.width,self.height))
        if self.absoluteX()+self.width > mouse[0] > self.absoluteX() and self.absoluteY()+self.height > mouse[1] > self.absoluteY():
            pygame.draw.rect(box, NamedColors.RED,(0,0,self.width,self.height))
        else:
            pygame.draw.rect(box, NamedColors.WHITE,(0,0,self.width,self.height))
        surf = self.font.render(self.text,0,(0,0,0),None)
        x = int((self.width-surf.get_width())/2)
        y = int((self.height-surf.get_height())/2)
        box.blit(surf, (x, y))
        Game.window.blit(box, (self.absoluteX(), self.absoluteY()))

    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and self.absoluteX()+self.width > event.pos[0] > self.absoluteX() and self.absoluteY()+self.height > event.pos[1]> self.absoluteY():
                    self.click()

    def click(self):
        self.action()

class Container(Component):
    def __init__(self, name, posx, posy):
        super().__init__(name, posx, posy)
        self.components = []
        self.posx = posx
        self.posy = posy
    def addComponent(self, component):
       self.components.append(component)
       component.parent = self
    def removeComponent(self, component):
        if component in self.components:
           self.components.remove(component)
           component.parent = None
    def draw(self):
        for component in self.components:
            component.draw()
    def update(self, context):
        for component in self.components:
            component.update(context)

class Screen(Container):
    def __init__(self, name):
        super().__init__(name, 0, 0)
        self.image = None
        self.image = pygame.Surface((Game.WINDOWWIDTH, Game.WINDOWHEIGHT))
        self.image.fill(Game.theme.colors[Theme.BACKGROUND])
        self.game = None
    def draw(self):
        self.game.window.blit(self.image, (0,0))
        super().draw()
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
            self.game.fpsClock.tick(Game.fps)     

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