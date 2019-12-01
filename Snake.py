import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
from Env import *
from Games import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)



class Snake(Component):
    def __init__(self, posx, posy):
        super().__init__()
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
        self.keys = []
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
            if i == len(self.body)-1:
                if( self.started):
                    if self.direction == "up":
                        seg.incrementYInPixel(-self.pixelsToMove)
                    if self.direction == "down":
                        seg.incrementYInPixel(self.pixelsToMove)
                    if self.direction == "right":
                        seg.incrementXInPixel(self.pixelsToMove)
                    if self.direction == "left":
                        seg.incrementXInPixel(-self.pixelsToMove)
                Game.window.blit(self.headImage(),(seg.xInPixel(), seg.yInPixel()))
            else:
                pos = self.body.index(seg)
                if( self.started):
                    if self.body[pos-1] == seg.atRight():
                        seg.incrementXInPixel(self.pixelsToMove)
                    if self.body[pos-1] == seg.atLeft():
                        seg.incrementXInPixel(-self.pixelsToMove)
                    if self.body[pos-1] == seg.atUp():
                        seg.incrementYInPixel(-self.pixelsToMove)
                    if self.body[pos-1] == seg.atDown():
                        seg.incrementYInPixel(self.pixelsToMove)
                if i == 0:
                    Game.window.blit(self.tailImage(),(seg.xInPixel(), seg.yInPixel()))
                else :
                    Game.window.blit(self.bodyImage(seg),(seg.xInPixel(), seg.yInPixel()))
                    #pygame.draw.rect(Game.window, GREY, (seg.xInPixel(), seg.yInPixel(), BOXSIZE, BOXSIZE))

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

    def headImage(self):
        if self.direction == "up":
            return self.sprite(96, 0)
        if self.direction == "down":
            return self.sprite(128, 32)
        if self.direction == "right":
            return self.sprite(128, 0)
        if self.direction == "left":
            return self.sprite(96, 32)
    def tailImage(self):
        seg = self.body[-1]
        if self.body[-2] == seg.atRight():
            return self.sprite(128, 64)
        if self.body[-2] == seg.atLeft():
            return self.sprite(96, 96)
        if self.body[-2] == seg.atUp():
            return self.sprite(96, 64)
        if self.body[-2] == seg.atDown():
            return self.sprite(128, 96)

    def bodyImage(self,seg):
        pos = self.body.index(seg)
        if self.body[pos-1] == seg.atRight():
            return self.sprite(32, 0)
        if self.body[pos-1] == seg.atLeft():
            return self.sprite(32, 0)
        if self.body[pos-1] == seg.atUp():
            return self.sprite(64, 32)
        if self.body[pos-1] == seg.atDown():
            return self.sprite(64, 32)
    def sprite(self, x,y):
        return self.spriteSheet.subsurface(pygame.Rect(x,y,32,32))
        
    def handleEvents(self, events):
        for event in events:
            if not PlayScreen.perdu and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    lastKey = None
                    if len(self.keys) != 0:
                        lastKey = self.keys[0]
                        if lastKey != event.key and len(self.keys) < 3:
                            self.keys.insert(0,event.key)
                    else :
                        self.keys.insert(0,event.key)
        self.compteur = self.compteur + 1
        #if not PlayScreen.perdu and self.compteur >= frames:
        if self.state == 'Alive' and self.compteur >= self.frames:
            print("Keys pressed:",self.keys)
            isStarted = self.started 
            if isStarted :
                self.update()
            if len(self.keys) != 0:
                keyPressed= self.keys.pop()
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

    def __init__(self):
        super().__init__()
        self.position = Position(random.randint(0,GAMEWIDTH-1), random.randint(0,GAMEHEIGHT-1))
        self.crunched = False
    def draw(self):
        if not self.crunched:
            Game.window.blit(Apple.imageApple, (self.position.xInPixel(), self.position.yInPixel()))


        

   
class HomeScreen(Screen):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.image = pygame.image.load(os.path.join('images', 'Menu.png')).convert()
        self.classic = Button(300,300, 220, 60, "Classique", 50, self.play)
        super().addComponent(self.classic)
        self.options = Button(300,370, 220, 60, "Options", 50, self.showOptions)
        super().addComponent(self.options)
    def play(self):
        self.game.setScreen(PlayScreen(WINDOWWIDTH, WINDOWHEIGHT))
        self.flag = False
    def showOptions(self):
        self.game.setScreen(OptionsScreen(WINDOWWIDTH, WINDOWHEIGHT))
        self.flag = False

class Score(Component):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
    def draw(self):
        Game.window.blit(Apple.imageApple, (self.x, self.y))
        text = Game.font.render("Score : "+str(len(self.parent.apples)-1),0,(0,0,0),(255,255,255))
        Game.window.blit(text, (self.x+40, self.y+8))

class HighestScore(Component):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.value = 0
        if os.path.isfile(Game.highScoreFilename): 
            file = open(Game.highScoreFilename,"r")
            readFile = file.read()
            if len(readFile) > 0:
                self.value = int(readFile)
            file.close()
        self.hightscore = Game.font.render("Highscore : "+str(self.value),0,(0,0,0),(255,255,255))
    def draw(self):
        Game.window.blit(self.hightscore, (self.x, self.y+8))
    def save(self):
        score = len(self.parent.apples)-1
        if score > self.value : 
            file = open(Game.highScoreFilename,"w")
            file.write(str(score)) 
            file.close()

class PlayScreen(Screen):
    compteur = 0
    perdu = False

    def __init__(self, width, height):
        super().__init__(width, height)
        self.gameOver = pygame.image.load(os.path.join('images', 'game_over.jpg')).convert()
        self.image = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        self.image.fill(WHITE)
        self.apples = []
        pygame.draw.rect(self.image, LIGHT_GREEN, (GAMEAREA_ORIGINX, GAMEAREA_ORIGINY, BOXSIZE*(GAMEWIDTH), BOXSIZE*(GAMEHEIGHT)))
        for i in range(0, GAMEWIDTH):
            if(i%2 == 0):
                for j in range(0, int((GAMEHEIGHT+1)/2)):
                    pygame.draw.rect(self.image, DARK_GREEN, (GAMEAREA_ORIGINX+BOXSIZE*i, GAMEAREA_ORIGINY+BOXSIZE*(2*j), BOXSIZE, BOXSIZE))
            if(i%2 == 1):
                for j in range(0, int((GAMEHEIGHT-1)/2)):
                    pygame.draw.rect(self.image, DARK_GREEN, (GAMEAREA_ORIGINX+BOXSIZE*i, GAMEAREA_ORIGINY+BOXSIZE*(2*j)+BOXSIZE, BOXSIZE, BOXSIZE))
        self.score = Score(140, 125)
        super().addComponent(self.score)
        self.highestScore = HighestScore(500, 125)
        super().addComponent(self.highestScore)
        self.serpent = Snake(7,7)  
        apple = Apple()
        while apple.position in self.serpent.body:
            apple = Apple()
        self.apples.append(apple)
        super().addComponent(apple)
        super().addComponent(self.serpent)

    def run(self):
        flag = True
        while flag:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    flag = False
                    self.game.screen = None
            self.handleEvents(events)
            if self.serpent.state == 'Dead':
                PlayScreen.perdu = True
            else:
                apple = self.apples[-1]
                if apple.crunched:
                    apple = Apple()
                    while apple.position in self.serpent.body:
                        apple = Apple()
                    self.apples.append(apple)
                    super().addComponent(apple)
            self.draw()
            if PlayScreen.perdu:
                self.highestScore.save()
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
        self.retour = Button(300,500, 150, 60, "Retour", 50, self.home)
        super().addComponent(self.retour)
        self.font = pygame.font.Font(None, 40)
        self.musicOn = Button(300,370, 80, 60, "ON", 40, self.on)
        super().addComponent(self.musicOn)
        self.musicOff = Button(400,370, 80, 60, "OFF", 40, self.off)
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
