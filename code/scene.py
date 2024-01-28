import pygame
from state import State
from settings import *

from pytmx.util_pygame import load_pygame
from camera import Camera
from player import Player
from objects import Tile
from weapons import Weapon

class Scene(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.game = game
		self.current_scene = 'tutorial'
		self.entry_point = '0'
		self.exiting = False
		
		self.drawn_sprites = Camera(self.game, self)
		self.update_sprites = pygame.sprite.Group()
		self.block_sprites = pygame.sprite.Group()

		# create all objects in the scene using tmx data
		self.tmx_data = load_pygame(f'../scenes/{self.current_scene}//{self.current_scene}.tmx')

		self.create_scene_instances()

	def get_scene_size(self):
		with open(f'../scenes/{self.current_scene}/{self.current_scene}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		return (cols * TILESIZE, rows * TILESIZE)

	def create_scene_instances(self):

		layers = []
		for layer in self.tmx_data.layers:
			layers.append(layer.name)

		if 'blocks' in layers:
			for x, y, surf in self.tmx_data.get_layer_by_name('blocks').tiles():
				Tile([self.block_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['blocks'])

		if 'entries' in layers:
			for obj in self.tmx_data.get_layer_by_name('entries'):
				if obj.name == self.entry_point:
					self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'player', LAYERS['player'])

	def create_particle(self, particle_type, pos):
		if particle_type == 'landing':
			pass

		elif particle_type == 'blood':
			pass

	def create_melee(self, weapon_type, attack_type):
		self.player.weapon = Weapon(self.game, self, [self.update_sprites, self.drawn_sprites], f'../assets/weapons/{weapon_type}/{attack_type}', z= LAYERS['particles'])

	def update(self, dt):
		self.update_sprites.update(dt)

	def debug(self, debug_list):
		for index, name in enumerate(debug_list):
			self.game.render_text(name, WHITE, self.game.font, (10, 15 * index), True)

	def draw(self, screen):

		self.drawn_sprites.offset_draw(self.player.rect.center)
		self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
					str('vel: '+ str(round(self.player.vel, 2))),
					str('combo: '+ str(self.player.jump_counter)),
					str('state: '+ str(self.player.facing)),
					None,])

		
