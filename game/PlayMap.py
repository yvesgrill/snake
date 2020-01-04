import random, time, pygame, sys, os
from pygame.locals import *

class Cell:
    SIZE = 32
    def __init__(self, i, j, map, blocking = False):
        #super().__init__("Cell("+str(i)+","+str(j)+")", i*Cell.SIZE, j*Cell.SIZE)
        self.i = i
        self.j = j
        self.map = map
        self.imageId = None
        self.x = i*Cell.SIZE
        self.y = j*Cell.SIZE
        self.blocking = blocking
        self.drawn = False

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.i == other.i and self.j == other.j
        return False
    def __str__(self):
        return "Cell("+str(self.i)+","+str(self.j)+")"
    def atRight(self):
        return self.at(1,0)
    def atLeft(self):
        return self.at(-1,0)
    def atUp(self):
        return self.at(0,-1)
    def atDown(self):
        return self.at(0,1)
    def at(self, deltaI, deltaJ):
        i = self.i+deltaI
        j = self.j+deltaJ
        if i >= self.map.width:
            i = 0
        if i < 0:
            i = self.map.width-1
        if j >= self.map.height:
            j = 0
        if j < 0:
            j = self.map.height-1
        return self.map.cell(i,j)
    def reset(self):
        self.x = self.i*Cell.SIZE+(self.map.area.position.x+1)
        self.y = self.j*Cell.SIZE+(self.map.area.position.y+1)
    def convertPositionToPixel(self,x,y):
        return (x*Cell.SIZE+(self.map.area.position.x+1),y*Cell.SIZE+(self.map.area.position.y+1))
    def absoluteX(self):
        return self.x+self.map.area.position.x
    def absoluteY(self):
        return self.y+self.map.area.position.y
    def draw(self ):
        if not self.blocking or not self.drawn:
            #logging.debug("Draw Cell ", self.i, self.j)
            self.map.area.backgroundLayer.blit(self.map.spriteSheet.image_by_id(self.imageId), (self.x, self.y))
            self.drawn = True
    def draw_image(self,image, shift=None):
        if shift == None:
            self.map.area.backgroundLayer.blit(image, (self.x, self.y))
        else:
            self.map.area.backgroundLayer.blit(image, (self.x+shift[0], self.y+shift[1]))
    def get_rect(self):
        return Rect(self.x, self.y, Cell.SIZE,Cell.SIZE) 

class PlayMap :
    EMPTY = '.'
    BLOCK = 'X'
    START = 'O'
    def __init__(self, level):
        self.spriteSheet = None
        self.cells = []
        self.area = None
        w = j = 0
        path = os.path.join('maps', level+"_blocking_map.txt")
        f = open(path, "r")
        for line in f:
            line = line.rstrip('\n')
            w = max(w, len(line))
            self.cells.append([])    
            i = 0
            for c in line:
                self.cells[j].append(Cell(i,j, self,c==PlayMap.BLOCK))
                if c == PlayMap.START:
                    self.startCell = (i,j)
                i += 1
            j += 1
        path = os.path.join('maps', level+"_tiles_map.txt")
        f = open(path, "r")
        j = 0
        for line in f:
            line = line.rstrip('\n')
            ids = line.split(' ') 
            i = 0
            for id in ids:
                #logging.debug("Cell ",i,j,id)
                self.cells[j][i].imageId = id
                i += 1
            j += 1
        self.width = w
        self.height = j
    def cell(self, i,j):
        #logging.debug("cell ",i,j)
        if i<0 or j<0 or i >= self.width or j >= self.height:
            return None         
        return self.cells[j][i]
    def __str__(self):
        return str(self.cells)