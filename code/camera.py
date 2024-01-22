import pygame, math, random
from settings import *

class Camera(pygame.sprite.Group):
    def __init__(self, game, scene):
        super().__init__()

        self.game = game
        self.scene = scene
        self.offset = pygame.math.Vector2()

    def offset_draw(self, target):
        self.game.screen.fill(LIGHT_GREY)

        self.offset = target - RES/2

        for layer in LAYERS.values():
            for sprite in self.scene.drawn_sprites:
                if sprite.z == layer: # and self.scene.visible_window.contains(sprite.rect):
                    offset = sprite.rect.topleft - self.offset
                    self.game.screen.blit(sprite.image, offset)