import pygame, sys, os

import logging

class SpriteSheet:
    def __init__(self, filename, cellWidth, cellHeight, n, m):
        self.sheetImage = pygame.image.load(os.path.join('images', filename)).convert_alpha()
        self.cellWidth = cellWidth
        self.cellHeight = cellHeight
        self.width = n
        self.height = m
        self.images = []
        self.imagesById = {}
        index=0
        for j in range(0,m):   
            self.images.append([])         
            for i in range(0,n):            
                x = i*self.cellWidth
                y = j*self.cellHeight
                self.images[j].append(self.sheetImage.subsurface(pygame.Rect(x,y,cellWidth,cellHeight)))
                self.imagesById[hex(index)[2:].rjust(2, '0')] = self.sheetImage.subsurface(pygame.Rect(x,y,cellWidth,cellHeight))
                index += 1
        logging.debug("cells: %s", self.imagesById)
    def image(self,n,m) :
        if n >=0 and m>=0 and n < self.width and m < self.height:
            return self.images[m][n]
        return None
    def image_by_id(self,id) :
        #logging.debug("Id=",id)
        return self.imagesById[id]