import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
import pygame.sprite

from Env import *
from Games import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)

class SegmentIterator :
    def __init__(self,segment, direction):
        self.segment = segment
        self.direction = direction

    def __iter__(self):
        return self

    def __next__(self):
        if self.segment == None:
            raise StopIteration()
        else :
            s = self.segment
            if self.direction =='forward':
                self.segment = self.segment.ahead
            else :
                self.segment = self.segment.behind
            return s
class SnakeSegment(Component):
    def __init__(self, posx, posy, selectImage):
        self.position = Position(posx,posy)
        self.target = self.position 
        self.ahead = None
        self.behind = None
        self.selectImage = selectImage
    def addSegmentAtTail(self, selectImage):
        s = SnakeSegment(self.position.x,self.position.y+1,selectImage)
        s.ahead=self
        self.behind = s
        return s
    def grow(self, position):
        head = self.head()
        s = SnakeSegment(position.x,position.y,head.selectImage)
        head.ahead=s
        s.behind = head
        head.selectImage = head.behind.selectImage
        return s
    def head(self):
        s = self
        while s.ahead != None:
            s = s.ahead       
        return s
    def tail(self):
        s = self
        while s.behind != None:
            s = s.behind       
        return s
    def isHead(self):
        return self.ahead == None
    def isTail(self):
        return self.behind == None
    def isTrunk(self):
        return self.ahead != None and self.behind != None
    def isCorner(self):
        if self.isTrunk() :
            if self.ahead.position.x != self.behind.position.x and self.ahead.position.y != self.behind.position.y:
                return True                
        return False
    def moveTo(self, target):
        if self.behind != None:
            self.behind.moveTo(self.position)
        self.position = target
    def forward(self):
        return SegmentIterator(self, 'forward')
    def backward(self):
        return SegmentIterator(self, 'backward')
    def draw(self):
        Game.window.blit(self.selectImage(self),(self.position.xInPixel(), self.position.yInPixel()))
        #if self.ahead == self.head():
        #    Game.window.blit(self.selectImage(self),Position.convertPositionToPixel(self.position.x, self.position.y))
    def reset(self):
        self.position.reset()
        #self.position = self.target
class Snake(Component):
    def __init__(self, posx, posy):
        super().__init__("snake")
        self.spriteSheet = SpriteSheet("images/snake-graphics.png",32,5,4)
        self.compteur = 0
        self.started = False
        self.direction = K_UP
        self.head = SnakeSegment(posx,posy,self.headImage)
        self.tail = self.head.addSegmentAtTail(self.bodyImage).addSegmentAtTail(self.tailImage)
        #self.body = [Position(posx,posy),Position(posx,posy + 1),Position(posx,posy + 2)]
        self.growing =False
        self.alive = True
        self.speed = 6
        self.frames = int(FPS/self.speed)
        self.pixelsToMove = BOXSIZE/self.frames      
        self.target = self.head.position.atUp()
        self.keysPressed = []
        #print("Pixels to move:",self.pixelsToMove )
        #pygame.sprite.Sprite.__init__(self)
   
    def isAt(self, pos):
        for seg in self.head.backward():
            if seg.position == pos:
                return True
        return False
    def move(self):
        if self.growing:
            self.head = self.head.grow(self.target)
            self.growing = False
        else :
            self.head.moveTo(self.target)
        self.target = self.computeTarget()
    def changeDirection(self, direction):
        if self.direction == K_UP and direction == K_DOWN:
            return
        if self.direction == K_DOWN and direction == K_UP:
            return
        if self.direction == K_RIGHT and direction == K_LEFT:
            return
        if self.direction == K_LEFT and direction == K_RIGHT:
            return       
        self.started = True
        #print("Change direction to ",direction)
        self.direction = direction
        self.target = self.computeTarget()
        #self.head.changeTarget(self.target)
    def computeTarget(self) :
        target = None
        if self.direction == K_UP:
                target = self.head.position.atUp()
        if self.direction == K_DOWN:
                target = self.head.position.atDown()
        if self.direction == K_RIGHT:
                target = self.head.position.atRight()
        if self.direction == K_LEFT:
                target = self.head.position.atLeft()
        if target != None:
            print("Target:",target.x, target.y)
        return target
    def draw(self):
        for seg in self.tail.forward():
            if(self.started and False):
                if seg.isHead():
                    if self.target == seg.position.atUp():
                        seg.position.incrementYInPixel(-self.pixelsToMove)
                    if self.target == seg.position.atDown():
                        seg.position.incrementYInPixel(self.pixelsToMove)
                    if self.target == seg.position.atRight():
                        seg.position.incrementXInPixel(self.pixelsToMove)
                    if self.target == seg.position.atLeft():
                        seg.position.incrementXInPixel(-self.pixelsToMove)
                elif seg.isTail():
                    if seg.ahead.position == seg.position.atUp():
                        seg.position.incrementYInPixel(-self.pixelsToMove)
                    if seg.ahead.position == seg.position.atDown():
                        seg.position.incrementYInPixel(self.pixelsToMove)
                    if seg.ahead.position == seg.position.atRight():
                        seg.position.incrementXInPixel(self.pixelsToMove)
                    if seg.ahead.position == seg.position.atLeft():
                        seg.position.incrementXInPixel(-self.pixelsToMove)
                elif not seg.isCorner():
                    print("not a corner")
                    if seg.ahead.position == seg.position.atUp():
                        seg.position.incrementYInPixel(-self.pixelsToMove)
                    if seg.ahead.position == seg.position.atDown():
                        seg.position.incrementYInPixel(self.pixelsToMove)
                    if seg.ahead.position == seg.position.atRight():
                        seg.position.incrementXInPixel(self.pixelsToMove)
                    if seg.ahead.position == seg.position.atLeft():
                        seg.position.incrementXInPixel(-self.pixelsToMove)
            seg.draw()
    def grow(self):
        self.growing = True
    #def print(self) :
        #print("Head(",self.head.x,",",self.head.y,")")
        #for seg in self.body:
            #print("Body(",seg.x,",",seg.y,")")
        #print("Tail(", self.tail.x,",",self.tail.y,")")

    def headImage(self,seg):
        #print("Head image",seg)
        if self.target == seg.position.atUp():
            return self.spriteSheet.image(3,0)
        if self.target == seg.position.atDown():
            return self.spriteSheet.image(4,1)
        if self.target == seg.position.atRight():
            return self.spriteSheet.image(4,0)
        if self.target == seg.position.atLeft():
            return self.spriteSheet.image(3,1)
    def tailImage(self,seg):
        #print("Tail image",seg)
        if seg.ahead.position == seg.position.atUp():
            return self.spriteSheet.image(3,2)
        if seg.ahead.position == seg.position.atDown():
            return self.spriteSheet.image(4,3)
        if seg.ahead.position== seg.position.atRight():
            return self.spriteSheet.image(4,2)
        if seg.ahead.position == seg.position.atLeft():
            return self.spriteSheet.image(3,3)

    def bodyImage(self,seg):
        #print("Body: ",seg.position.x,seg.position.y)
        #print("Body target: ",seg.target.x,seg.target.y)
        #print("Ahead position: ",seg.ahead.position.x,seg.ahead.position.y)
        #print("Ahead target: ",seg.ahead.target.x,seg.ahead.target.y)
        #print("Behind position: ",seg.behind.position.x,seg.behind.position.y)
        #print("Behind target: ",seg.behind.target.x,seg.behind.target.y)
        if seg.ahead.position == seg.position.atUp() :
            if seg.behind.position == seg.position.atDown():
                return self.spriteSheet.image(2,1)
            if seg.behind.position == seg.position.atLeft():
                return self.spriteSheet.image(2,2)
            else :
                return self.spriteSheet.image(0,1)
        if seg.ahead.position == seg.position.atDown() :
            if seg.behind.position == seg.position.atUp():
                return self.spriteSheet.image(2,1)
            if seg.behind.position == seg.position.atLeft():
                return self.spriteSheet.image(2,0)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.position == seg.position.atRight() :
            if seg.behind.position == seg.position.atLeft():
                return self.spriteSheet.image(1,0)
            if seg.behind.position == seg.position.atUp():
                return self.spriteSheet.image(0,1)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.position == seg.position.atLeft() :
            if seg.behind.position == seg.position.atRight():
                return self.spriteSheet.image(1,0)
            if seg.behind.position == seg.position.atUp():
                return self.spriteSheet.image(2,2)
            else :
                return self.spriteSheet.image(2,0)
        
    def update(self, events):
        if self.alive :
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        lastKey = None
                        if len(self.keysPressed) != 0:
                            lastKey = self.keysPressed[0]
                            if lastKey != event.key and len(self.keysPressed) < 3:
                                self.keysPressed.insert(0,event.key)
                        else :
                            self.keysPressed.insert(0,event.key)
            if self.started:
                self.compteur = self.compteur + 1
                if self.compteur >= self.frames:
                    print("Keys pressed:",self.keysPressed)
                    self.handleKeyPressed()
                    self.move()
                    if self.checkAlive():
                        for seg in self.head.backward():
                            seg.reset()
                        apple = self.parent.apples[-1]
                        if self.head.position == apple.position:
                            self.eatApple(apple)
                    self.compteur = 0
            else:
                self.handleKeyPressed()
    def handleKeyPressed(self):
        if len(self.keysPressed) > 0:
            keyPressed = self.keysPressed.pop()
            self.changeDirection(keyPressed)
    def checkAlive(self):
        if not self.headTouchWall():
            if self.isAt(self.target):
                self.alive = False
        else:
            self.alive = False
        return self.alive
    def headTouchWall(self):
        b = self.head.position.y >= 0 and self.head.position.y < GAMEHEIGHT and self.head.position.x < GAMEWIDTH and self.head.position.x >= 0       
        return not b
    def eatApple(self, apple):
        apple.crunched = True
        pygame.mixer.music.load(".\son\Crunched.mp3")
        pygame.mixer.music.play()
        print("Apple crunched!")
        self.grow()

class Apple(Component):
    imageApple = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (BOXSIZE-1, BOXSIZE-1))

    def __init__(self):
        super().__init__("apple")
        self.position = Position(random.randint(0,GAMEWIDTH-1), random.randint(0,GAMEHEIGHT-1))
        self.crunched = False
    def draw(self):
        if not self.crunched:
            Game.window.blit(Apple.imageApple, (self.position.xInPixel(), self.position.yInPixel()))



class HomeScreen(Screen):
    def __init__(self, width, height):
        super().__init__("Home",width, height)
        self.image = pygame.image.load(os.path.join('images', 'Menu.png')).convert()
        classic = Button("classicBtn",300,300, 220, 60, "Classique", 50, self.play)
        super().addComponent(classic)
        options = Button("optionsBtn",300,370, 220, 60, "Options", 50, self.showOptions)
        super().addComponent(options)
    def play(self):
        self.game.setScreen("Play")
        self.flag = False
    def showOptions(self):
        self.game.setScreen("Options")
        self.flag = False

class Score(Component):
    def __init__(self, x, y):
        super().__init__("scorePanel")
        self.x = x
        self.y = y
    def draw(self):
        Game.window.blit(Apple.imageApple, (self.x, self.y))
        text = Game.font.render("Score : "+str(len(self.parent.apples)-1),0,(0,0,0),(255,255,255))
        Game.window.blit(text, (self.x+40, self.y+8))
class GameOver(Component):
    def __init__(self, x, y):
        super().__init__("gameOverPanel")
        self.gameOver = pygame.image.load(os.path.join('images', 'game_over.jpg')).convert()
        self.x = x
        self.y = y
    def draw(self):
        Game.window.blit(self.gameOver, (self.x, self.y))
class HighestScore(Component):
    def __init__(self, x, y):
        super().__init__("highscorePanel")
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
        super().__init__("Play",width, height)
        self.gameOver = GameOver(240, 360)
        self.image = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        self.image.fill(WHITE)
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
        self.removeComponent(self.gameOver)
        PlayScreen.perdu = False
        self.apples = []
        self.serpent = None

    def run(self):
        for apple in self.apples:
            self.removeComponent(apple)
        if self.serpent != None:
            self.removeComponent(self.serpent)
        self.removeComponent(self.gameOver)

        self.apples = []
        PlayScreen.perdu = False
        self.serpent = Snake(7,7)  
        apple = Apple()
        while self.serpent.isAt(apple.position):
            apple = Apple()
        self.apples.append(apple)
        self.addComponent(apple)
        self.addComponent(self.serpent)
        super().run()
    def update(self, events):
        super().update(events)
        if not self.serpent.alive:
            PlayScreen.perdu = True
            self.highestScore.save()
            self.addComponent(self.gameOver)
            self.game.setScreen("Home")
            self.flag = False
        else:
            apple = self.apples[-1]
            if apple.crunched:
                apple = Apple()
                while self.serpent.isAt(apple.position):
                    apple = Apple()
                self.apples.append(apple)
                super().addComponent(apple)

class OptionsScreen(Screen):
    def __init__(self, width, height):
        super().__init__("Options",width, height)
        self.image = pygame.image.load(os.path.join('images', 'Options.png')).convert()
        retour = Button("retourBtn",300,500, 150, 60, "Retour", 50, self.home)
        super().addComponent(retour)
        self.font = pygame.font.Font(None, 40)
        musicOn = Button("musicOnBtn",300,370, 80, 60, "ON", 40, self.on)
        super().addComponent(musicOn)
        musicOff = Button("musicOffBtn",400,370, 80, 60, "OFF", 40, self.off)
        super().addComponent(musicOff)
        self.music = True
    def home(self):
        self.game.setScreen("Home")
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
game.addScreen(HomeScreen(WINDOWWIDTH, WINDOWHEIGHT))
game.addScreen(PlayScreen(WINDOWWIDTH, WINDOWHEIGHT))
game.addScreen(OptionsScreen(WINDOWWIDTH, WINDOWHEIGHT)) 
game.setScreen("Home") 
game.run()

sys.exit()
