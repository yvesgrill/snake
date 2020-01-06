import random, time, pygame, sys, os
from pygame.locals import *
import pygame.mixer
import pygame.time
import pygame.sprite
from gui import * 
from game import * 
import getpass
from operator import attrgetter
import logging

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 150)
POSITION_INITX = 561
POSITION_INITY = 281

class Direction:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def get_inverse(self):
        return Direction(-self.x,-self.y)
    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.x == other.x and self.y == other.y
        return False

UP = Direction(0,-1)
DOWN = Direction(0,1)
LEFT = Direction(-1,0)
RIGHT = Direction(1,0)


class SegmentIterator :
    FORWARD = 'forward'
    BACKWARD = 'backward'
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
            if self.direction == SegmentIterator.FORWARD:
                self.segment = self.segment.ahead
            else :
                self.segment = self.segment.behind
            return s
class SnakeSegment(pygame.sprite.Sprite):
    def __init__(self, cell, snake, orientation):
        pygame.sprite.Sprite.__init__(self)                
        self.cell = cell 
        self.ahead = None
        self.behind = None
        self.snake = snake        
        self.snake.add(self)         
        self.orientation = orientation
    def addSegmentBehind(self):
        shift = self.orientation.get_inverse()
        s = SnakeSegment(self.cell.at(shift.x,shift.y),self.snake,self.orientation)
        s.ahead = self
        if self.behind != None:
            self.behind.ahead = s
            s.behind = self.behind
        self.behind = s
        return s
    def addSegmentAhead(self, shift):
        s = SnakeSegment(self.cell.at(shift.x,shift.y),self.snake,shift)
        s.behind = self
        if self.ahead != None:
            self.ahead.behind = s
            s.ahead = self.ahead
        self.ahead = s
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
        self.cell.drawn = False
        if self.behind != None:
            self.behind.moveTo(self.cell)
            self.behind.orientation = self.orientation
        self.cell = target
    def move(self,orientation):
        shift = orientation
        self.cell.drawn = False
        if self.behind != None:
            self.behind.moveTo(self.cell)
            self.behind.orientation = self.orientation
        self.cell = self.cell.at(shift.x,shift.y)
        self.orientation = orientation
    def forward(self):
        return SegmentIterator(self, SegmentIterator.FORWARD)
    def backward(self):
        return SegmentIterator(self, SegmentIterator.BACKWARD)
    def update(self):
        self.image = pygame.transform.scale(self.get_image(),(Cell.SIZE,Cell.SIZE))
        self.rect = self.cell.get_rect()
#    def draw(self):
        #image = pygame.transform.scale(self.get_image(),(Cell.SIZE,Cell.SIZE))
#        self.cell.draw_image(self.image)
    def get_image(self):
        if self.isHead() :
            return self.snake.headImage(self)
        if self.isTail() :
            return self.snake.tailImage(self)
        else :
            return self.snake.bodyImage(self)
    def __str__(self):
        if self.isHead():
            return "Head("+str(self.cell.i)+","+str(self.cell.j)+")"
        elif self.isTail():
            return "Tail("+str(self.cell.i)+","+str(self.cell.j)+")"
        else:
            return "Body("+str(self.cell.i)+","+str(self.cell.j)+")"

class Snake(pygame.sprite.RenderPlain):
    available_moves = {K_UP:UP,K_DOWN:DOWN,K_LEFT:LEFT,K_RIGHT:RIGHT}
    def __init__(self, cell,spriteSheet,orientation=UP):
        super().__init__( )
        self.playArea = cell.map.area
        self.spriteSheet = spriteSheet
        self.head = SnakeSegment(cell,self, orientation)
        body = self.head.addSegmentBehind()
        self.tail = body.addSegmentBehind()
        self.growing =False
        self.alive = True
        self.nextMove = None 
        self.keysPressed = []
        self.tongue = None
        self.eyes = None
        self.speed = 6
        self.frameCounter = TimeTrigger(150)
    def isAt(self, pos):
        if self.head.cell == pos:
            return True
        return False
    def move(self):
        if self.growing:
            self.head = self.head.addSegmentAhead(self.nextMove)
            self.growing = False
        else :
            self.head.move(self.nextMove)
    def changeDirection(self, direction):
        if self.head.orientation == UP and direction == K_DOWN:
            return
        if self.head.orientation == DOWN and direction == K_UP:
            return
        if self.head.orientation == RIGHT and direction == K_LEFT:
            return
        if self.head.orientation == LEFT and direction == K_RIGHT:
            return       
        #logging.debug("Change direction to ",direction)
        self.nextMove = Snake.available_moves[direction]

    def draw(self):
        #for seg in self.tail.forward():
        #    seg.draw()
        super().draw(self.playArea.backgroundLayer)
        #self.tongue.draw()
        #self.eyes.draw()
    def grow(self):
        self.growing = True
    def __str__(self) :
        s = 'Snake: '
        for seg in self.head.backward():
            if seg.isTail():
                s += str(seg)
            else: 
                s += str(seg)+" - "
        return s
    def headImage(self,seg):
        #logging.debug("Head image",seg)
        if seg.orientation == UP:
            return self.spriteSheet.image(3,0)
        if seg.orientation == DOWN:
            return self.spriteSheet.image(4,1)
        if seg.orientation == RIGHT:
            return self.spriteSheet.image(4,0)
        if seg.orientation == LEFT:
            return self.spriteSheet.image(3,1)
    def tailImage(self,seg):
        #logging.debug("Tail image",seg)
        if seg.ahead.orientation == UP:
            return self.spriteSheet.image(3,2)
        if seg.ahead.orientation == DOWN:
            return self.spriteSheet.image(4,3)
        if seg.ahead.orientation == RIGHT:
            return self.spriteSheet.image(4,2)
        if seg.ahead.orientation == LEFT:
            return self.spriteSheet.image(3,3)

    def bodyImage(self,seg):
        if seg.ahead.orientation == UP :
            if seg.orientation == UP:
                return self.spriteSheet.image(2,1)
            if seg.orientation == RIGHT:
                return self.spriteSheet.image(2,2)
            else :
                return self.spriteSheet.image(0,1)
        if seg.ahead.orientation == DOWN :
            if seg.orientation == DOWN:
                return self.spriteSheet.image(2,1)
            if seg.orientation == RIGHT:
                return self.spriteSheet.image(2,0)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.orientation == RIGHT :
            if seg.orientation == RIGHT:
                return self.spriteSheet.image(1,0)
            if seg.orientation == DOWN:
                return self.spriteSheet.image(0,1)
            else :
                return self.spriteSheet.image(0,0)
        if seg.ahead.orientation == LEFT :
            if seg.orientation == LEFT:
                return self.spriteSheet.image(1,0)
            if seg.orientation == DOWN:
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
            self.tongue.update()
            self.eyes.update()
            if self.nextMove != None:
                if self.frameCounter.check():
                    logging.debug("Keys pressed:%s",self.keysPressed)
                    self.handleKeyPressed()
                    if self.checkNextMoveAllowed():
                        self.move()
                        apple = self.playArea.apple
                        if self.head.cell == apple.cell:
                            self.eatApple(apple)
                self.frameCounter.update()
            else:
                self.handleKeyPressed()
                if self.nextMove != None:
                    self.frameCounter.start()
            super().update()
    def handleKeyPressed(self):
        if len(self.keysPressed) > 0:
            keyPressed = self.keysPressed.pop()
            self.changeDirection(keyPressed)
    def checkNextMoveAllowed(self):
        if not self.headTouchWall():
            if self.headTouchBody():
                self.alive = False
        else:
            self.alive = False
        return self.alive
    def headTouchBody(self):
        cell = self.head.cell.at(self.nextMove.x, self.nextMove.y)
        for seg in self.head.behind.backward():
            if seg.cell == cell:
                return True
        return False
    def headTouchWall(self):
        return self.head.cell.at(self.nextMove.x, self.nextMove.y).blocking
    def eatApple(self, apple):
        apple.crunched = True
        if self.playArea.get_application().get_window("optionsWindow").sound :
            sound = pygame.mixer.Sound('./son/Crunched.wav')
        #pygame.mixer.music.load('./son/Crunched.wav')
            sound.play()
        logging.debug("Apple crunched!")
        self.grow()
    def add_tongue(self, spriteSheet):
        self.tongue = SnakeTongue(self,spriteSheet)
    def add_eyes(self, spriteSheet):
        self.eyes = SnakeEyes(self,spriteSheet)
class SnakeTongue(pygame.sprite.Sprite):
    TRIGGER_FRAME=10
    def __init__(self, snake, spriteSheet):
        pygame.sprite.Sprite.__init__(self)                
        self.spriteSheet = spriteSheet
        self.snake = snake
        self.out = False
        self.index = 0
        self.trigger = TimeTrigger(150)
    def update(self):
        if self.snake.alive :
            if not self.out:
                self.trigger.start()
                n = random.randint(0,500)
                if n == 0:
                    self.out = True
                    self.snake.add(self)         
                #if self.out:
                #    sound = pygame.mixer.Sound('./son/Hiss.wav')
                #    sound.play()
            else :
                if self.index > 20:
                    self.index = 0
                    self.trigger.reset()
                    self.out = False
                    self.snake.remove(self)    
                else:
                    if self.trigger.check():
                        self.index += 1                
                    self.trigger.update()
                    self._draw()
    def _draw(self):
        if self.out :
            shift = self.snake.nextMove
            if shift == None:
                shift = self.snake.head.orientation
            cell = self.snake.head.cell.at(shift.x,shift.y)
            self.image,shift = self.get_image()
            if self.image != None and cell != None and not cell.blocking:
                logging.debug("Head cell=%d %d", self.snake.head.cell.i, self.snake.head.cell.j)
                logging.debug("Tongue cell=%d %d", cell.i, cell.j)
                #cell.draw_image(image, shift)
                self.rect = Rect(cell.x+shift[0], cell.y+shift[1], self.image.get_width(), self.image.get_height())

    def get_image(self):
        shift = (-10,0)
        image = self.spriteSheet.image(0,self.index)
        if image == None:
            self.index = 0
            self.out = False
            self.snake.remove(self)         
        else:
            image = pygame.transform.scale(image, (48, Cell.SIZE))
            orientation = self.snake.nextMove
            if orientation == None:
                orientation = self.snake.head.orientation
            if orientation == UP:
                image = pygame.transform.rotate(image, 90)
                shift = (0,-10)
            elif orientation == DOWN :
                image = pygame.transform.rotate(image, 270)
                shift = (0,-10)
            elif orientation == LEFT :
                image = pygame.transform.rotate(image, 180)
            elif orientation == RIGHT :
                image = image
            logging.debug("Index=%d",self.index)
        return (image,shift)

class SnakeEye(pygame.sprite.Sprite):
    def __init__(self, snake, spriteSheet, right):
        pygame.sprite.Sprite.__init__(self)            
        self.spriteSheet = spriteSheet
        self.snake = snake
        self.right = right    
        self.index = 0    
        self.update()
    def update(self):
        if self.right:
            logging.debug("Update right eye with index %d", self.index)
        else:
            logging.debug("Update left eye with index %d", self.index)
        cell = self.snake.head.cell
        self.image = self.spriteSheet.image(0,self.index)
        if self.image == None or cell == None:
            self.index = 0
            self.snake.remove(self)         
        else:
            orientation = self.snake.nextMove
            if orientation == None:
                orientation = self.snake.head.orientation
            self.image = pygame.transform.scale(self.image, (14, 14))
            if orientation ==  UP:
                self.image = pygame.transform.rotate(self.image, 90)
                if self.right:
                    shift = (3,7)
                else:
                    shift = (14,7)
            if orientation == DOWN:
                self.image = pygame.transform.rotate(self.image, 270)
                if self.right:
                    shift = (3,11)
                else:
                    shift = (14,11)
            if orientation == LEFT:
                self.image = pygame.transform.rotate(self.image, 180)
                if self.right:
                    shift = (7,4)
                else:
                    shift = (7,14)
            if orientation == RIGHT:
                if self.right:
                    shift = (11,3)
                else:
                    shift = (11,14)
            logging.debug("Index=%d",self.index)
            self.rect=Rect(cell.x+shift[0],cell.y+shift[1], self.image.get_width(), self.image.get_height())
class SnakeEyes():
    TRIGGER_FRAME=10
    def __init__(self, snake, spriteSheet):
        self.spriteSheet = spriteSheet
        self.snake = snake
        self.blinking = False
        self.index = 0
        self.rightEye = SnakeEye(snake,spriteSheet,True)
        self.leftEye = SnakeEye(snake,spriteSheet,False)
        self.trigger = TimeTrigger(100)
    def update(self):
        logging.debug("Update blinking ")
        if self.snake.alive :
            if not self.blinking:
                n = random.randint(0,500)
                if n == 0:
                    self.trigger.start()
                    self.blinking = True
                    self.snake.add(self.rightEye)         
                    self.snake.add(self.leftEye)         
                    self.rightEye.index = 0
                    self.leftEye.index = 0
            else :
                if self.index > 8:
                    self.index = 0
                    self.trigger.reset()
                    self.snake.remove(self.rightEye)         
                    self.snake.remove(self.leftEye)    
                    self.blinking = False     
                else :
                    if self.trigger.check():
                        self.rightEye.index = self.index
                        self.leftEye.index = self.index
                        self.index += 1
                    self.trigger.update()
                #self._draw()

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
        self.label = Label("homeLabel", (270,70), (120,60),"Jouer à Snake", className='title')        
        self.add_component(self.label)
        classic = Button("classicBtn","Classique", self.playClassic, className='home')
        self.add_component(classic)
        special = Button("specialBtn","Spécial", self.playSpecial, className='home')
        self.add_component(special)
        options = Button("optionsBtn","Options", self.showOptions, className='home')
        self.add_component(options)
        quit = Button('quitBtn', "Quit", self.quit)
        self.add_component(quit)
        #self.style.background.image='Menu.png'
        logging.debug("id=%s", options.get_id())
    def playClassic(self):
        w = self.application.get_window("gameBoard")
        w.game.set_level('classic') 
        w.show()
    def playSpecial(self):
        w = self.application.get_window("gameBoard")
        w.game.set_level('labyrinth')
        w.show()
    def showOptions(self):
        self.application.show_window("optionsWindow")
    def quit(self):
        self.application.quit()

class ScoreView(Container):
    def __init__(self, position, dimension, score=None):
        super().__init__("scorePanel", position, dimension )
        self.score = score
        icon = ImageView("scoreIcon", None, (Cell.SIZE, Cell.SIZE),'apple.png')
        self.add_component(icon)
        #icon = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Pomme.png')), (Cell.SIZE, Cell.SIZE))
        #self.backgroundLayer.blit(icon, (0, 0))
        self.title = "%s"
        text = self.title % self.score.value
        self.label = Label("scoreLabel", (Cell.SIZE+1,0), (60, dimension[1]),text)
        self.add_component(self.label)
        
    def update(self):
        super().update()
        text = self.title % self.score.value
        self.label.set_text(text)
        self.label.update()
class GameOver(Window):
    def __init__(self, position, dimension):
        super().__init__("gameOverPanel",position,dimension)
        replay = Button("replayBtn","Rejouer", self.replay)
        self.add_component(replay)
        cancel = Button("cancelBtn","Annuler", self.cancel)
        self.add_component(cancel)
    def replay(self):
        w = self.application.get_window("gameBoard")
        w.remove_overlay()
        w.stop()
        w.preparePlay()
        self.hide()
    def cancel(self):
        w = self.application.get_window("gameBoard")
        w.remove_overlay()
        w.stop()
        self.hide()
        w.hide()

    def on_handle_eventsss(self, event):
        w = self.get_width()
        h = self.get_height()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.absoluteX()+w > event.pos[0] > self.absoluteX() and self.absoluteY()+h > event.pos[1]> self.absoluteY():
                self.container.stop()
class HighestScoreView(Container):
    def __init__(self, position, dimension, score=None):
        super().__init__("highestScorePanel", position, dimension)
        self.score = score
        icon = ImageView("highestScoreIcon", None, (Cell.SIZE, Cell.SIZE),'trophy.png')
        self.add_component(icon)

        text = str(self.score.value)
        self.label = Label("highestScoreLabel", (Cell.SIZE+1,0), (60,self.dimension.get_height()),text)
        self.add_component(self.label)
    def update(self):
        super().update()
    def set_highestscore(self, score):
        self.score = score
        text = str(self.score.value)
        self.label.set_text(text)
class PlayArea(Component):
    def __init__(self, position, game, map):
        super().__init__("snakePlayArea", position, (Cell.SIZE*map.width,Cell.SIZE*map.height))
        self.spriteSheet = SpriteSheet(self.style.background.image, 32, 32, 5, 4)
        map.spriteSheet = self.spriteSheet
        self.gridWidth  = map.width
        self.gridHeight = map.height
        self.snake = None
        self.apple = None
        self.map = map
        self.map.area = self
        logging.debug("taille=%d %d",self.gridWidth, self.gridHeight)

    def update(self):
        self.set_dirty(True)
        for line in self.map.cells:
            for cell in line:
                cell.draw()
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
        self.snake = Snake(cell, self.spriteSheet, LEFT)
        logging.debug('%s',self.snake)
        logging.debug('Snake head position: %d %d %d %d',self.snake.head.cell.x, self.snake.head.cell.y, self.snake.head.cell.absoluteX(), self.snake.head.cell.absoluteY())
        tongueSpriteSheet = SpriteSheet("tongue.png",48,24,1,21)
        self.snake.add_tongue(tongueSpriteSheet)
        blinkSpriteSheet = SpriteSheet("blink.png",28,28,1,9)
        self.snake.add_eyes(blinkSpriteSheet)
    def reset(self):
        self.apple = None
        self.snake = None

class GameBoard(Window):
    GAMEAREA_ORIGINX = 130
    GAMEAREA_ORIGINY = 70

    def __init__(self, levelMap, cellSize=32):
        super().__init__("gameBoard")
        Cell.SIZE=cellSize
        self.game = Game('classic')
        self.scoreView = ScoreView((140, 25), (200,40), Score(0,''))
        self.add_component(self.scoreView)
        self.highestScore = HighestScoreView((500, 25), (150,40), self.game.highestScores.get_highest_score())
        self.add_component(self.highestScore)
        self.playArea = None
    def preparePlay(self):
        self.playArea.reset()
        self.playFinished = False
        self.playArea.addSnake()  
        self.playArea.addApple()
        self.game.new_play()
        self.scoreView.score = self.game.score
        self.highestScore.set_highestscore(self.game.highestScores.get_highest_score())
        if self.application.get_window("optionsWindow").music :
            volume = pygame.mixer.music.get_volume() #Retourne la valeur du volume, entre 0 et 1
            pygame.mixer.music.set_volume(0.2) #Met le volume à 0.5 (moitié)
            pygame.mixer.music.load('./son/theme-music.wav')
            pygame.mixer.music.play(-1)

    def run(self):
        if self.playArea != None:
            self.remove_component(self.playArea)
        map = PlayMap(self.game.level)
        x = min([(Application.WINDOWWIDTH-(map.width*Cell.SIZE))/2,GameBoard.GAMEAREA_ORIGINX])
        y = min([(Application.WINDOWHEIGHT-(map.height*Cell.SIZE))/2,GameBoard.GAMEAREA_ORIGINY])
        logging.debug("W1= %d",Application.WINDOWWIDTH)
        logging.debug("POS= %d %d",x,y)

        self.playArea = PlayArea((int(x),int(y)),self.game, map)
        self.add_component(self.playArea)
        self.preparePlay()
        #self.get_application().remove_window(self.gameOver)
        #self.gameOver.visible = False
        #self.get_application().add_window(self.gameOver)
        
        super().run()
    def on_handle_event(self, events):
        super().on_handle_event(events)
        if not self.playFinished:
            if not self.playArea.snake.alive:
                self.game.highestScores.add_score(self.game.score)
                self.game.highestScores.save()
                self.add_overlay()
                gameOver = self.application.get_window("gameOverPanel")
                gameOver.show()
                self.playFinished = True
                pygame.mixer.music.fadeout(2000) #Fondu de 2s à la fin de la musique
            else:
                apple = self.playArea.apple
                if apple.crunched:
                    self.playArea.addApple()
                    self.game.score.value += 1
                    logging.debug("Score=%d",self.game.score.value)
    def stop(self):
        #pygame.mixer.music.fadeout(400) #Fondu à 400ms de la fin des musiques
        pygame.mixer.music.stop()
        self.hide()


class OptionsWindow(Window):
    def __init__(self):
        super().__init__("optionsWindow") #, position=(50,50), dimension=(500,600))
        self.title = Label("optionsLabel", (270,70), (120,60),"Options", className='title')        
        self.add_component(self.title)
        soundLabel = Label("musicLabel", (180, 190), (120,60),"Sons")        
        self.add_component(soundLabel)
        soundOn = Button("soundOnBtn", "ON", self.soundOn,(300,190), (80, 60))
        self.add_component(soundOn)
        soundOff = Button("soundOffBtn", "OFF", self.soundOff,(400,190), (80, 60))
        self.add_component(soundOff)
        musicLabel = Label("musicLabel", (180, 290), (120,60),"Musique")        
        self.add_component(musicLabel)
        musicOn = Button("musicOnBtn", "ON", self.musicOn,(300,290), (80, 60))
        self.add_component(musicOn)
        musicOff = Button("musicOffBtn", "OFF", self.musicOff,(400,290), (80, 60))
        self.add_component(musicOff)
        retour = Button("retourBtn", "Retour", self.cancel,position=(300,370), dimension=(150, 60))
        self.add_component(retour)
        self.music = True
        self.sound = True
        self.style.font.size=42
    def cancel(self):
        self.hide()
    def soundOn(self):
        self.sound = True
        logging.debug("Sound ON")
    def soundOff(self):
        logging.debug("Sound OFF")
        self.sound = False
    def musicOn(self):
        self.music = True
        logging.debug("Music ON")
    def musicOff(self):
        logging.debug("Music OFF")
        self.music = False
logging.basicConfig(filename='snake.log', filemode='w', level=logging.WARNING)
themeName = 'default'
if len(sys.argv) > 1:
    themeName = sys.argv[1]
theme = Theme.parseCss(themeName)
game = Application('Snake', 2000, theme)
game.add_window(HomeWindow(),True)
game.add_window(GameBoard("level1", 30))
game.add_window(OptionsWindow())
game.add_window(GameOver((190, 260), (318,250)))
game.run()

sys.exit()
