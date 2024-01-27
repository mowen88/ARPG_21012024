import pygame
from settings import *

class Weapon(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, path, z= LAYERS['blocks']):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.scene.player.rect.center)

		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z

	def animate(self, animation_speed):

		self.frame_index += animation_speed
		self.frame_index = self.frame_index % len(self.frames)	
		self.image = self.frames[int(self.frame_index)]
		if self.frame_index > len(self.frames)-1:	
			self.kill()

		direction = self.scene.player.facing if self.scene.player.facing == 1 else 0
		self.image = pygame.transform.flip(self.frames[int(self.frame_index)], direction-1, False)

	def update(self, dt):
		self.animate(0.25 * dt)
		self.rect.center = self.scene.player.rect.center

