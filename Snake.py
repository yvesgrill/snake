import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
import pygame.sprite
from Games import *
from Colors import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)
BOXSIZE = 20
POSITION_INITX = 561
POSITION_INITY = 281
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
    def __init__(self, cell, selectImage):
        super().__init__("snakeSegment", cell.xInPixel(), cell.yInPixel())
        self.position = cell
        self.target = self.position 
        self.ahead = None
        self.behind = None
        self.selectImage = selectImage
    def addSegmentAtTail(self, selectImage):
        cell = Cell(self.position.x,self.position.y+1, self.position.area)
        s = SnakeSegment(cell,selectImage)
        s.ahead=self
        self.behind = s
        return s
    def grow(self, position):
        cell = Cell(position.x,position.y, self.position.area)
        head = self.head()
        s = SnakeSegment(cell,head.selectImage)
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
        image = pygame.transform.scale(self.selectImage(self),(BOXSIZE,BOXSIZE))
        Game.window.blit(image,(self.position.xInPixel(), self.position.yInPixel()))
        #if self.ahead == self.head():
        #    Game.window.blit(self.selectImage(self),Position.convertPositionToPixel(self.position.x, self.position.y))
    def reset(self):
        self.position.reset()
        #self.position = self.target
class Snake(Component):
    def __init__(self, cell, playArea):
        super().__init__("snake", cell.xInPixel(), cell.yInPixel())
        self.spriteSheet = SpriteSheet("images/snake-graphics.png",32,5,4)
        self.compteur = 0
        self.playArea = playArea
        self.started = False
        self.direction = K_UP
        self.head = SnakeSegment(cell,self.headImage)
        self.tail = self.head.addSegmentAtTail(self.bodyImage).addSegmentAtTail(self.tailImage)
        #self.body = [Position(posx,posy),Position(posx,posy + 1),Position(posx,posy + 2)]
        self.growing =False
        self.alive = True
        self.speed = 6
        self.frames = int(Game.fps/self.speed)
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
        b = self.head.position.y >= 0 and self.head.position.y < self.playArea.height and self.head.position.x < self.playArea.width and self.head.position.x >= 0       
        return not b
    def eatApple(self, apple):
        apple.crunched = True
        sound = pygame.mixer.Sound('./son/Crunched.wav')
        #pygame.mixer.music.load('./son/Crunched.wav')
        sound.play()
        print("Apple crunched!")
        self.grow()

class Apple(Component):
    imageApple = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (BOXSIZE-1, BOXSIZE-1))

    def __init__(self, position):
        super().__init__("apple", position.xip, position.yip)
        self.position = position
        self.crunched = False
    def draw(self):
        if not self.crunched:
            Game.window.blit(Apple.imageApple, (self.position.xInPixel(), self.position.yInPixel()))


class HomeScreen(Screen):
    def __init__(self):
        super().__init__("Home")
        self.image = pygame.image.load(os.path.join('images', 'Menu.png')).convert()
        classic = Button("classicBtn",300,300, 220, 60, "Classique", 50, self.play)
        self.addComponent(classic)
        options = Button("optionsBtn",300,370, 220, 60, "Options", 50, self.showOptions)
        self.addComponent(options)
    def play(self):
        self.game.setScreen("Play")
        self.flag = False
    def showOptions(self):
        self.game.setScreen("Options")
        self.flag = False

class Score(Component):
    def __init__(self, x, y):
        super().__init__("scorePanel", x, y)
    def draw(self):
        Game.window.blit(Apple.imageApple, (self.absoluteX(), self.absoluteY()))
        text = Game.font.render("Score : "+str(len(self.parent.apples)-1),0,(0,0,0),(255,255,255))
        Game.window.blit(text, (self.absoluteX()+40, self.absoluteY()+8))
class GameOver(Component):
    def __init__(self, x, y):
        super().__init__("gameOverPanel",x,y)
        self.gameOver = pygame.image.load(os.path.join('images', 'game_over.jpg')).convert()
    def draw(self):
        Game.window.blit(self.gameOver, (self.absoluteX(), self.absoluteY()))
class HighestScore(Component):
    def __init__(self, x, y):
        super().__init__("highscorePanel", x, y)
        self.value = 0
        if os.path.isfile(Game.highScoreFilename): 
            file = open(Game.highScoreFilename,"r")
            readFile = file.read()
            if len(readFile) > 0:
                self.value = int(readFile)
            file.close()
        self.hightscore = Game.font.render("Highscore : "+str(self.value),0,(0,0,0),(255,255,255))
    def draw(self):
        Game.window.blit(self.hightscore, (self.absoluteX(), self.absoluteY()+8))
    def save(self):
        score = len(self.parent.apples)-1
        if score > self.value : 
            file = open(Game.highScoreFilename,"w")
            file.write(str(score)) 
            file.close()
class PlayArea(Container):
    def __init__(self, x, y, width, height):
        super().__init__("playArea", x, y)
        self.width=width
        self.height = height
        self.image = pygame.Surface((BOXSIZE*width, BOXSIZE*height))
        pygame.draw.rect(self.image, Game.theme.colors['CELL_EVEN'], (0, 0, BOXSIZE*width, BOXSIZE*height))
        for i in range(0, width):
            if(i%2 == 0):
                for j in range(0, int((height+1)/2)):
                    pygame.draw.rect(self.image, Game.theme.colors['CELL_ODD'], (BOXSIZE*i, BOXSIZE*(2*j), BOXSIZE, BOXSIZE))
            if(i%2 == 1):
                for j in range(0, int((height-1)/2)):
                    pygame.draw.rect(self.image, Game.theme.colors['CELL_ODD'], (BOXSIZE*i, BOXSIZE*(2*j)+BOXSIZE, BOXSIZE, BOXSIZE))
    def draw(self):
        Game.window.blit(self.image, (self.absoluteX(),self.absoluteY()))
        super().draw()
    def newApple(self) :
        cell = Cell(random.randint(0,self.width-1), random.randint(0,self.height-1),self)
        return Apple(cell)
    def newSnake(self) :
        cell = Cell(int(self.width/2), int(self.height/2), self)
        return Snake(cell, self)

class Cell:
    def __init__(self, x, y, area):
        self.x = x
        self.xip = x*BOXSIZE+(area.x+1)
        self.y = y
        self.yip = y*BOXSIZE+(area.y+1)
        self.area = area
    def xInPixel(self):
        return round(self.xip)
    def incrementXInPixel(self, n):
        self.xip = self.xip+n
#        return self.x*BOXSIZE+(GAMEAREA_ORIGINX+1)
    def yInPixel(self):
        return round(self.yip)
#        return self.y*BOXSIZE+(GAMEAREA_ORIGINY+1)
    def incrementYInPixel(self, n):
        self.yip = self.yip + n
    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.x == other.x and self.y == other.y
        return False
    def atRight(self):
        return Cell(self.x+1,self.y,self.area)
    def atLeft(self):
        return Cell(self.x-1,self.y,self.area)
    def atUp(self):
        return Cell(self.x,self.y-1,self.area)
    def atDown(self):
        return Cell(self.x,self.y+1,self.area)
    def setX(self, x) :
        self.x = x
        self.xip = x*BOXSIZE+(self.area.x+1)
    def setY(self, y) :
        self.y = y
        self.yip = y*BOXSIZE+(self.area.y+1)
    def reset(self):
        self.xip = self.x*BOXSIZE+(self.area.x+1)
        self.yip = self.y*BOXSIZE+(self.area.y+1)
    def convertPositionToPixel(self,x,y):
        return (x*BOXSIZE+(self.area.x+1),y*BOXSIZE+(self.area.y+1))

class PlayScreen(Screen):
    compteur = 0
    perdu = False
    GAMEAREA_ORIGINX = 130
    GAMEAREA_ORIGINY = 70

    def __init__(self, nbHorizontalCells, nbVerticalCells):
        super().__init__("Play")
        x = (Game.WINDOWWIDTH-(nbHorizontalCells*BOXSIZE))/2
        y = min((Game.WINDOWHEIGHT-(nbVerticalCells*BOXSIZE))/2,PlayScreen.GAMEAREA_ORIGINY)
        self.playArea = PlayArea(int(x),int(y),nbHorizontalCells, nbVerticalCells)
        self.addComponent(self.playArea)
        self.gameOver = GameOver(240, 360)
        self.score = Score(140, 25)
        self.addComponent(self.score)
        self.highestScore = HighestScore(500, 25)
        self.addComponent(self.highestScore)
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
        self.serpent = self.playArea.newSnake()  
        apple = self.playArea.newApple()
        while self.serpent.isAt(apple.position):
            apple = self.playArea.newApple()
        self.apples.append(apple)
        self.addComponent(apple)
        self.addComponent(self.serpent)
        if self.game.screens["Options"].music :
            volume = pygame.mixer.music.get_volume() #Retourne la valeur du volume, entre 0 et 1
            pygame.mixer.music.set_volume(0.2) #Met le volume à 0.5 (moitié)
            pygame.mixer.music.load('./son/theme-music.wav')
            pygame.mixer.music.play(-1)
        
        super().run()
    def update(self, events):
        super().update(events)
        if not self.serpent.alive:
            PlayScreen.perdu = True
            self.highestScore.save()
            self.addComponent(self.gameOver)
            pygame.mixer.music.fadeout(400) #Fondu à 400ms de la fin des musiques
            pygame.mixer.music.stop()
            self.game.setScreen("Home")
            self.flag = False
        else:
            apple = self.apples[-1]
            if apple.crunched:
                apple = self.playArea.newApple()
                while self.serpent.isAt(apple.position):
                    apple = self.playArea.newApple()
                self.apples.append(apple)
                super().addComponent(apple)

class OptionsScreen(Screen):
    def __init__(self):
        super().__init__("Options")
        self.image = pygame.image.load(os.path.join('images', 'Options.png')).convert()
        retour = Button("retourBtn",300,500, 150, 60, "Retour", 50, self.home)
        self.addComponent(retour)
        self.font = pygame.font.Font(None, 40)
        musicOn = Button("musicOnBtn",300,370, 80, 60, "ON", 40, self.on)
        self.addComponent(musicOn)
        musicOff = Button("musicOffBtn",400,370, 80, 60, "OFF", 40, self.off)
        self.addComponent(musicOff)
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
        
theme = Theme()
theme.colors['CELL_EVEN'] = NamedColors.VIOLET
theme.colors['CELL_ODD'] = NamedColors.DARK_VIOLET

game = Game('Snake', 60, theme)
game.addScreen(HomeScreen())
game.addScreen(PlayScreen(17,17))
game.addScreen(OptionsScreen()) 
game.setScreen("Home") 
game.run()

sys.exit()
