import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
import pygame.sprite
import gui 
from gui.PgButton import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)
POSITION_INITX = 561
POSITION_INITY = 281

class Cell:
    SIZE = 32
    def __init__(self, i, j, map, blocking = False):
        #super().__init__("Cell("+str(i)+","+str(j)+")", i*Cell.SIZE, j*Cell.SIZE)
        self.i = i
        self.j = j
        self.map = map
        self.imageId = None
        self.x = i*Cell.SIZE
        self.y = j*Cell.SIZE
        self.blocking = blocking
    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.i == other.i and self.j == other.j
        return False
    def __str__(self):
        return "Cell("+str(self.i)+","+str(self.j)+")"
    def atRight(self):
        return self.map.cell(self.i+1,self.j)
    def atLeft(self):
        return self.map.cell(self.i-1,self.j)
    def atUp(self):
        return self.map.cell(self.i,self.j-1)
    def atDown(self):
        return self.map.cell(self.i,self.j+1)
    def reset(self):
        self.x = self.i*Cell.SIZE+(self.map.area.position.x+1)
        self.y = self.j*Cell.SIZE+(self.map.area.position.y+1)
    def convertPositionToPixel(self,x,y):
        return (x*Cell.SIZE+(self.map.area.position.x+1),y*Cell.SIZE+(self.map.area.position.y+1))
    def absoluteX(self):
        return self.x+self.map.area.position.x
    def absoluteY(self):
        return self.y+self.map.area.position.y
    def draw(self ):
        #print("Draw Cell ", self.i, self.j)
        self.map.area.surface.blit(self.map.spriteSheet.image_by_id(self.imageId), (self.x, self.y))
    def draw_image(self,image):
        self.map.area.surface.blit(image, (self.x, self.y))
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
class SnakeSegment:
    def __init__(self, cell, selectImage):
        self.cell = cell 
        self.target = self.cell
        self.ahead = None
        self.behind = None
        self.selectImage = selectImage
        self.xf = self.cell.x
        self.yf = self.cell.y
    def addSegmentAtTail(self, selectImage):
        #cell = Cell(self.cell.i,self.cell.j+1, self.cell.area)
        s = SnakeSegment(self.cell.atDown(),selectImage)
        s.ahead = self
        self.behind = s
        return s
    def grow(self, cell):
        #cell = Cell(cell.i,cell.j, self.cell.area)
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
            if self.ahead.cell.i != self.behind.cell.i and self.ahead.cell.j != self.behind.cell.j:
                return True                
        return False
    def moveTo(self, target):
        if self.behind != None:
            self.behind.moveTo(self.cell)
        self.cell = target
    def forward(self):
        return SegmentIterator(self, 'forward')
    def backward(self):
        return SegmentIterator(self, 'backward')
    def draw(self):
        image = pygame.transform.scale(self.selectImage(self),(Cell.SIZE,Cell.SIZE))
        self.cell.draw_image(image)
    def reset(self):
     #   self.reset()
        self.cell = self.cell
    def incrementXInPixel(self, n):
        self.xf = self.xf+n
        self.x = round(self.xf)
    def incrementYInPixel(self, n):
        self.yf = self.yf + n
        self.y = round(self.yf)
class Snake:
    def __init__(self, cell,spriteSheet):
        #super().__init__("snake", cell.x, cell.y)
        self.playArea = cell.map.area
        self.spriteSheet = spriteSheet
        self.compteur = 0
        self.started = False
        self.direction = K_UP
        self.head = SnakeSegment(cell,self.headImage)
        body = self.head.addSegmentAtTail(self.bodyImage)
        self.tail = body.addSegmentAtTail(self.tailImage)

        #self.body = [Position(posx,posy),Position(posx,posy + 1),Position(posx,posy + 2)]
        self.growing =False
        self.alive = True
        self.speed = 6
        self.frames = int(Application.fps/self.speed)
        self.pixelsToMove = Cell.SIZE/self.frames      
        self.target = self.head.cell.atUp()
        self.keysPressed = []
        #print("Pixels to move:",self.pixelsToMove )
        #pygame.sprite.Sprite.__init__(self)
    def __str__(self):
        return "Snake:"+str(self.head)
    def isAt(self, pos):
        if self.head.cell == pos:
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
                target = self.head.cell.atUp()
        if self.direction == K_DOWN:
                target = self.head.cell.atDown()
        if self.direction == K_RIGHT:
                target = self.head.cell.atRight()
        if self.direction == K_LEFT:
                target = self.head.cell.atLeft()
        if target != None:
            print("Target:",target.i, target.j)
        return target
    def draw(self):
        for seg in self.tail.forward():
            if(self.started and False):
                if seg.isHead():
                    if self.target == seg.atUp():
                        seg.incrementYInPixel(-self.pixelsToMove)
                    if self.target == seg.atDown():
                        seg.incrementYInPixel(self.pixelsToMove)
                    if self.target == seg.atRight():
                        seg.incrementXInPixel(self.pixelsToMove)
                    if self.target == seg.atLeft():
                        seg.incrementXInPixel(-self.pixelsToMove)
                elif seg.isTail():
                    if seg.ahead == seg.atUp():
                        seg.incrementYInPixel(-self.pixelsToMove)
                    if seg.ahead == seg.atDown():
                        seg.incrementYInPixel(self.pixelsToMove)
                    if seg.ahead == seg.atRight():
                        seg.incrementXInPixel(self.pixelsToMove)
                    if seg.ahead == seg.atLeft():
                        seg.incrementXInPixel(-self.pixelsToMove)
                elif not seg.isCorner():
                    print("not a corner")
                    if seg.ahead == seg.atUp():
                        seg.incrementYInPixel(-self.pixelsToMove)
                    if seg.ahead == seg.atDown():
                        seg.incrementYInPixel(self.pixelsToMove)
                    if seg.ahead == seg.atRight():
                        seg.incrementXInPixel(self.pixelsToMove)
                    if seg.ahead == seg.atLeft():
                        seg.incrementXInPixel(-self.pixelsToMove)
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
        if self.target == seg.cell.atUp():
            return self.spriteSheet.image(3,0)
        if self.target == seg.cell.atDown():
            return self.spriteSheet.image(4,1)
        if self.target == seg.cell.atRight():
            return self.spriteSheet.image(4,0)
        if self.target == seg.cell.atLeft():
            return self.spriteSheet.image(3,1)
    def tailImage(self,seg):
        #print("Tail image",seg)
        if seg.ahead.cell == seg.cell.atUp():
            return self.spriteSheet.image(3,2)
        if seg.ahead.cell == seg.cell.atDown():
            return self.spriteSheet.image(4,3)
        if seg.ahead.cell == seg.cell.atRight():
            return self.spriteSheet.image(4,2)
        if seg.ahead.cell == seg.cell.atLeft():
            return self.spriteSheet.image(3,3)

    def bodyImage(self,seg):
        #print("Body: ",seg.position.x,seg.position.y)
        #print("Body target: ",seg.target.x,seg.target.y)
        #print("Ahead position: ",seg.ahead.position.x,seg.ahead.position.y)
        #print("Ahead target: ",seg.ahead.target.x,seg.ahead.target.y)
        #print("Behind position: ",seg.behind.position.x,seg.behind.position.y)
        #print("Behind target: ",seg.behind.target.x,seg.behind.target.y)
        if seg.ahead.cell == seg.cell.atUp() :
            if seg.behind.cell == seg.cell.atDown():
                return self.spriteSheet.image(2,1)
            if seg.behind.cell == seg.cell.atLeft():
                return self.spriteSheet.image(2,2)
            else :
                return self.spriteSheet.image(0,1)
        if seg.ahead.cell == seg.cell.atDown() :
            if seg.behind.cell == seg.cell.atUp():
                return self.spriteSheet.image(2,1)
            if seg.behind.cell == seg.cell.atLeft():
                return self.spriteSheet.image(2,0)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.cell == seg.cell.atRight() :
            if seg.behind.cell == seg.cell.atLeft():
                return self.spriteSheet.image(1,0)
            if seg.behind.cell == seg.cell.atUp():
                return self.spriteSheet.image(0,1)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.cell == seg.cell.atLeft() :
            if seg.behind.cell == seg.cell.atRight():
                return self.spriteSheet.image(1,0)
            if seg.behind.cell == seg.cell.atUp():
                return self.spriteSheet.image(2,2)
            else :
                return self.spriteSheet.image(2,0)
        
    def on_handle_event(self, event):
        if self.alive :
            #for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        lastKey = None
                        if len(self.keysPressed) != 0:
                            lastKey = self.keysPressed[0]
                            if lastKey != event.key and len(self.keysPressed) < 3:
                                self.keysPressed.insert(0,event.key)
                        else :
                            self.keysPressed.insert(0,event.key)
    def update(self):
        if self.alive :
            if self.started:
                self.compteur = self.compteur + 1
                if self.compteur >= self.frames:
                    print("Keys pressed:",self.keysPressed)
                    self.handleKeyPressed()
                    self.move()
                    if self.checkAlive():
                        #for seg in self.head.backward():
                        #    seg.reset()
                        apple = self.playArea.apple
                        if self.isAt(apple.cell):
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
            if self.headTouchBody():
                self.alive = False
        else:
            self.alive = False
        return self.alive
    def headTouchBody(self):
        pos = self.head.cell
        for seg in self.head.behind.backward():
            if seg.cell == pos:
                return True
        return False
    def headTouchWall(self):
        #b = self.head.cell.j >= 0 and self.head.cell.j < self.playArea.height and self.head.cell.i < self.playArea.width and self.head.cell.i >= 0       
        for line in self.playArea.map.cells:
            for cell in line:
                if cell.blocking and self.isAt(cell):
                    return True
        return False
    def eatApple(self, apple):
        apple.crunched = True
        sound = pygame.mixer.Sound('./son/Crunched.wav')
        #pygame.mixer.music.load('./son/Crunched.wav')
        sound.play()
        print("Apple crunched!")
        self.grow()

class Apple:
    def __init__(self, cell, spriteSheet):
        self.image = pygame.transform.scale(spriteSheet.image(0,3), (Cell.SIZE, Cell.SIZE))
        self.cell = cell
        self.crunched = False
    def draw(self):
        if not self.crunched:
            self.cell.draw_image(self.image)


class HomeWindow(Window):
    def __init__(self):
        super().__init__("homeWindow")
        classic = Button("classicBtn",(300,300), (220, 60), "Classique", self.play, 'home')
        self.add_component(classic)
        options = Button("optionsBtn",(300,370), (220, 60), "Options", self.showOptions, 'home')
        self.add_component(options)
        quit = PygButton((300,440),(220, 60), "Quit")
        self.add_component(quit)
        #self.style.background.image='Menu.png'
        print("id=", options.get_id())
    def play(self):
        self.application.show_window("gameBoard")
    def showOptions(self):
        self.application.show_window("optionsWindow")

class Score(Container):
    def __init__(self, position, dimension):
        super().__init__("scorePanel", position, dimension)
        icon = ImageView("imageView", (0,0), (Cell.SIZE, Cell.SIZE),'Pomme.png')
        self.add_component(icon)
        #icon = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (Cell.SIZE, Cell.SIZE))
        #self.surface.blit(icon, (0, 0))
        self.title = "Score : %s"
        text = self.title % 0
        self.label = Label("label", (Cell.SIZE+1,0), (100, Cell.SIZE),text)
        self.add_component(self.label)
        
    def update(self):
        super().update()
        text = self.title % str(len(self.container.apples)-1)
        self.label.set_text(text)

class GameOver(Component):
    def __init__(self, position, dimension):
        super().__init__("gameOverPanel",position,dimension)
    def update(self):
        self.surface = pygame.transform.scale(pygame.image.load(os.path.join('images', 'game_over.jpg')).convert(), self.get_dimension())
    def on_handle_event(self, event):
        w = self.surface.get_width()
        h = self.surface.get_height()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.absoluteX()+w > event.pos[0] > self.absoluteX() and self.absoluteY()+h > event.pos[1]> self.absoluteY():
                self.container.stop()
class HighestScore(Component):
    filename = "hightscore.txt"
    def __init__(self, position, dimension):
        super().__init__("highscorePanel", position, dimension)
        self.value = 0
        if os.path.isfile(HighestScore.filename): 
            file = open(HighestScore.filename,"r")
            readFile = file.read()
            if len(readFile) > 0:
                self.value = int(readFile)
            file.close()
    def update(self):
        super().update()
        hightscore = self.get_font().render("Highscore : "+str(self.value),0,(0,0,0),(255,255,255))
        self.surface.blit(hightscore, (0, 8))
    def save(self):
        score = len(self.container.apples)-1
        if score > self.value : 
            file = open(HighestScore.filename,"w")
            file.write(str(score)) 
            file.close()
class PlayArea(Component):
    def __init__(self, position, map,spriteSheet):
        super().__init__("playArea", position, (Cell.SIZE*map.width,Cell.SIZE*map.height))
        self.spriteSheet = spriteSheet
        self.gridWidth  = map.width
        self.gridHeight = map.height
        self.snake = None
        self.apple = None
        self.map = map
        self.map.area = self
        print("taille=",self.gridWidth, self.gridHeight)
#        pygame.draw.rect(self.surface, Application.theme.colors['CELL_EVEN'], (0, 0, self.width, self.height))
#        for j in range(0, self.gridHeight):
#            for i in range(0, self.gridWidth):
#                n = i+(j*self.gridWidth)
#                if(n%2 == 0):
#                    pygame.draw.rect(self.surface, Application.theme.colors['CELL_ODD'], (Cell.SIZE*i, Cell.SIZE*j, Cell.SIZE, Cell.SIZE))
#        j=0
#        for row in map.cells:                
#            i=0
#            for cell in row:
#                if cell == PlayMap.BLOCK:
#                    self.addWallElement(i, j)
#                if cell == PlayMap.START:
#                    self.startCell = (i,j)
#                i = i+1
#            j = j+1

    def draw(self):
        #self.application.display.blit(self.surface, (self.absoluteX(),self.absoluteY()))
        for line in self.map.cells:
            for cell in line:
                cell.draw( )
        self.apple.draw()
        self.snake.draw()
        super().draw()
    def on_handle_event(self, event):
        if event.type == USEREVENT:
            self.snake.update()
        else:
            self.snake.on_handle_event(event)
    def addApple(self) :
        cell = self.map.cell(random.randint(0,self.gridWidth-1), random.randint(0,self.gridHeight-1))
        while self.inSnake(cell) or self.inWall(cell):
            cell = self.map.cell(random.randint(0,self.gridWidth-1), random.randint(0,self.gridHeight-1))
        self.apple = Apple(cell, self.spriteSheet)
        return self.apple
    def inWall(self, cell):
        return cell.blocking
    def inSnake(self, cell):
        for seg in self.snake.head.backward():
            if seg.cell == cell:
                return True
        return False
    def addSnake(self) :
        cell = self.map.cell(*self.map.startCell)
        self.snake = Snake(cell, self.spriteSheet)
        print("Snake:",self.snake, self.snake.head.cell.x, self.snake.head.cell.y, self.snake.head.cell.absoluteX(), self.snake.head.cell.absoluteY())
    def reset(self):
        self.apple = None
        self.snake = None

class GameBoard(Window):
    GAMEAREA_ORIGINX = 130
    GAMEAREA_ORIGINY = 70

    def __init__(self, levelMap, cellSize=32):
        super().__init__("gameBoard")
        Cell.SIZE=cellSize
        spriteSheet = SpriteSheet("images/snake-graphics.png",32,5,4)
        map = PlayMap(levelMap, spriteSheet)

        x = min([(Application.WINDOWWIDTH-(map.width*Cell.SIZE))/2,GameBoard.GAMEAREA_ORIGINX])
        y = min([(Application.WINDOWHEIGHT-(map.height*Cell.SIZE))/2,GameBoard.GAMEAREA_ORIGINY])
        print("W1=",Application.WINDOWWIDTH)
        print("POS=",x,y)

        self.playArea = PlayArea((int(x),int(y)),map,spriteSheet)
        self.add_component(self.playArea)
        self.applicationOver = GameOver((240, 360), (300,300))
        self.score = Score((140, 25), (200,50))
        self.add_component(self.score)
        self.highestScore = HighestScore((500, 25), (150,50))
        self.add_component(self.highestScore)
        self.apples = []

    def run(self):
        self.playFinished = False
        self.remove_component(self.applicationOver)
        print("components",self.components)
        self.apples = []
        self.playArea.reset()  
        self.playArea.addSnake()  
        apple = self.playArea.addApple()
        self.apples.append(apple)
        if self.application.get_window("optionsWindow").music :
            volume = pygame.mixer.music.get_volume() #Retourne la valeur du volume, entre 0 et 1
            pygame.mixer.music.set_volume(0.2) #Met le volume à 0.5 (moitié)
            pygame.mixer.music.load('./son/theme-music.wav')
            pygame.mixer.music.play(-1)
        
        super().run()
    def on_handle_event(self, events):
        super().on_handle_event(events)
        if not self.playFinished:
            if not self.playArea.snake.alive:
                self.highestScore.save()
                self.add_component(self.applicationOver)
                self.playFinished = True
            else:
                apple = self.apples[-1]
                if apple.crunched:
                    apple = self.playArea.addApple()
                    self.apples.append(apple)
    def stop(self):
        pygame.mixer.music.fadeout(400) #Fondu à 400ms de la fin des musiques
        pygame.mixer.music.stop()
        self.hide()

class PlayMap :
    EMPTY = '.'
    BLOCK = 'X'
    START = 'O'
    def __init__(self, level, spriteSheet):
        self.spriteSheet = spriteSheet
        self.cells = []
        self.area = None
        w = j = 0
        path = os.path.join('maps', level+"_blocking_map.txt")
        f = open(path, "r")
        for line in f:
            line = line.rstrip('\n')
            w = max(w, len(line))
            self.cells.append([])    
            i = 0
            for c in line:
                self.cells[j].append(Cell(i,j, self,c==PlayMap.BLOCK))
                if c == PlayMap.START:
                    self.startCell = (i,j)
                i += 1
            j += 1
        path = os.path.join('maps', level+"_tiles_map.txt")
        f = open(path, "r")
        j = 0
        for line in f:
            line = line.rstrip('\n')
            ids = line.split(' ') 
            i = 0
            for id in ids:
                #print("Cell ",i,j,id)
                self.cells[j][i].imageId = id
                i += 1
            j += 1
        self.width = w
        self.height = j
    def cell(self, i,j):
        #print("cell ",i,j)
        if i<0 or j<0 or i >=self.width or j >= self.height:
            return None         
        return self.cells[j][i]
    def __str__(self):
        return str(self.cells)
class OptionsWindow(Window):
    def __init__(self):
        super().__init__("optionsWindow", position=(50,50), dimension=(500,600))
        retour = Button("retourBtn",(300,500), (150, 60), "Retour", self.cancel)
        self.add_component(retour)
        musicOn = Button("musicOnBtn",(300,370), (80, 60), "ON", self.on)
        self.add_component(musicOn)
        musicOff = Button("musicOffBtn",(400,370), (80, 60), "OFF", self.off)
        self.add_component(musicOff)
        self.music = True
        self.style.font.size=42
        self.style.background.image='Options.png'
    def cancel(self):
        self.hide()
    def update(self):
        super().update()
        if self.music:
            text = self.get_font().render("Music",0,(0,0,0),None)
            self.surface.blit(text, (300, 300))
    def on(self):
        self.music = True
        print("Music ON")
    def off(self):
        print("Music OFF")
        self.music = False

theme = Theme.parseCss("default")
game = Application('Snake', 60, theme)
game.add_window(HomeWindow(),True)
game.add_window(GameBoard("classique", 32))
game.add_window(OptionsWindow())
game.run()

sys.exit()
