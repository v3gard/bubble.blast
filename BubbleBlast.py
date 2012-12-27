#!/usr/bin/python
#-*- coding: utf-8 -*-

import logging.config

import bubbleblast
from bubbleblast.event import EventManager
from bubbleblast.listener import HIDController
from bubbleblast.listener import CPUSpinnerController
from bubbleblast.listener import Game
from bubbleblast.listener import PygameView


def main():
    logging.config.fileConfig('logging.conf')
    logging.info('Initializing game.')

    evManager = EventManager()

    hid = HIDController(evManager)
    spinner = CPUSpinnerController(evManager)
    pygameView = PygameView(evManager)
    game = Game(evManager)

    try:
        spinner.Run() # main game loop. runs until terminated.
    except (KeyboardInterrupt, SystemExit):
        print("Terminated")
        logging.info("Application forcefully terminated by user")
        return
    logging.info("Application terminated gracefully.")


if __name__=="__main__":
    main()
