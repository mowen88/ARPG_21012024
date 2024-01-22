import pygame
from settings import *

class Collider(pygame.sprite.Sprite):
	def __init__(self, groups, pos, size, name=None):
		super().__init__(groups)
		self.image = pygame.Surface((size))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(2,0)
		self.name = name

class Tile(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE)), z= LAYERS['blocks']):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z