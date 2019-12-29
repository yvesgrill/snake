import pygame, sys, os





class SpriteSheet:
    def __init__(self, filename, cellSize, n, m):
        self.sheetImage = pygame.image.load(filename).convert_alpha()
        self.cellSize = cellSize
        self.images = []
        self.imagesById = {}
        index=0
        for j in range(0,m):   
            self.images.append([])         
            for i in range(0,n):            
                x = i*32
                y = j*32
                self.images[j].append(self.sheetImage.subsurface(pygame.Rect(x,y,cellSize,cellSize)))
                self.imagesById[hex(index)[2:].rjust(2, '0')] = self.sheetImage.subsurface(pygame.Rect(x,y,cellSize,cellSize))
                index += 1
        print("cells:", self.imagesById)
    def image(self,n,m) :
        return self.images[m][n]
    def image_by_id(self,id) :
        #print("Id=",id)
        return self.imagesById[id]