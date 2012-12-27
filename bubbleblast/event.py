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
    def __init__(self):
        self.name = "CPU Tick Event"

class MouseClickEvent(Event):
    """
    Mouse Click Event
    """
    def __init__(self, event):
        self.name = "Mouse Click Event"
        self.event = event
