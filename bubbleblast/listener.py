#!/usr/bin/python
#-*- coding:utf-8 -*-

import pygame

from event import EventManager
from event import TickEvent
from event import ConfigTickEvent
from event import MouseClickEvent
from event import QuitEvent

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
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
                    self.evManager.Post(QuitEvent())
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self.evManager.Post(MouseClickEvent(ev))

class Game(Listener):
    """
    """

    def __init__(self, evManager):
        self.name = "Game Controller"
        self.evManager = evManager
        evManager.Subscribe(self)

    def Notify(self, event):
        pass

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

    def Notify(self, event):
        if isinstance(event, TickEvent):
            # Draw everything
            self.screen.blit(self.background, (0,0))
            pygame.display.flip()


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

    def Run(self):
        while self.isRunning:
            self.clock.tick(self.clocktick)
            ev = TickEvent()
            self.evManager.Post(ev)

    def Notify(self, event):
        if isinstance(event, QuitEvent):
            self.isRunning = False
        elif isinstance(event, ConfigTickEvent):
            self.clocktick = event.tick