#!/usr/bin/python
#-*- coding:utf-8 -*-

import logging

class EventManager(object):
    """
    """
    def __init__(self):
        # må ha en weakref dict (men forsøker med vanlig list for å finne ut hvorfor)
        self.listeners = []
        logging.debug("EventManager initialized")

    def Subscribe(self, listener):
        """Subscribes to events from the event manager"""
        # add to weakref
        logging.debug("Adding subscriber: "+listener.name)
        self.listeners.append(listener)

    def Unsubscribe(self, listener):
        """Unsubscribes from events"""
        if listener in self.listeners:
            del self.listeners[listener]

    def Post(self, event):
        """Posts (ie broadcasts) an event to the subscribers"""
        if not isinstance(event, TickEvent):
            logging.debug("Firing event: %s" % event.name)
        for listener in self.listeners:
            listener.Notify(event)

#-----------------------------------------------------------------------------
class Event(object):
    """
    Event superclass
    """
    def __init__(self):
        self.name = "Generic Event"
        
class PauseEvent(Event):
    """
    Pause Event. Used for pausing the game.
    """
    def __init__(self):
        self.name = "Pause Event"

class ConfigTickEvent(Event):
    """
    Config Tick Event. Used for setting pygame clock tick (e.g. 60 fps)
    """
    def __init__(self, tick):
        self.name = "Config Tick Event"
        self.tick = tick

class QuitEvent(Event):
    """
    Quit Event
    """
    def __init__(self):
        self.name = "Quit Event"

class TickEvent(Event):
    """
    CPU Tick Event
    """
    def __init__(self, tick=0):
        self.name = "CPU Tick Event"
        self.tick = tick

class GameStartedEvent(Event):
    """
    Game Started Event
    """
    def __init__(self, game):
        self.name = "Game Started Event"
        self.game = game

class GameResetEvent(Event):
    """
    Game Reset Event
    """
    def __init__(self):
        self.name = "Game Reset Event"

class SpriteResetEvent(Event):
    """
    Sprite Reset Event
    """
    def __init__(self):
        self.name = "Sprite Reset Event"

class NextLevelRequest(Event):
    """
    Next Level Request
    """
    def __init__(self):
        self.name = "Next Level Request"

class GameOverEvent(Event):
    """
    Game Over Event
    """
    def __init__(self, game):
        self.name = "Game Over Event"
        self.game = game

class CharactorPlaceRequest(Event):
    """
    Charactor Place Request
    """
    def __init__(self, coordinates, speed=2, radius=50):
        self.name = "Charactor Place Request"
        self.coordinates = coordinates
        self.speed = speed
        self.radius = radius

class CharactorImplodeEvent(Event):
    """
    Charactor Implode Event
    """
    def __init__(self, charactor):
        self.name = "Charactor Implode Event"
        self.charactor = charactor

class CharactorShrinkEvent(Event):
    """
    Charactor Shrink Event
    """
    def __init__(self, charactor):
        self.name = "Charactor Shrink Event"
        self.charactor = charactor


class CharactorRemoveRequest(Event):
    """
    Charactor Remove Request
    """
    def __init__(self, charactor):
        self.name = "Charactor Remove Request"
        self.charactor = charactor

class CharactorSpriteRemoveRequest(Event):
    """
    Charactor Sprite Remove Request
    """
    def __init__(self, charactor):
        self.name = "Charactor Sprite Remove Request"
        self.charactor = charactor


class CharactorRemovedEvent(Event):
    """
    Charactor Removed Event
    """
    def __init__(self):
        self.name = "Charactor Removed Event"


class CharactorPlacedEvent(Event):
    """
    Charactor Placed Event
    """
    def __init__(self, charactor):
        self.name = "Charactor Placed Event"
        self.charactor = charactor


class MapBuiltEvent(Event):
    """
    Map Built Event
    """
    def __init__(self, map):
        self.name = "Map Built Event"
        self.map = map

class MouseClickRequest(Event):
    """
    Mouse Click Request 
    """
    def __init__(self, event):
        self.name = "Mouse Click Request"
        self.event = event

class MouseClickHoldRequest(Event):
    """
    Mouse Click and Hold Request 
    """
    def __init__(self, button, position):
        self.name = "Mouse Click and Hold Request (x:%d, y:%d)" % position
        self.button = button
        self.position = position
