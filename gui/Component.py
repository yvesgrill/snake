import random, time, pygame, sys, os
from gui.NamedColors import *
from pygame.locals import *
from gui.Commons import *
from gui.Application import *
import logging

class Layer:
    def __init__(self, id, source, dest=(0,0), area=None, flags=0):
        self.id = id
        self.dest = dest
        self.source = source
        self.area = area
        self.flags = flags
    def to_tuple(self):
        #return (self.source,self.dest,self.area, self.flags)
        return (self.source,self.dest)
    def __str__(self):
        return 'Layer('+self.id+'):'+str(self.dest)
class Component:
    def __init__(self, id, position=None, dimension=None, className=None):
        self.container = None
        self.id = id
        self.className = className
        themeStyle = Application.theme.get_style(self.get_id(),self.get_class(),self.__class__.__name__)
        if themeStyle == None:
            themeStyle = Application.theme.defaultStyle
        if position != None:
            self.position = Position(*position)
        else:
            self.position = themeStyle.position
        if self.position == None:
            self.position = Position(0,0)
        if dimension != None:
            self.dimension = Dimension(*dimension)    
        else:
            self.dimension = themeStyle.dimension
        self.style = Style()
        self.style.copy(themeStyle)         
        self.realized = False
        self.__font = None
        self.enabled = True
        self.visible = True
        if themeStyle.visible != None: 
            self.visible = themeStyle.visible
        self.state = None
        self.__dirty = True
        self.styles = {}
        self.layers = []
        themeStyle = Application.theme.get_style(self.get_id(),self.get_class(),self.__class__.__name__,'hover')
        if themeStyle != None:
            style = Style()
            style.copy(themeStyle)         
            self.styles['hover']=style
    def realize(self):
        logging.debug("Realize component %s",self.id)
        if not self.realized:
            logging.debug("Dimension= %d %d", self.dimension.get_width(),self.dimension.get_height())
            self.backgroundLayer = pygame.Surface(self.get_dimension())
            self.foregroundLayer = pygame.Surface(self.get_dimension())
            self.foregroundLayer.set_colorkey(BLACK)
            self.updateBackground()
            logging.debug("Surface= %d %d", self.backgroundLayer.get_width(), self.backgroundLayer.get_height())
            self.realized = True
    def get_background_color(self):
        color = self.style.background.color 
        if self.state != None:
            color = self.styles[self.state].background.color
        if color == None or color == 'transparent' :
            return None
        elif color == 'inherit':
            if self.container != None:
                return self.container.get_background_color()
        else:
            return color
    def get_foreground_color(self):
        color = self.style.color 
        if self.state != None:
            color = self.styles[self.state].color
        if color == None or color == 'transparent' :
            return Application.theme.defaultStyle.color
        elif color == 'inherit':
            if self.container != None:
                return self.container.get_foreground_color()
            else:
                return Application.theme.defaultStyle.color                
        else:
            return color
    def calculate_dimension(self):
        if self.dimension != None:
            return self.dimension
        dim = []
        styleDimension = self.style.dimension
        if styleDimension == None:
            dim = None
        elif len(styleDimension) == 1:
            if styleDimension == 'auto':
                w,h = 0,0
                for layer in self.layers:
                    w = max(w,layer.source.get_width())
                    h = max(h,layer.source.get_heigth())
                dim.append(w)
                dim.append(h)
        elif len(styleDimension) == 2:
            if styleDimension[0] == 'auto':
                w = 0
                for layer in self.layers:
                    w = max(w,layer.source.get_width())
                dim.append(w)
            elif isinstance(styleDimension[0],Quantity):
                if styleDimension[0].unit == Quantity.PERCENTAGE:
                    if self.container != None:
                        dim.append(int(self.container.dimension.width*styleDimension[0].value/100))
                    else:
                        dim.append(0)
                else:
                    dim.append(int(styleDimension[0].value))
            else:
                dim.append(int(styleDimension[0].value))
            if styleDimension[1] == 'auto':
                h = 0
                for layer in self.layers:
                    h = max(h,layer.source.get_heigth())
                dim.append(h)
            elif isinstance(styleDimension[1],Quantity):
                if styleDimension[1].unit == Quantity.PERCENTAGE:
                    if self.container != None:
                        dim.append(int(self.container.dimension.height*styleDimension[1].value/100))
                    else:
                        dim.append(0)
                else:
                    dim.append(int(styleDimension[1].value))
            else:
                dim.append(int(styleDimension[1].value))

    def add_overlay(self):
        overlay = pygame.Surface(self.get_dimension())
        #self.backgroundLayer.fill(BLACK)
        overlay.set_alpha(128)
        self.update_layer('overlay',overlay,(self.absoluteX(),self.absoluteY()), (self.absoluteX(),self.absoluteY(), overlay.get_width(), overlay.get_height()))
    def remove_overlay(self):
        self.remove_layer('overlay')

    def updateBackground(self):
        self.__dirty = True

        color = self.get_background_color()
        if color != None:
            self.backgroundLayer = pygame.Surface(self.get_dimension())
            self.backgroundLayer.fill(color)
            self.update_layer('background',self.backgroundLayer,(self.absoluteX(),self.absoluteY()), (self.absoluteX(),self.absoluteY(), self.backgroundLayer.get_width(), self.backgroundLayer.get_height()))
        if self.style.background.image != None :
            #if self.backgroundLayer == None:
            image = pygame.image.load(os.path.join('images', self.style.background.image)).convert()
            x, y = 0, 0
            dim = None
            size = self.style.background.size
            if size == None:
                dim = None
            elif len(size) == 1:
                if size == 'cover':
                    dim = self.get_dimension()
                if size == 'auto':
                    dim = None
            elif len(size) == 2:
                dim = []
                if size[0] == 'auto':
                    dim.append(image.get_width())
                elif isinstance(size[0],Quantity):
                    if size[0].unit == Quantity.PERCENTAGE:
                        dim.append(int(self.dimension.width*size[0].value/100))
                    else:
                        dim.append(int(size[0].value))
                else:
                    dim.append(int(size[0].value))
                if size[1] == 'auto':
                    dim.append(image.get_height())
                elif isinstance(size[1],Quantity):
                    if size[1].unit == Quantity.PERCENTAGE:
                        dim.append(int(self.dimension.height*size[1].value/100))
                    else:
                        dim.append(int(size[1].value))
                else:
                    dim.append(int(size[1].value))
            if dim != None:
                image = pygame.transform.scale(image, dim)

            if self.style.background.position != None:
                if self.style.background.position[0] == 'left':
                    x = 0
                elif self.style.background.position[0] == 'right':
                    x = self.dimension.width-image.get_width()
                elif self.style.background.position[0] != None:
                    x = int(self.style.background.position[0])
                if self.style.background.position[1] == 'top':
                    y = 0
                elif self.style.background.position[1] == 'bottom':
                    y = self.dimension.height-image.get_height()
                elif self.style.background.position[1] != None:
                    y = int(self.style.background.position[1])

            self.backgroundLayer.blit(image, (x, y))            
            self.update_layer('background',self.backgroundLayer,(self.absoluteX(),self.absoluteY()), (self.absoluteX(),self.absoluteY(), self.backgroundLayer.get_width(), self.backgroundLayer.get_height()))
    def updateText(self, text, color):
        self.__dirty = True
        if color == BLACK:
            self.foregroundLayer.set_colorkey(WHITE)
            self.foregroundLayer.fill(WHITE)
        surf = self.get_font().render(text,True,color,None)
        x = int((self.dimension.get_width()-surf.get_width())/2)
        y = int((self.dimension.get_height()-surf.get_height())/2)
        #self.foregroundLayer.blit(surf, (x, y))
        self.update_layer('foreground',surf,(self.absoluteX()+x,self.absoluteY()+y),(self.absoluteX(),self.absoluteY(), surf.get_width(), surf.get_height()))

    def update(self):
        logging.debug("Update component %s",self.id)
        #self.updateBackground()

    def draw(self):
        logging.debug("Draw component %s of size (%d,%d) at position (%d,%d)",self.id, self.get_width(), self.get_height(), *self.get_position())
        
        #logging.debug("Draw component ",self.id, self.style.background.color.to_tuple(), self.style.background.image)
        if self.container == None:
            self.get_application().display.blit(self.backgroundLayer, (self.absoluteX(), self.absoluteY()))
            #self.get_application().display.blit(self.foregroundLayer, (self.absoluteX(), self.absoluteY()))
        else:
            self.container.backgroundLayer.blit(self.backgroundLayer, self.get_position())
            self.get_application().display.blit(self.foregroundLayer, (self.absoluteX(), self.absoluteY()))
    def handle_event(self, event):
        if self.enabled :
            self.on_handle_event(event)
    def on_handle_event(self, event):
        pass
    def absoluteX(self):
        if self.container == None:
            return self.position.get_x()
        else:
            return self.position.get_x()+self.container.position.get_x()
    def absoluteY(self):
        if self.container == None:
            return self.position.get_y()
        else:
            return self.position.get_y()+self.container.position.get_y()
    def get_position(self):
        return (self.position.get_x(),self.position.get_y())
    def get_dimension(self):
        return (self.dimension.get_width(),self.dimension.get_height())
    def get_width(self):
        return self.dimension.get_width()
    def get_height(self):
        return self.dimension.get_height()
    def get_bounds(self):
        return (self.position.get_x(),self.position.get_y(),self.dimension.get_width(),self.dimension.get_height())
    def get_font(self):
        if self.style.font == None:
            return self.container.get_font()
        if self.__font == None:
            self.__font = Application.theme.get_font(self.style.font)
        return self.__font
    def get_application(self):
        if self.container != None:
            return self.container.get_application()
        return None
    def get_id(self):
        return '#'+self.id
    def get_class(self):
        if self.className != None:
            return '.'+self.className
        return None
    def is_visible(self):
        if self.visible:
            if self.container != None:
                return self.container.is_visible()
            else:
                return True
        else:
            return False
    def remove_layer(self,id):
        for layer in self.layers:
            if layer.id == id:
                self.layers.remove(layer)
                return
        return
    def update_layer(self,id, source, dest, area):
        layer = None
        for l in self.layers:
            if l.id == id:
                layer = l
        if layer == None:
            layer = Layer(id,source, dest, area)
            self.layers.append(layer)
        else:
            layer.source = source
            layer.dest = dest
    def collect_layers(self,layers,ids):
        if self.is_visible() and self.__dirty :
            self.__dirty = False
            logging.debug('Collect %d layers of component %s', len(self.layers),self.id)
            for layer in self.layers:
                if layer.id in ids :
                    if layer.source != None:
                        layers.append(layer)
                    else:
                        logging.warning('Layer %s of component %s is empty', layer.id, self.id)
    def set_dirty(self, dirty):
        self.__dirty = dirty