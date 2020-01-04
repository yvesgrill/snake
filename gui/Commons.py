import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
import tinycss2
from gui.NamedColors import *
import logging

class Quantity:
    PERCENTAGE='%'
    PIXEL='px'
    POINT='pt'
    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit
    def __eq__(self, other):
        if isinstance(other, Quantity):
            return self.value == other.value and self.unit == other.unit
        return str(self) == str(other)    
    def __str__(self):
        s = str(self.value)
        if self.unit != None:
            s+=self.unit
        return s
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def to_tuple(self):
        return (self.x,self.y)
    def __str__(self):
        s = 'x: '+str(self.x)
        s += '\n'
        s += '\ty: '+str(self.y)
        return s
    def get_x(self):
        return self.x.value if isinstance(self.x, Quantity) else  self.x
    def get_y(self):
        return self.y.value if isinstance(self.y, Quantity) else  self.y
class Dimension:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def to_tuple(self):
        return (self.width,self.height)
    def __str__(self):
        s = 'width: '+str(self.width)
        s += '\n'
        s += '\theight: '+str(self.height)
        return s
    def get_width(self):
        return self.width.value if isinstance(self.width, Quantity) else  self.width
    def get_height(self):
        return self.height.value if isinstance(self.height, Quantity) else  self.height

class FontStyle:
    def __init__(self, size, bold = None, italic = None,family=None):
        self.family = family
        self.size = Quantity(size)
        self.bold = bold
        self.italic = italic
    def copy(self, fontStyle):
        if fontStyle.family != None:
            self.family = fontStyle.family
        if fontStyle.size != None:
            self.size = fontStyle.size
        if fontStyle.bold != None:
            self.bold = fontStyle.bold
        if fontStyle.italic != None:
            self.italic = fontStyle.italic
    def get_size(self):
        return self.size.value if isinstance(self.size, Quantity) else  self.size
    def __str__(self):
        s = 'font-family: '+str(self.family)
        s += '\n'
        s += '\tfont-size: '+str(self.size)
        s += '\n'
        s += '\tfont-bold: '+str(self.bold)
        s += '\n'
        s += '\tfont-italic: '+str(self.italic)
        s += '\n'
        return s
class BackgroundStyle:
    def __init__(self, color = None, image=None):
        self.color = color
        self.image = image
        self.size = None
        self.position = None
    def copy(self, backgroundStyle):
        if backgroundStyle.color != None:
            self.color = backgroundStyle.color
        if backgroundStyle.image != None:
            self.image = backgroundStyle.image
        if backgroundStyle.size != None:
            self.size = backgroundStyle.size
        if backgroundStyle.position != None:
            self.position = backgroundStyle.position
    def __str__(self):
        s = 'background-color: '+str(self.color)
        s += '\n'
        s += '\tbackground-image: '+str(self.image)
        s += '\n'
        s += '\tbackground-size: '+str(self.size)
        s += '\n'
        s += '\tbackground-position: '+str(self.position)
        s += '\n'
        return s
class Style:
    def __init__(self, color=None):
        self.font = FontStyle(32)
        self.background = BackgroundStyle()
        self.color = color
        self.dimension = None
        self.position = None
        self.visible = None
    def __str__(self):
        s = '{'
        s += '\n'
        s += '\t'+str(self.font)
        s += '\n'
        s += '\t'+str(self.background) 
        s += '\n'
        s += '\tcolor: '+str(self.color) 
        s += '\n'
        s += '\t'+str(self.dimension) 
        s += '\n'
        s += '\t'+str(self.position) 
        s += '\n'
        s += '\tvisible:'+str(self.visible) 
        s += '\n'
        s += '}'
        return s
    def copy(self, style):
        if style.color != None:
            self.color = style.color
        if style.dimension != None:
            self.dimension = style.dimension
        if style.position != None:
            self.position = style.position
        if style.visible != None:
            self.visible = style.visible
        self.font.copy(style.font)
        self.background.copy(style.background)

class Theme:
    def __init__(self, name, fontStyle = FontStyle(32), bgColor = WHITE, fgColor = BLACK):
        self.name = name
        self.defaultStyle = Style()
        self.defaultStyle.font = fontStyle
        self.defaultStyle.color = fgColor
        self.defaultStyle.background.color=None
        self.defaultStyle.dimension = None

        self.colors = {}
        self.styles = {}
    def get_style(self,id,className, type, state=None) :
        logging.debug("get_style:%s %s %s",id,className, type)
        type = type.lower()
        if state != None:
            id += ':'+state
            type += ':'+state
            className = className+':'+state if className != None else className
        style = Style() #self.defaultStyle
        if self.styles.__contains__(type.lower()):
            style.copy(self.styles[type.lower()])
        if self.styles.__contains__(className):
            style.copy(self.styles[className])
        if self.styles.__contains__(id):
            style.copy(self.styles[id])
        return style
    def get_font(self, style=None):
        if style == None:
            return pygame.font.SysFont(self.defaultStyle.font.family, self.defaultStyle.font.get_size(), self.defaultStyle.font.bold, self.defaultStyle.font.italic)
        else:
            if style.family == None:
                return pygame.font.SysFont(self.defaultStyle.font.family, style.get_size(), style.bold, style.italic)
            else:
                return pygame.font.SysFont(style.family, style.get_size(), style.bold, style.italic)

    def __str__(self):
        s = "Theme:"+ self.name+'\n'
        for key, value in self.styles.items():            
            s += str(key)
            s += str(value)
            s += '\n'
        return s
    @staticmethod
    def parseCss(name):
        f = open(os.path.join('styles', name+".css"), "r")
        css = f.read()

        rules = tinycss2.parse_stylesheet(css,True,True)
        config = {}
        for rule in rules:
            logging.debug("rule: %s",rule)
            lastLiteral = None
            key = ''
            for c in rule.prelude:
                logging.debug("component: %s",c)
                if isinstance(c,tinycss2.ast.WhitespaceToken):
                    if lastLiteral == None:
                        lastLiteral = ' '
                if isinstance(c,tinycss2.ast.LiteralToken):
                    lastLiteral = c.value
                if isinstance(c,tinycss2.ast.IdentToken):
                    logging.debug("selector: %s",c.value)
                    if lastLiteral != None:
                        key += lastLiteral+c.value
                    else:
                        key += c.value
                if isinstance(c,tinycss2.ast.HashToken):
                    logging.debug("selector: %s",c.value)
                    key += '#'+c.value
            props = {}
            config[key] = props
            key = None
            value  = []
            for c in rule.content:
                logging.debug("component: %s",c)
                if isinstance(c,tinycss2.ast.IdentToken):
                    logging.debug("rule: %s",c.value)
                    if key == None :
                        key = str(c.value)
                    else :
                        value.append(str(c.value))
                if isinstance(c,tinycss2.ast.StringToken):
                    value.append(c.value)
                if isinstance(c,tinycss2.ast.HashToken):
                    value.append('#'+c.value)
                if isinstance(c,tinycss2.ast.PercentageToken):
                    qte = Quantity(c.int_value if c.is_integer else c.value,Quantity.PERCENTAGE)
                    value.append(qte)
                if isinstance(c,tinycss2.ast.DimensionToken):
                    qte = Quantity(c.int_value if c.is_integer else c.value,c.lower_unit)                    
                    value.append(qte)
                if isinstance(c,tinycss2.ast.NumberToken):
                    qte = Quantity(c.int_value if c.is_integer else c.value)                    
                    value.append(qte)
                if isinstance(c,tinycss2.ast.FunctionBlock):
                    args = []
                    for arg in c.arguments:
                        if isinstance(arg,tinycss2.ast.NumberToken):
                            args.append(arg.int_value if arg.is_integer else arg.value)
                        elif isinstance(arg,tinycss2.ast.StringToken):
                            args.append(arg.value)
                    if c.lower_name == 'rgb' :
                        value.append(html_rgb_color(args))
                if isinstance(c,tinycss2.ast.LiteralToken) and c.value==';':
                    props[key] = value
                    key = None
                    value = []

        logging.debug("Config= %s",config)        
        theme = Theme(name)
        for (key,value) in config.items():
            if not theme.styles.__contains__(key):
                theme.styles[key] = Style()
            for (key2,value2) in value.items():
                if key2 == 'display':
                    if value2[0] == 'none':
                        theme.styles[key].visible = False
                    else:
                        theme.styles[key].visible = True
                if key2 == 'background-color':
                    theme.styles[key].background.color = Color(value2[0])
                if key2 == 'background-image':
                    theme.styles[key].background.image = value2[0]
                if key2 == 'background-size':
                    if len(value2) == 1:
                        theme.styles[key].background.size = value2[0]
                    else:
                        theme.styles[key].background.size = value2
                if key2 == 'background-position': 
                    theme.styles[key].background.position = value2
                if key2 == 'color':
                    theme.styles[key].color = Color(value2[0])
                if key2 == 'font-family':
                    theme.styles[key].font.family = value2[0]
                if key2 == 'font-size':
                    theme.styles[key].font.size = value2[0]
                if key2 == 'font-weight':
                    theme.styles[key].font.bold = (value2[0] == 'bold')
                if key2 == 'font-style':
                    theme.styles[key].font.italic = (value2[0] == 'italic')
                if key2 == 'left':
                    if theme.styles[key].position == None:
                        theme.styles[key].position = Position(x=value2[0], y=None)
                    else:
                        theme.styles[key].position.x = value2[0]
                if key2 == 'top':
                    if theme.styles[key].position == None:
                        theme.styles[key].position = Position(x=None, y=value2[0])
                    else:
                        theme.styles[key].position.y = value2[0]
                if key2 == 'width':
                    if theme.styles[key].dimension == None:
                        theme.styles[key].dimension = Dimension(width=value2[0], height=None)
                    else:
                        theme.styles[key].dimension.width = value2[0]
                if key2 == 'height':
                    if theme.styles[key].dimension == None:
                        theme.styles[key].dimension = Dimension(width=None, height=value2[0])
                    else:
                        theme.styles[key].dimension.height = value2[0]
        logging.debug("Theme= %s",theme)        
        return theme
# class ComponentDecorator(Component):
#     def __init__(self, component, posx, posy):
#         super().__init__(component.name, posx, posy, component.container)
#         self.component = component
#     def draw(self):
#         self.component.draw()
#     def on_handle_event(self, event):
#         self.component.on_handle_event(event)

# class BorderDecorateur(ComponentDecorator):
#     def __init__(self, component, borderSize):
#         super().__init__(component, component.x-borderSize, component.y-borderSize)
#     def draw(self):
#         self.component.draw()
#         box = pygame.Surface(self.get_dimension())
#         pygame.draw.rect(box, Color.BLACK,(0,0,self.dimension.width,self.dimension.height))
#         self.get_application().display.blit(box, (self.absoluteX(), self.absoluteY()))


def html_rgb_color(args):
    s = '#'
    logging.debug("args=%s",args)
    for arg in args:
        s += str(hex(arg)[2:].rjust(2, '0'))
    return s