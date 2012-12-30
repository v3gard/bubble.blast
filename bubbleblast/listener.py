#!/usr/bin/python
#-*- coding:utf-8 -*-

import pygame
import logging

from event import EventManager
from event import TickEvent
from event import MapBuiltEvent
from event import ConfigTickEvent
from event import MouseClickRequest
from event import MouseClickHoldRequest
from event import QuitEvent
from event import GameStartedEvent
from event import CharactorPlaceRequest
from event import CharactorPlacedEvent
from event import CharactorImplodeEvent
from event import CharactorRemovedEvent
from event import CharactorRemoveRequest
from event import CharactorShrinkEvent
from event import CharactorSpriteRemoveRequest

from sprite import Box
from sprite import Bubble

class Listener(object):
    """
    Listener superclass
    """

    def __init__(self, evManager):
        self.name = "Generic listener"
        self.evManager = evManager

    def Notify(self, event):
        """Called from evManager. Notifies the listener of an event"""
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
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self.evManager.Post(MouseClickRequest(ev))
            # handle mouse hold events
            if pygame.mouse.get_pressed()[0]:
                self.evManager.Post(MouseClickHoldRequest(0, pygame.mouse.get_pos()))

class Map(Listener):
    """
    One open Map/Board (no sectors)
    """
    def __init__(self, evManager):
        self.name = "Map"
        self.evManager = evManager
        evManager.Subscribe(self)

    def Build(self):
        # There is currently no map to build, but this will likely change in
        # the future.
        ev = MapBuiltEvent(self)
        self.evManager.Post(ev)

    def Notify(self, event):
        pass

class Player(Listener):
    """
    """
    def __init__(self, evManager):
        self.name = "Player"
        self.evManager = evManager
        evManager.Subscribe(self)

        self.charactors = [ Charactor(evManager) ]

    def Notify(self, event):
        pass

class Charactor(Listener):
    """
    """
    def __init__(self, evManager):
        self.name = "Charactor"
        self.evManager = evManager
        self.speed = 2
        self.radius = 100
        self.sprite = None
        evManager.Subscribe(self)

    def Notify(self, event):
        if isinstance(event, CharactorPlaceRequest):
            self.Place(event)

class Game(Listener):
    """
    """
    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    def __init__(self, evManager):
        self.name = "Game Controller"
        self.evManager = evManager
        self.state = Game.STATE_PREPARING
        evManager.Subscribe(self)
        logging.debug("Initialized game to preparing state")

        self.map = Map(evManager)
        self.players = [Player(evManager)]
        self.charactors = []

    def Start(self):
        self.map.Build()
        self.state = Game.STATE_RUNNING
        ev = GameStartedEvent()
        self.evManager.Post(ev)

    def Notify(self, event):
        if isinstance(event, TickEvent):
            if self.state == Game.STATE_PREPARING:
                self.Start()
            elif self.state == Game.STATE_RUNNING:
                for c in self.charactors:
                    if c.radius == 0:
                        self.evManager.Post(CharactorImplodeEvent(c))
                    if ((event.tick % c.speed) == 0):
                        c.radius -= 1
                        c.sprite.Shrink(c.radius)
        elif isinstance(event, GameStartedEvent):
            # should define the position here me thinks. however, I need the
            # center position for the game window (or provide random
            # coordinates within the limits of the game window)
            # (this gets more important when adding different levels)
            #self.evManager.Post(CharactorPlaceRequest((200,100), 2, 40))
            #self.evManager.Post(CharactorPlaceRequest((350,350), 5, 100))
            c1 = Charactor(self.evManager)
            c2 = Charactor(self.evManager)
            c3 = Charactor(self.evManager)
            c1.coordinates = (350,350)
            c1.speed = 3
            c1.radius = 100
            c2.coordinates = (200,100)
            c2.speed = 6
            c2.radius = 40
            c3.coordinates = (500,50)
            c3.speed = 4
            c3.radius = 40
            self.charactors.append(c1)
            self.charactors.append(c2)
            self.charactors.append(c3)
            
            for c in self.charactors:
                ev = CharactorPlacedEvent(c)
                self.evManager.Post(ev)


        elif isinstance(event, CharactorPlacedEvent):
            #self.charactors.append(event.charactor)
            pass
        elif isinstance(event, CharactorImplodeEvent):
            # here we count the amount of implodes (this is a BAD thing. we
            # want the bubbles to be blasted!)
            self.evManager.Post(CharactorSpriteRemoveRequest(event.charactor))
        elif isinstance(event, CharactorRemoveRequest):
            tmpList = [ x for x in self.charactors if id(event.charactor) != id(x) ]
            self.charactors = tmpList
            self.evManager.Post(CharactorRemovedEvent())




class PygameView(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "Pygame View"
        self.evManager = evManager
        evManager.Subscribe(self)

        pygame.init()

        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Bubble Blast")

        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill((0,0,0))
        self.background = background

        self.backSprites = pygame.sprite.RenderUpdates()
        self.frontSprites = pygame.sprite.RenderUpdates()

    def ShowMap(self, map):
        pass

    def ShowCharactor(self, charactor):
        #charactorSprite = Box((50,50), (255,0,0),charactor.coordinates, self.frontSprites)
        charactorSprite = Bubble(charactor.radius, self.frontSprites, charactor.coordinates)
        charactor.sprite = charactorSprite
        #charactorSprite.rect.center = self.background.get_rect().center

    def Notify(self, event):
        if isinstance(event, TickEvent):
            # Draw everything
            self.screen.blit(self.background, (0,0))
            self.backSprites.clear( self.screen, self.background )
            self.frontSprites.clear( self.screen, self.background )

            self.backSprites.update()
            self.frontSprites.update()

            dirtyRects1 = self.backSprites.draw(self.screen)
            dirtyRects2 = self.frontSprites.draw(self.screen)
            dirtyRects = dirtyRects1+dirtyRects2

            pygame.display.update(dirtyRects)

        elif isinstance(event, CharactorPlacedEvent):
            # add charactor to game board
            self.ShowCharactor(event.charactor)
        elif isinstance(event, CharactorSpriteRemoveRequest):
            self.frontSprites.remove(event.charactor.sprite)
            self.evManager.Post(CharactorRemoveRequest(event.charactor))

class CPUSpinnerController(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "CPU Spinner Controller"
        self.evManager = evManager
        evManager.Subscribe(self)
        self.isRunning = True
        self.clocktick = 60
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
