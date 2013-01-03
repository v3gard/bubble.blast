#!/usr/bin/python
#-*- coding:utf-8 -*-

import pygame

class Box(pygame.sprite.Sprite):
    def __init__(self, size, color, initial_position, group):
        # All sprite classes should extend pygame.sprite.Sprite. This gives you
        # several important internal methods that you probably don't need or
        # want to write yourself. Even if you do rewrite the internal methods,
        # you should extend Sprite, so things like
        # isinstance(obj, pygame.sprite.Sprite) return true on it.
        pygame.sprite.Sprite.__init__(self, group)

        # Create the image that will be displayed and fill it with the right color.
        self.image = pygame.Surface(size)
        self.image.fill(color)

        # Make our top-left corner the passes-in location
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position


class Bubble(pygame.sprite.Sprite):
    def __init__(self, radius, group, initial_position=(0,0), color=(255,0,0)):
        pygame.sprite.Sprite.__init__(self, group)
        self.color = color
        self.pos = initial_position
        charactorSurf = pygame.Surface((radius*2, radius*2))
        pygame.draw.circle(charactorSurf, color, (radius,radius), radius)
        self.image = charactorSurf
        self.rect = charactorSurf.get_rect()
        self.rect.center = self.pos
        self.image = self.image.convert_alpha()

    def Shrink(self, radius):
        if radius>0:
            charactorSurf = pygame.Surface((radius*2, radius*2))
            pygame.draw.circle(charactorSurf, self.color, (radius,radius), radius)
            self.image = charactorSurf
            self.rect = charactorSurf.get_rect()
            self.rect.center = self.pos
            self.image = self.image.convert_alpha()

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, pos, group, text="Undefined", size=36):
        self.text = text
        self.color = (255, 255, 255)
        pygame.sprite.Sprite.__init__(self, group)
        self.font = pygame.font.SysFont("Liberation Sans", size)
        textRender = self.font.render(self.text, 1, self.color)
        self.image = textRender
        self.rect = textRender.get_rect(centerx=pos[0],centery=pos[1])

class HUDSprite(pygame.sprite.Sprite):
    def __init__(self, pos, game, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.color = (255,255,255)
        self.pos = pos
        self.game = game
        self.font = pygame.font.SysFont("Liberation Mono", 12)
        self.text = None
        textRender = self.font.render(self.text, 1, self.color)
        self.image = textRender
        self.rect = textRender.get_rect(centerx=pos[0], centery=pos[1])

    def update(self):
        self.text = "Level: %02d   ||   Highscore: %05d   ||   Score: %06d   ||   Lives: %1d" % (self.game.level, self.game.highscore, self.game.player.score, self.game.lives)
        textRender = self.font.render(self.text, 1, self.color)
        self.image = textRender
