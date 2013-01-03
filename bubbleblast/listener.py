#!/usr/bin/python
#-*- coding:utf-8 -*-

import pygame
import logging
import pickle
import os
from random import random
from pygame.rect import Rect

from event import EventManager
from event import TickEvent
from event import MapBuiltEvent
from event import ConfigTickEvent
from event import MouseClickRequest
from event import MouseClickHoldRequest
from event import QuitEvent
from event import PauseEvent
from event import GameStartedEvent
from event import GameResetEvent
from event import SpriteResetEvent
from event import GameOverEvent
from event import NextLevelRequest
from event import HighscoreEvent
from event import CharactorPlaceRequest
from event import CharactorPlacedEvent
from event import CharactorImplodeEvent
from event import CharactorRemovedEvent
from event import CharactorRemoveRequest
from event import CharactorShrinkEvent
from event import CharactorSpriteRemoveRequest

from sprite import Box
from sprite import Bubble
from sprite import TextSprite
from sprite import HUDSprite

class Listener(object):
    """
    Listener superclass
    """

    def __init__(self, evManager):
        self.name = "Generic listener"
        self.evManager = evManager

    def Notify(self, event):
        """Called from evManager. Notifies the listener of an event"""
        print "woot"
        pass

class HIDController(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "HID Controller"
        self.evManager = evManager
        evManager.Subscribe(self)

    def Notify(self, event):
        if isinstance(event, TickEvent):
            # handle simple keypresses and clicks
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_n:
                    self.evManager.Post(GameResetEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    self.evManager.Post(PauseEvent())
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self.evManager.Post(MouseClickRequest(ev))
            # handle mouse hold events
            #if pygame.mouse.get_pressed()[0]:
            #    self.evManager.Post(MouseClickHoldRequest(0, pygame.mouse.get_pos()))

class Map(Listener):
    """
    One open Map/Board (no sectors)
    """
    def __init__(self, evManager):
        self.name = "Map"
        self.evManager = evManager
        evManager.Subscribe(self)
        self.size = None

    def Build(self):
        # There is currently no map to build, but this will likely change in
        # the future.
        self.size = (640, 480)
        #self.size = (1366, 768)
        ev = MapBuiltEvent(self)
        self.evManager.Post(ev)

    def Notify(self, event):
        pass

    def get_available_position(self, radius):
        """returns coordinates for a position on the map that is currently not
        in use."""
        # check map for available coordinates
        xCoord = int(self.size[0]*random()) # TODO: temp workaround
        yCoord = int(self.size[1]*random()) # TODO: temp workaround
        return (xCoord, yCoord)
    

class Player(Listener):
    """
    """
    def __init__(self, evManager):
        self.name = "Player"
        self.evManager = evManager
        evManager.Subscribe(self)
        self.score = 0

    def Notify(self, event):
        pass

class Charactor(Listener):
    """
    """
    def __init__(self, evManager):
        self.name = "Bubble Charactor"
        self.evManager = evManager
        self.coordinates = (0,0)
        self.speed = 2
        self.radius = 100
        self.sprite = None
        #evManager.Subscribe(self)

    def __init__(self, evManager, coordinates=(0,0), speed=2, radius=100):
        self.speed=speed
        self.radius=radius
        self.coordinates=coordinates
        self.sprite=None

    def Notify(self, event):
        if isinstance(event, CharactorPlaceRequest):
            self.Place(event)

class Game(Listener):
    """
    """
    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2
    STATE_GAMEOVER = 3

    FILE_HIGHSCORE = "~/.bubbleblast/highscore"

    def __init__(self, evManager):
        self.name = "Game Controller"
        self.evManager = evManager
        self.state = Game.STATE_PREPARING
        evManager.Subscribe(self)
        logging.debug("Initialized game to preparing state")

        self.map = Map(evManager)
        self.player = Player(evManager)
        self.charactors = []

        # initial values
        self.gotHighscore = False
        self.highscore = None
        self.level = None
        self.lives = None
        self.bubbles = None
        self.interval = None
        self.initialbubbles = 5
        self.initiallives = 5
        self.initialinterval = 300
        self.initiallevel = 1

    def Start(self):

        # should define the position here me thinks. however, I need the
        # center position for the game window (or provide random
        # coordinates within the limits of the game window)
        # (this gets more important when adding different levels)

        self.map.Build()
        self.player.score = 0
        self.gotHighscore = False
        self.highscore = self.ReadHighscore()
        self.lives = self.initiallives
        self.level = self.initiallevel
        self.bubbles = self.initialbubbles
        self.interval = self.initialinterval

        self.state = Game.STATE_RUNNING

        ev = GameStartedEvent(self)
        self.evManager.Post(ev)

    def Stop(self):
        self.state = Game.STATE_GAMEOVER
        self.SaveHighscore()
        self.evManager.Post(GameOverEvent(self))

    def Reset(self):
        self.state = Game.STATE_PREPARING
        self.charactors = []
        self.evManager.Post(SpriteResetEvent())
        self.Start()

    def AddCharactor(self):
        size = int(random()*100+50)
        pos = self.map.get_available_position(size)
        speed = int(random()*10)+5
        ch = Charactor(self.evManager, pos, speed, size)
        self.charactors.append(ch)

        ev = CharactorPlacedEvent(ch)
        self.evManager.Post(ev)

    def RemoveCharactor(self, charactor):
        tmpList = [ x for x in self.charactors if id(charactor) != id(x) ]
        self.charactors = tmpList
        self.evManager.Post(CharactorRemovedEvent())

        size = int(random()*100)+50
        pos = self.map.get_available_position(size)
        speed = int(random()*10)+4

    def ReadHighscore(self):
        try:
            with open(os.path.expanduser(Game.FILE_HIGHSCORE), "r") as f:
                logging.info("Reading high score from file")
                highscore = pickle.load(f)
                return highscore
        except pickle.PickleError, e:
            logging.error("Unable to read high score from file. Error: %s" % e)
        except IOError, e:
            logging.error("Unable to open high score file for reading. Error: %s" % e)
        except EOFError, e:
            logging.error("Unknown parsing error. Error: %s" % e)
        return 0

    def SaveHighscore(self, force=False):
        if (self.player.score < self.highscore):
            return
        elif force==True:
            pass
        try:
            with open(os.path.expanduser(Game.FILE_HIGHSCORE), "w") as f:
                #if os.path.exists(os.path.dirname(os.path.expanduser(Game.FILE_HIGHSCORE))):
                #    if os.path.exists(os.path.expanduser(Game.FILE_HIGHSCORE)):
                logging.info("Saving highscore value of %d" % self.player.score)
                pickle.dump(self.player.score, f)
        except pickle.PickleError, e:
            logging.error("Unable to save high score to file. Error: %s" % e)
        except IOError, e:
            logging.error("Unable to open high score file for writing. Error: %s" % e)

    def Notify(self, event):
        if isinstance(event, TickEvent):
            ### GAME IS PREPARING
            if self.state == Game.STATE_PREPARING:
                self.Start()
            ### GAME IS RUNNING
            elif self.state == Game.STATE_RUNNING:
                # handle existing charactors
                for c in self.charactors:
                    if c.radius == 0:
                        self.evManager.Post(CharactorImplodeEvent(c))
                    if ((event.tick % c.speed) == 0):
                        c.radius -= 1
                        c.sprite.Shrink(c.radius)
                # check if is time to add new charactor to game board
                if (event.tick % self.interval == 0) and self.bubbles > 0:
                    self.AddCharactor()
                    self.bubbles -= 1
                elif (self.bubbles == 0):
                    self.evManager.Post(NextLevelRequest())
                elif (self.player.score > self.highscore):
                    self.highscore = self.player.score
                    if (self.gotHighscore == False):
                        self.gotHighscore = True
                        self.evManager.Post(HighscoreEvent())

        elif isinstance(event, NextLevelRequest):
            self.level += 1
            self.bubbles = self.initialbubbles + (3 * self.level)
            if (self.interval >= 200):
                self.interval -= 20
            elif (self.interval < 200 and self.interval >= 100):
                self.interval -= 10
            elif (self.interval < 100 and self.interval >= 10):
                self.interval -= 5
            if (self.level % 3 == 0):
                self.lives += 1

        elif isinstance(event, CharactorImplodeEvent):
            # here we count the amount of implodes (this is a BAD thing. we
            # want the bubbles to be blasted!)
            self.lives -= 1
            self.RemoveCharactor(event.charactor)
            self.evManager.Post(CharactorSpriteRemoveRequest(event.charactor))
            if self.lives == 0:
                self.Stop()
        elif isinstance(event, PauseEvent):
            if self.state == Game.STATE_RUNNING:
                self.state = Game.STATE_PAUSED
            else:
                self.state = Game.STATE_RUNNING
        elif isinstance(event, MouseClickRequest):
            if self.state == Game.STATE_RUNNING:
                pos = event.event.pos
                ptrRect = Rect(pos, (5,5))
                for c in self.charactors:
                    if ptrRect.colliderect(c.sprite.rect): # bubble burst
                        self.player.score += (10+(self.level-1)*5)
                        self.RemoveCharactor(c)
                        self.evManager.Post(CharactorSpriteRemoveRequest(c))
                        break
        elif isinstance(event, GameResetEvent):
            self.Reset()

class PygameView(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "Pygame View"
        self.evManager = evManager
        self.game = None
        evManager.Subscribe(self)

        pygame.init()

        self.screen = pygame.display.set_mode((640, 480))
        #self.screen = pygame.display.set_mode((1366, 768))
        pygame.display.set_caption("Bubble Blast")

        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill((0,0,0))
        self.background = background

        self.backSprites = pygame.sprite.RenderUpdates()
        self.frontSprites = pygame.sprite.RenderUpdates()
        self.HUDSprites = pygame.sprite.RenderUpdates()

    def ShowMap(self, map):
        # TODO: Should be able to adjust the screen resolution (i.e. window
        # size) here during run-time.
        pass

    def ShowCharactor(self, charactor):
        #charactorSprite = Box((50,50), (255,0,0),charactor.coordinates, self.frontSprites)
        charactorSprite = Bubble(charactor.radius, self.frontSprites, charactor.coordinates)
        charactor.sprite = charactorSprite
        #charactorSprite.rect.center = self.background.get_rect().center

    def ShowGameOver(self, game):
        posx = self.background.get_width()/2
        posy = self.background.get_height()/2
        TextSprite((posx,posy),self.frontSprites, size=60, text="GAME OVER")
        if game.gotHighscore:
            TextSprite((posx,posy+60),self.frontSprites, size=20, text="New highscore of %d achieved! Congratulations!" % game.player.score)
        else:
            TextSprite((posx,posy+60),self.frontSprites, size=20, text="Score: %d" % game.player.score)

    def Clear(self):
        self.frontSprites.empty()

    def Notify(self, event):
        if isinstance(event, TickEvent):
            # Draw everything
            self.screen.blit(self.background, (0,0))
            self.backSprites.clear( self.screen, self.background )
            self.frontSprites.clear( self.screen, self.background )
            self.HUDSprites.clear( self.screen, self.background )

            self.backSprites.update()
            self.frontSprites.update()
            self.HUDSprites.update()

            dirtyRects1 = self.backSprites.draw(self.screen)
            dirtyRects2 = self.frontSprites.draw(self.screen)
            dirtyRects3 = self.HUDSprites.draw(self.screen)
            dirtyRects = dirtyRects1+dirtyRects2+dirtyRects3

            pygame.display.update(dirtyRects)

        elif isinstance(event, CharactorPlacedEvent):
            # add charactor to game board
            self.ShowCharactor(event.charactor)
        elif isinstance(event, CharactorSpriteRemoveRequest):
            self.frontSprites.remove(event.charactor.sprite)
        elif isinstance(event, MapBuiltEvent):
            self.ShowMap(event.map)
        elif isinstance(event, GameStartedEvent):
            self.game = event.game
            posx = self.background.get_width()/2
            posy = self.background.get_height()/2
            hs = HUDSprite((posx,posy),event.game, self.HUDSprites)
            hs.rect.topleft = self.screen.get_rect().topleft
        elif isinstance(event, GameOverEvent):
            self.Clear()
            self.ShowGameOver(event.game)
        elif isinstance(event, SpriteResetEvent):
            self.Clear()

class CPUSpinnerController(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "CPU Spinner Controller"
        self.evManager = evManager
        evManager.Subscribe(self)
        self.isRunning = True
        self.clocktick = 240
        self.clock = pygame.time.Clock()
        self.currentTick = 0

    def Run(self):
        while self.isRunning:
            self.clock.tick(self.clocktick)
            ev = TickEvent(self.currentTick)
            self.evManager.Post(ev)
            self.currentTick += 1

    def Notify(self, event):
        if isinstance(event, QuitEvent):
            self.isRunning = False
        elif isinstance(event, ConfigTickEvent):
            self.clocktick = event.tick
