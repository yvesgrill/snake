import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
from Env import *
from Games import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)



class Snake(Component, pygame.sprite.Sprite):
    def __init__(self, screen, posx, posy):
        super().__init__(screen)
        self.compteur = 0
        self.started = False
        self.direction = "up"
        self.body = [Position(posx,posy),Position(posx,posy + 1),Position(posx,posy + 2)]
        self.growing =False
        self.state = 'Alive'
        self.speed = 6
        self.frames = int(FPS/self.speed)
        self.pixelsToMove = BOXSIZE/self.frames      
        self.target = None  
        print("Pixels to move:",self.pixelsToMove )
        pygame.sprite.Sprite.__init__(self)
        self.spriteSheet = pygame.image.load("images/snake-graphics.png").convert_alpha()
    def update(self):
        self.move()
    def move(self):
        if( not self.started):
            return
        if self.direction == "up" and  self.head().y > 0:
                self.target = Position(self.head().x,self.head().y - 1)
        if self.direction == "down" and self.head().y < GAMEHEIGHT-1:
                self.target = Position(self.head().x,self.head().y + 1)
        if self.direction == "right" and self.head().x < GAMEWIDTH-1:
                self.target = Position(self.head().x + 1,self.head().y)
        if self.direction == "left" and self.head().x > 0:
                self.target = Position(self.head().x - 1,self.head().y)
        
        if self.target != None:
            if self.target in self.body:
                self.state = 'Dead'
            self.body.insert(0,self.target)
            if self.growing == False:
               self.body.pop()
            else :
               self.growing = False
        else:
            self.state = 'Dead'
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
        #self.move()
    def draw(self):
        for i,seg in enumerate(reversed(self.body)):
            if i == 0:
                if self.body[-2] == seg.atRight():
                    if( self.started):
                        seg.incrementXInPixel(self.pixelsToMove)
                    Game.window.blit(self.sprite(128, 64),(seg.xInPixel(), seg.yInPixel()))
                if self.body[-2] == seg.atLeft():
                    if( self.started):
                        seg.incrementXInPixel(-self.pixelsToMove)
                    Game.window.blit(self.sprite(96, 96),(seg.xInPixel(), seg.yInPixel()))
                if self.body[-2] == seg.atUp():
                    if( self.started):
                        seg.incrementYInPixel(-self.pixelsToMove)
                    Game.window.blit(self.sprite(96, 64),(seg.xInPixel(), seg.yInPixel()))
                if self.body[-2] == seg.atDown():
                    if( self.started):
                        seg.incrementYInPixel(self.pixelsToMove)
                    Game.window.blit(self.sprite(128, 96),(seg.xInPixel(), seg.yInPixel()))
            elif i == len(self.body)-1:
                if self.direction == "up":
                    if( self.started):
                        seg.incrementYInPixel(-self.pixelsToMove)
                    print("Position:",seg.yInPixel())
                    Game.window.blit(self.sprite(96, 0),(seg.xInPixel(), seg.yInPixel()))
                if self.direction == "down":
                    if( self.started):
                        seg.incrementYInPixel(self.pixelsToMove)
                    Game.window.blit(self.sprite(128, 32),(seg.xInPixel(), seg.yInPixel()))
                if self.direction == "right":
                    if( self.started):
                        seg.incrementXInPixel(self.pixelsToMove)
                    Game.window.blit(self.sprite(128, 0),(seg.xInPixel(), seg.yInPixel()))
                if self.direction == "left":
                    if( self.started):
                        seg.incrementXInPixel(-self.pixelsToMove)
                    Game.window.blit(self.sprite(96, 32),(seg.xInPixel(), seg.yInPixel()))
            else:
                pos = self.body.index(seg)
                if self.body[pos-1] == seg.atRight():
                    if( self.started):
                        seg.incrementXInPixel(self.pixelsToMove)
                    pygame.draw.rect(Game.window, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))
                if self.body[pos-1] == seg.atLeft():
                    if( self.started):
                        seg.incrementXInPixel(-self.pixelsToMove)
                    pygame.draw.rect(Game.window, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))
                if self.body[pos-1] == seg.atUp():
                    if( self.started):
                        seg.incrementYInPixel(-self.pixelsToMove)
                    pygame.draw.rect(Game.window, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))
                if self.body[pos-1] == seg.atDown():
                    if( self.started):
                        seg.incrementYInPixel(self.pixelsToMove)
                    pygame.draw.rect(Game.window, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))

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
        
    def handleEvents(self, keys):
        self.compteur = self.compteur + 1
        #if not PlayScreen.perdu and self.compteur >= frames:
        if self.state == 'Alive' and self.compteur >= self.frames:
            print("Keys pressed:",keys)
            isStarted = self.started 
            if isStarted :
                self.update()
            if len(keys) != 0:
                keyPressed= keys.pop()
                if keyPressed == K_RIGHT:
                    self.changeDirection(ALLDIRECTION[2])
                if keyPressed == K_LEFT:
                    self.changeDirection(ALLDIRECTION[3])
                if keyPressed == K_DOWN:
                    self.changeDirection(ALLDIRECTION[1])
                if keyPressed == K_UP:
                    self.changeDirection(ALLDIRECTION[0])
            self.checkDead()
            for seg in self.body:
                seg.reset()
            self.compteur = 0
            self.checkEatApple()
    def checkDead(self):
        head = None

        if self.direction == "up" and  self.head().y > 0:
            head = Position(self.head().x,self.head().y - 1)
        if self.direction == "down" and self.head().y < GAMEHEIGHT-1:
            head = Position(self.head().x,self.head().y + 1)
        if self.direction == "right" and self.head().x < GAMEWIDTH-1:
            head = Position(self.head().x + 1,self.head().y)
        if self.direction == "left" and self.head().x > 0:
            head = Position(self.head().x - 1,self.head().y)
        if head != None:
            if head in self.body:
                self.state = 'Dead'
        else:
            self.state = 'Dead'
    def checkEatApple(self):
        apple = self.parent.apples[-1]
        if self.head() == apple.position:
            apple.crunched = True
            pygame.mixer.music.load(".\son\Crunched.mp3")
            pygame.mixer.music.play()
            print("Apple crunched!")
            self.grow()

class Apple(Component):
    imageApple = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (BOXSIZE-1, BOXSIZE-1))

    def __init__(self, screen):
        super().__init__(screen)
        self.position = Position(random.randint(0,GAMEWIDTH-1), random.randint(0,GAMEHEIGHT-1))
        self.crunched = False
    def draw(self):
        if not self.crunched:
            Game.window.blit(Apple.imageApple, (self.position.xInPixel(), self.position.yInPixel()))


        

   
class HomeScreen(Screen):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.image = pygame.image.load(os.path.join('images', 'Menu.png')).convert()
        self.classic = Button(self, 300,300, 220, 60, "Classique", 50, self.play)
        super().addComponent(self.classic)
        self.options = Button(self, 300,370, 220, 60, "Options", 50, self.showOptions)
        super().addComponent(self.options)
    def play(self):
        self.game.setScreen(PlayScreen(WINDOWWIDTH, WINDOWHEIGHT))
        self.flag = False
    def showOptions(self):
        self.game.setScreen(OptionsScreen(WINDOWWIDTH, WINDOWHEIGHT))
        self.flag = False


class PlayScreen(Screen):
    compteur = 0
    perdu = False

    def __init__(self, width, height):
        super().__init__(width, height)
        self.gameOver = pygame.image.load(os.path.join('images', 'game_over.jpg')).convert()
        self.image = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        self.image.fill(WHITE)
        self.apples = []
        Game.keys = []
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
        self.appleScore.position.setX( 0 )
        self.appleScore.position.setY(-2)
        super().addComponent(self.appleScore)
        apple = Apple(self)
        while apple.position in self.serpent.body:
            apple = Apple(self)
        self.apples.append(apple)
        super().addComponent(apple)
        if os.path.isfile(Game.highScoreFilename): 
            self.file = open(Game.highScoreFilename,"r")
            self.readFile = self.file.read()
            if len(self.readFile) == 0:
                self.hightscore = Game.font.render("Highscore : 0",0,(0,0,0),(255,255,255))    
            else:
                self.hightscore = Game.font.render("Highscore : "+self.readFile,0,(0,0,0),(255,255,255))
            self.file.close()
        else :
                self.hightscore = Game.font.render("Highscore : 0",0,(0,0,0),(255,255,255))    

    def run(self):
        flag = True
        while flag:
            events = pygame.event.get()
            keysPressed = pygame.key.get_pressed()
            for event in events:
                if not PlayScreen.perdu and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        lastKey = None
                        if len(Game.keys) != 0:
                            lastKey = Game.keys[0]
                            if lastKey != event.key and len(Game.keys) < 3:
                                Game.keys.insert(0,event.key)
                        else :
                            Game.keys.insert(0,event.key)

                if event.type == pygame.QUIT:
                    flag = False
                    self.game.screen = None
            print(Game.keys)
            self.serpent.handleEvents(Game.keys)
            if self.serpent.state == 'Dead':
                PlayScreen.perdu = True
            else:
                apple = self.apples[-1]
                if apple.crunched:
                    apple = Apple(self)
                    while apple.position in self.serpent.body:
                        apple = Apple(self)
                    self.apples.append(apple)
            self.draw()
            text = Game.font.render("Score : "+str(len(self.apples)-1),0,(0,0,0),(255,255,255))
            Game.window.blit(text, (180, 125))
            Game.window.blit(self.hightscore, (500, 125))
            self.appleScore.draw()
            self.apples[-1].draw()
            if PlayScreen.perdu:
                self.file = open(Game.highScoreFilename,"w")
                self.file.write(str(len(self.apples)-1))
                self.file.close()
                Game.window.blit(self.gameOver, (240, 360))
                self.game.setScreen(HomeScreen(WINDOWWIDTH, WINDOWHEIGHT)) 
                PlayScreen.perdu = False
                flag = False

            pygame.display.update()
            #print("Coucou",PlayScreen.compteur)
            Game.fpsClock.tick(FPS)

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
        Game.window.blit(text, (300, 300))
        self.music = True
        print("Music ON")
    def off(self):
        print("Music OFF")
        self.music = False
        
game = Game('Snake')
home =HomeScreen(WINDOWWIDTH, WINDOWHEIGHT)
game.setScreen(home) 
game.run()

sys.exit()
