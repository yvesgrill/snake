import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 840
GAMEWIDTH = 17
GAMEHEIGHT = 17
GAMEAREA_ORIGINX = 130
GAMEAREA_ORIGINY = 180
BOXSIZE = 32
MOVEFREQ = 0.5
WHITE = (255, 255, 255)
GREY = (127, 127, 127)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
ALLDIRECTION = ["up", "down", "right", "left"]
DIRECTION = ALLDIRECTION[2]
POSITION_INITX = 561
POSITION_INITY = 281
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)


class Game:
    fenetre = None
    keys = []
    font= None
    fpsClock = None
    screen = None
    def __init__(self, speed):
        return
    
    def run(self):
        pygame.init()
        pygame.mixer.init()
        Game.font = pygame.font.Font(None, 32)
        Game.fpsClock = pygame.time.Clock()
        Game.fenetre = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Snake')

        Game.screen = HomeScreen(WINDOWWIDTH, WINDOWHEIGHT)
        flag = True

        while Game.screen != None:
            Game.screen.run()
        pygame.quit()

class Component:
    def __init__(self, parent):
        self.parent = parent
    def draw(self):
        print("Vous devez définir la méthode draw")

        
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def xInPixel(self):
        return self.x*BOXSIZE+(GAMEAREA_ORIGINX+1)
    def yInPixel(self):
        return self.y*BOXSIZE+(GAMEAREA_ORIGINY+1)
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
class Snake(Component, pygame.sprite.Sprite):
    def __init__(self, screen, posx, posy):
        super().__init__(screen)
        self.started = False
        self.direction = "up"
        self.body = [Position(posx,posy),Position(posx,posy + 1),Position(posx,posy + 2)]
        self.growing =False
        pygame.sprite.Sprite.__init__(self)
        self.spriteSheet = pygame.image.load("images/snake-graphics.png").convert_alpha()
    def update(self):
       self.move()
    def move(self):
        if( not self.started):
            return
        global BOXSIZE
        head = ''
        if self.direction == "up" and  self.head().y > 0:
                head = Position(self.head().x,self.head().y - 1)
        if self.direction == "down" and self.head().y < GAMEHEIGHT-1:
                head = Position(self.head().x,self.head().y + 1)
        if self.direction == "right" and self.head().x < GAMEWIDTH-1:
                head = Position(self.head().x + 1,self.head().y)
        if self.direction == "left" and self.head().x > 0:
                head = Position(self.head().x - 1,self.head().y)
        
        if head != '':
            if head in self.body:
                PlayScreen.perdu = True
            self.body.insert(0,head)
            if self.growing == False:
               self.body.pop()
            else :
               self.growing = False
        else:
            PlayScreen.perdu = True
    def changeDirection(self, direction):

        if self.direction == "up" and direction == "down":
            return
        if self.direction == "down" and direction == "up":
            return
        if self.direction == "right" and direction == "left":
            return
        if self.direction == "left" and direction == "right":
            return
        self.started = True
        #print("Change direction to ",direction)
        self.direction = direction
        self.move()
    def draw(self):
        global BOXSIZE, WHITE, BLACK, GREY
        for i,seg in enumerate(reversed(self.body)):
            if i == 0:
                if self.body[-2] == seg.atRight():
                    Game.fenetre.blit(self.sprite(128, 64),(seg.xInPixel()+(BOXSIZE/2), seg.yInPixel()))
                    #pygame.draw.rect(Game.fenetre, GREY, (seg.xInPixel()+(BOXSIZE/2), seg.yInPixel(), (BOXSIZE/2), BOXSIZE))
                if self.body[-2] == seg.atLeft():
                    Game.fenetre.blit(self.sprite(96, 96),(seg.xInPixel(), seg.yInPixel()))
                    #pygame.draw.rect(Game.fenetre, GREY, (seg.xInPixel(), seg.yInPixel(), (BOXSIZE/2), BOXSIZE))
                if self.body[-2] == seg.atUp():
                    Game.fenetre.blit(self.sprite(96, 64),(seg.xInPixel(), seg.yInPixel()))
                    #pygame.draw.rect(Game.fenetre, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, (BOXSIZE/2)))
                if self.body[-2] == seg.atDown():
                    Game.fenetre.blit(self.sprite(128, 96),(seg.xInPixel(), seg.yInPixel()+(BOXSIZE/2)))
                    #pygame.draw.rect(Game.fenetre, GREY, (seg.xInPixel(), seg.yInPixel()+(BOXSIZE/2), BOXSIZE, (BOXSIZE/2)))
                #pygame.draw.circle(Game.fenetre, GREY, (seg.xInPixel()+int(BOXSIZE/2), seg.yInPixel()+int(BOXSIZE/2)), int(BOXSIZE/2))
            elif i == len(self.body)-1:
                #pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel()+int(BOXSIZE/2), seg.yInPixel()+int(BOXSIZE/2)), int(BOXSIZE/2))
                if self.direction == "up":
                    Game.fenetre.blit(self.sprite(96, 0),(seg.xInPixel(), seg.yInPixel()+(BOXSIZE/2)))
                    #pygame.draw.rect(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel()+(BOXSIZE/2), BOXSIZE-1, (BOXSIZE/2)-1))
                    #pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel()+BOXSIZE), int(BOXSIZE/4))
                    #pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel()+BOXSIZE, seg.yInPixel()+BOXSIZE), int(BOXSIZE/4))
                    #pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel(), seg.yInPixel()+BOXSIZE), int(BOXSIZE/4)-4)
                    #pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel()+BOXSIZE, seg.yInPixel()+BOXSIZE), int(BOXSIZE/4)-4)
                if self.direction == "down":
                    Game.fenetre.blit(self.sprite(128, 32),(seg.xInPixel(), seg.yInPixel()))
##                    pygame.draw.rect(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel(), BOXSIZE-1, (BOXSIZE/2)-1))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel()), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel()+BOXSIZE, seg.yInPixel()), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel(), seg.yInPixel()), int(BOXSIZE/4)-4)
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel()+BOXSIZE, seg.yInPixel()), int(BOXSIZE/4)-4)
                if self.direction == "right":
                    Game.fenetre.blit(self.sprite(128, 0),(seg.xInPixel(), seg.yInPixel()))
##                    pygame.draw.rect(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel(), (BOXSIZE/2)-1, BOXSIZE-1))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel()), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel(), seg.yInPixel()+BOXSIZE), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel(), seg.yInPixel()), int(BOXSIZE/4)-4)
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel(), seg.yInPixel()+BOXSIZE), int(BOXSIZE/4)-4)
                if self.direction == "left":
                    Game.fenetre.blit(self.sprite(96, 32),(seg.xInPixel()+(BOXSIZE/2), seg.yInPixel()))
##                    pygame.draw.rect(Game.fenetre, BLACK, (seg.xInPixel()+(BOXSIZE/2), seg.yInPixel(), (BOXSIZE/2)-1, BOXSIZE-1))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel()+BOXSIZE, seg.yInPixel()), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, BLACK, (seg.xInPixel()+BOXSIZE, seg.yInPixel()+BOXSIZE), int(BOXSIZE/4))
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel()+BOXSIZE, seg.yInPixel()), int(BOXSIZE/4)-4)
##                    pygame.draw.circle(Game.fenetre, WHITE, (seg.xInPixel()+BOXSIZE, seg.yInPixel()+BOXSIZE), int(BOXSIZE/4)-4)
            else:
                pygame.draw.rect(Game.fenetre, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))

    def grow(self):
        self.growing = True
    #def print(self) :
        #print("Head(",self.head.x,",",self.head.y,")")
        #for seg in self.body:
            #print("Body(",seg.x,",",seg.y,")")
        #print("Tail(", self.tail.x,",",self.tail.y,")")
    def head(self) :
        return self.body[0]
    def tail(self) :
        return self.body[-1]

    def sprite(self, x, y):
        return self.spriteSheet.subsurface(pygame.Rect(x,y,32,32))
        
class Apple(Component):
    imageApple = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (BOXSIZE-1, BOXSIZE-1))

    def __init__(self, screen):
        super().__init__(screen)
        self.position = Position(random.randint(0,GAMEWIDTH-1), random.randint(0,GAMEHEIGHT-1))
        self.crunched = False
    def draw(self):
        if not self.crunched:
            Game.fenetre.blit(Apple.imageApple, (self.position.xInPixel(), self.position.yInPixel()))

class Button(Component):
    def __init__(self, screen, posx, posy, width, height, text, size, action):
        super().__init__(screen)
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.Font(None, size)
        self.action = action

    def draw(self):
        global RED,WHITE
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
        Game.fenetre.blit(box, (self.posx, self.posy))

    def onEvents(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.posx+self.width > event.pos[0] > self.posx and self.posy+self.height > event.pos[1]> self.posy:
                self.click()

    def click(self):
        self.action()
        

class Screen:
    def __init__(self, width, height):
        self.components = []
        self.image = None
    def addComponent(self, component):
       self.components.append(component)
    def draw(self):
        Game.fenetre.blit(self.image, (0,0))
        for component in self.components:
            component.draw()
    def run(self):
        self.flag = True
        while self.flag :
            events = pygame.event.get()
            keysPressed = pygame.key.get_pressed()
            for event in events:
                for component in self.components:
                    component.onEvents(event)
                if event.type == pygame.QUIT:
                    self.flag = False
                    Game.screen = None
            self.draw()
            pygame.display.update()
            Game.fpsClock.tick(FPS)        
class HomeScreen(Screen):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.image = pygame.image.load(os.path.join('images', 'Menu.png')).convert()
        self.classic = Button(self, 300,300, 220, 60, "Classique", 50, self.play)
        super().addComponent(self.classic)
        self.options = Button(self, 300,370, 220, 60, "Options", 50, self.options)
        super().addComponent(self.options)
    def play(self):
        print("coucou")
        Game.screen = PlayScreen(WINDOWWIDTH, WINDOWHEIGHT)
        self.flag = False
    def options(self):
        Game.screen = OptionsScreen(WINDOWWIDTH, WINDOWHEIGHT)
        self.flag = False
class PlayScreen(Screen):
    compteur = 0
    perdu = False

    def __init__(self, width, height):
        super().__init__(width, height)
        self.gameOver = pygame.image.load(os.path.join('images', 'game_over.jpg')).convert()
        self.image = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        self.image.fill(WHITE)
        self.speed = 7
        self.apples = []

        pygame.draw.rect(self.image, LIGHT_GREEN, (GAMEAREA_ORIGINX, GAMEAREA_ORIGINY, BOXSIZE*(GAMEWIDTH), BOXSIZE*(GAMEHEIGHT)))
        for i in range(0, GAMEWIDTH):
            if(i%2 == 0):
                for j in range(0, int((GAMEHEIGHT+1)/2)):
                    pygame.draw.rect(self.image, DARK_GREEN, (GAMEAREA_ORIGINX+BOXSIZE*i, GAMEAREA_ORIGINY+BOXSIZE*(2*j), BOXSIZE, BOXSIZE))
            if(i%2 == 1):
                for j in range(0, int((GAMEHEIGHT-1)/2)):
                    pygame.draw.rect(self.image, DARK_GREEN, (GAMEAREA_ORIGINX+BOXSIZE*i, GAMEAREA_ORIGINY+BOXSIZE*(2*j)+BOXSIZE, BOXSIZE, BOXSIZE))
        self.serpent = Snake(self,7,7)  
        super().addComponent(self.serpent)
        self.appleScore = Apple(self)
        self.appleScore.position.x = 0
        self.appleScore.position.y = -2
        super().addComponent(self.appleScore)
        apple = Apple(self)
        while apple.position in self.serpent.body:
            apple = Apple(self)
        self.apples.append(apple)
        super().addComponent(apple)
        self.file = open("hightscore.txt","r")
        self.readFile = self.file.read()
        if len(self.readFile) == 0:
            self.hightscore = Game.font.render("Highscore : 0",0,(0,0,0),(255,255,255))    
        else:
            self.hightscore = Game.font.render("Highscore : "+self.readFile,0,(0,0,0),(255,255,255))
        self.file.close()

    def run(self):
        flag = True
        while flag:
            PlayScreen.compteur = PlayScreen.compteur + 1
            events = pygame.event.get()
            keysPressed = pygame.key.get_pressed()
            for event in events:
                if not PlayScreen.perdu and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        Game.keys.insert(0,event.key)
                if event.type == pygame.QUIT:
                    flag = False
                    Game.screen = None
            if not PlayScreen.perdu and PlayScreen.compteur >= int(FPS/self.speed):
                print("Keys pressed:",Game.keys)
                if len(Game.keys) == 0:
                    self.serpent.update()
                    self.refresh(self.serpent)
                else :
                    keyPressed= Game.keys.pop()
                    if keyPressed == K_RIGHT:
                        self.serpent.changeDirection(ALLDIRECTION[2])
                    if keyPressed == K_LEFT:
                        self.serpent.changeDirection(ALLDIRECTION[3])
                    if keyPressed == K_DOWN:
                        self.serpent.changeDirection(ALLDIRECTION[1])
                    if keyPressed == K_UP:
                        self.serpent.changeDirection(ALLDIRECTION[0])
                    self.refresh(self.serpent)
                PlayScreen.compteur = 0

            self.draw()
            text = Game.font.render("Score : "+str(len(self.apples)-1),0,(0,0,0),(255,255,255))
            Game.fenetre.blit(text, (180, 125))
            Game.fenetre.blit(self.hightscore, (500, 125))
            self.appleScore.draw()
            self.apples[-1].draw()
            self.serpent.draw()
            if PlayScreen.perdu:
                self.file = open("hightscore.txt","w")
                self.file.write(str(len(self.apples)-1))
                self.file.close()
                Game.fenetre.blit(self.gameOver, (240, 360))
                Game.screen = HomeScreen(WINDOWWIDTH, WINDOWHEIGHT)
                PlayScreen.perdu = False
                flag = False
            pygame.display.update()
            print("Coucou",PlayScreen.compteur)
            Game.fpsClock.tick(FPS)
    def refresh(self,serpent):
        apple = self.apples[-1]
        if self.serpent.head() == apple.position:
            apple.crunched = True
            #pygame.mixer.music.load(open("son\Crunched.wav","rb"))
            #pygame.mixer.music.play()
            print("Apple crunched!")
            self.serpent.grow()
            apple = Apple(self)
            while apple.position in serpent.body:
                apple = Apple(self)
            self.apples.append(apple)

class OptionsScreen(Screen):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.image = pygame.image.load(os.path.join('images', 'Options.png')).convert()
        self.retour = Button(self, 300,500, 150, 60, "Retour", 50, self.home)
        super().addComponent(self.retour)
        self.font = pygame.font.Font(None, 40)
        self.musicOn = Button(self, 300,370, 80, 60, "ON", 40, self.on)
        super().addComponent(self.musicOn)
        self.musicOff = Button(self, 400,370, 80, 60, "OFF", 40, self.off)
        super().addComponent(self.musicOff)
        self.music = True
    def home(self):
        Game.screen = HomeScreen(WINDOWWIDTH, WINDOWHEIGHT)
        self.flag = False
    def on(self):
        text = self.font.render("Music",0,(0,0,0),None)
        Game.fenetre.blit(text, (300, 300))
        self.music = True
        print("Music ON")
    def off(self):
        print("Music OFF")
        self.music = False
        
game = Game(0.2)
game.run()

sys.exit()
