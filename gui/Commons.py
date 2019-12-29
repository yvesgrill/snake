import random, time, pygame, sys, os
from gui.Colors import *
from pygame.locals import *
import pygame.mixer
import tinycss2

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def to_tuple(self):
        return (self.x,self.y)
class Dimension:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def to_tuple(self):
        return (self.width,self.height)
class FontStyle:
    def __init__(self, size, bold = False, italic = False,family=None):
        self.family = family
        self.size = size
        self.bold = bold
        self.italic = italic
    def copy(self, fontStyle):
        self.family = fontStyle.family
        self.size = fontStyle.size
        self.bold = fontStyle.bold
        self.italic = fontStyle.italic
class BackgroundStyle:
    def __init__(self, color = WHITE, image=None):
        self.color = color
        self.image = image
    def copy(self, backgroundStyle):
        self.color = backgroundStyle.color
        self.image = backgroundStyle.image
class Style:
    def __init__(self, color=BLACK):
        self.font = FontStyle(32)
        self.background = BackgroundStyle()
        self.color = color
        self.dimension = None

class Theme:
    def __init__(self, name, fontStyle = FontStyle(32), bgColor = WHITE, fgColor = BLACK):
        self.name = name
        self.defaultStyle = Style()
        self.defaultStyle.font = fontStyle
        self.defaultStyle.color = fgColor
        self.defaultStyle.background.color=bgColor
        self.colors = {}
        self.styles = {}
    def get_style(self,id,className, type) :
        print("get_style:"+id,className, type)
        style = self.defaultStyle
        if self.styles.__contains__(type.lower()):
            style = self.styles[type.lower()]
        if self.styles.__contains__(className):
            style = self.styles[className]
        if self.styles.__contains__(id):
            style = self.styles[id]
        return style
    def get_font(self, style=None):
        if style == None:
            return pygame.font.SysFont(self.defaultStyle.font.family, self.defaultStyle.font.size, self.defaultStyle.font.bold, self.defaultStyle.font.italic)
        else:
            if style.family == None:
                return pygame.font.SysFont(self.defaultStyle.font.family, style.size, style.bold, style.italic)
            else:
                return pygame.font.SysFont(style.family, style.size, style.bold, style.italic)

    def __str__(self):
        return "Theme:"+ self.name+','+str(self.styles)
    @staticmethod
    def parseCss(filename):
        f = open(os.path.join('styles', filename+".css"), "r")
        css = f.read()

        rules = tinycss2.parse_stylesheet(css,True,True)
        config = {}
        for rule in rules:
            print("rule:",rule)
            lastLiteral = None
            for c in rule.prelude:
                print("component:",c)
                if isinstance(c,tinycss2.ast.LiteralToken):
                    lastLiteral = c.value
                if isinstance(c,tinycss2.ast.IdentToken):
                    print("selector:",c.value)
                    if lastLiteral != None:
                        key = lastLiteral+c.value
                    else:
                        key = c.value
                if isinstance(c,tinycss2.ast.HashToken):
                    print("selector:",c.value)
                    key = '#'+c.value
            props = {}
            config[key] = props
            key = None
            for c in rule.content:
                print("component:",c)
                if isinstance(c,tinycss2.ast.IdentToken):
                    print("rule:",c.value)
                    if key == None :
                        key = str(c.value)
                    else :
                        value = str(c.value)
                if isinstance(c,tinycss2.ast.StringToken):
                    value = c.value
                if isinstance(c,tinycss2.ast.DimensionToken):
                    value = c.int_value if c.is_integer else c.value
                if isinstance(c,tinycss2.ast.NumberToken):
                    value = c.int_value if c.is_integer else c.value
                if isinstance(c,tinycss2.ast.FunctionBlock):
                    value = c.lower_name +' ' 
                    for arg in c.arguments:
                        if isinstance(arg,tinycss2.ast.NumberToken):
                            value += str(arg.int_value) if arg.is_integer else str(arg.value)
                        else:
                            value += arg.value
                        value += ' '
                if isinstance(c,tinycss2.ast.LiteralToken) and c.value==';':
                    props[key] = value
                    key = None

        print("Config=",config)        
        theme = Theme("hhh")
        for (key,value) in config.items():
            if not theme.styles.__contains__(key):
                theme.styles[key] = Style()
            for (key2,value2) in value.items():
                if key2 == 'background-color':
                    theme.styles[key].background.color = NamedColors.to_color(value2)
                if key2 == 'background-image':
                    theme.styles[key].background.image = value2
                if key2 == 'color':
                    theme.styles[key].color = NamedColors.to_color(value2)
                if key2 == 'font-family':
                    theme.styles[key].font.family = value2
                if key2 == 'font-size':
                    theme.styles[key].font.size = value2
                if key2 == 'font-weight':
                    theme.styles[key].font.bold = (value2 == 'bold')
                if key2 == 'font-style':
                    theme.styles[key].font.italic = (value2 == 'italic')
                if key2 == 'width':
                    if theme.styles[key].dimension == None:
                        theme.styles[key].dimension = Dimension(width=value2, height=None)
                    else:
                        theme.styles[key].dimension.width = value2
                if key2 == 'height':
                    if theme.styles[key].dimension == None:
                        theme.styles[key].dimension = Dimension(width=None, height=value2)
                    else:
                        theme.styles[key].dimension.height = value2
        print("Theme=",theme)        
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
#         pygame.draw.rect(box, NamedColors.BLACK,(0,0,self.dimension.width,self.dimension.height))
#         self.get_application().display.blit(box, (self.absoluteX(), self.absoluteY()))
