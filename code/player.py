import pygame, math, random
from settings import *
from player_fsm import Fall


class Player(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, name, z):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.name = name
		self.z = z
		
		self.animations = {'idle':[], 'run':[], 'jump':[], 'fall':[], 'land':[], 'attack_0':[], 'attack_1':[], 'attack_2':[]}
		self.import_images()

		self.frame_index = 0
		self.image = self.animations['fall'][self.frame_index].convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)
		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()

		self.gravity = 0.2
		self.acc_rate = 0.4
		self.fric = -0.2
		self.acc = pygame.math.Vector2(0, self.gravity)	
		self.vel = pygame.math.Vector2()
		self.max_fall_speed = 6
		self.jump_height = 5
		self.facing = 1

		self.on_ladder = False
		self.platform = None
		self.relative_position = pygame.math.Vector2()
		self.on_ground = False
		self.drop_through = False

		self.combo_counter = 0
		self.can_attack = True
		self.can_dash = True

		self.jump_counter = 0
		self.cyote_timer = 0
		self.cyote_timer_threshold = 6
		self.jump_buffer_active = False
		self.jump_buffer = 0
		self.jump_buffer_threshold = 6

		self.alive = True
		self.state = Fall(self)

		self.weapon = None

	def import_images(self):
		for animation in self.animations.keys():
			full_path = f'../assets/characters/{self.name}/' + animation
			self.animations[animation] = self.game.get_folder_images(full_path)

	def animate(self, state, speed, loop=True):

		self.frame_index += speed

		if self.frame_index >= len(self.animations[state]):
			if loop: 
				self.frame_index = 0
			else:
				self.frame_index = len(self.animations[state]) -1
		
		direction = self.facing if self.facing == 1 else 0
		self.image = pygame.transform.flip(self.animations[state][int(self.frame_index)], direction-1, False)

	def jump(self, height):
		self.vel.y = -height

	def get_on_ground(self):
		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox = self.rect.inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)

	def input(self):
		keys = pygame.key.get_pressed()
		
		if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
			self.acc.x = -self.acc_rate
			self.facing = -1
			
		elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not (keys[pygame.K_LEFT] or keys[pygame.K_a]):
			self.acc.x = self.acc_rate
			self.facing = 1


	def exit_scene(self):
		for exit in self.scene.exit_sprites:
			if self.hitbox.colliderect(exit.hitbox) and ACTIONS['up']:
				self.game.write_game_time()
				self.scene.exiting = True
				self.scene.new_scene = SCENE_DATA[self.scene.current_scene][exit.name.split("_")[0]]
				self.scene.prev_level = SCENE_DATA[self.scene.current_scene]['level']
				self.scene.entry_point = exit.name.split("_")[0]

	def collide_tutorials(self):
		for rect in self.scene.tutorial_sprites:
			if self.hitbox.colliderect(rect.rect):# and rect not in SAVE_DATA['killed_sprites']:
				Dialogue(self.game, rect.text, WHITE, (HALF_WIDTH, HALF_HEIGHT + TILESIZE *2), True).enter_state()
				#self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], rect.text, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5), 200, NEON_GREEN)
				#SAVE_DATA['killed_sprites'].append(rect.text)
				rect.kill()
	
	def get_collidable_sprites(self):
		collidable_list = pygame.sprite.spritecollide(self, self.scene.block_sprites, False)
		return collidable_list

	def collisions_x(self):
		for sprite in self.get_collidable_sprites():
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.right >= sprite.hitbox.left and self.old_hitbox.right <= sprite.old_hitbox.left:
					self.hitbox.right = sprite.hitbox.left
					self.vel.x = 0
				elif self.hitbox.left <= sprite.hitbox.right and self.old_hitbox.left >= sprite.old_hitbox.right:
					self.hitbox.left = sprite.hitbox.right
					self.vel.x = 0

				self.rect.centerx = self.hitbox.centerx
				self.pos.x = self.hitbox.centerx

	def collisions_y(self):
		for sprite in self.get_collidable_sprites():
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.bottom >= sprite.hitbox.top and self.old_hitbox.bottom <= sprite.old_hitbox.top:
					self.hitbox.bottom = sprite.hitbox.top
					self.on_ground = True
					self.vel.y = 0

				elif self.hitbox.top <= sprite.hitbox.bottom and self.old_hitbox.top >= sprite.old_hitbox.bottom:
					self.hitbox.top = sprite.hitbox.bottom
					self.vel.y = 0

				self.rect.centery = self.hitbox.centery
				self.pos.y = self.hitbox.centery
				self.platform = None

	def physics_x(self, dt):
			
		self.acc.x += self.vel.x * self.fric
		self.vel.x += self.acc.x * dt

		if self.platform: 
			if self.hitbox.right < self.platform.hitbox.left or self.hitbox.left > self.platform.hitbox.right:
				self.platform = None
			elif self.platform.vel.x != 0:
				self.pos.x = round(self.platform.pos.x) +round(self.relative_position.x)

		self.pos.x += self.vel.x * dt + (0.5 * self.acc.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collisions_x()


	def physics_y(self, dt):

		self.vel.y += self.acc.y * dt

		if self.platform:
			self.pos.y = round(self.platform.pos.y) +round(self.relative_position.y)

		self.pos.y += self.vel.y * dt + (0.5 * self.acc.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		# self.collide_platforms(self.scene.platform_sprites, dt)
		self.collisions_y()
	
		if self.vel.y >= self.max_fall_speed: 
			self.vel.y = self.max_fall_speed

		elif abs(self.vel.y) >= 0.5:
			self.on_ground = False
			self.platform = None

	def got_headroom(self):
		for sprite in self.scene.block_sprites:
			raycast_box = pygame.Rect(self.hitbox.x, self.hitbox.y - TILESIZE/2, self.hitbox.width, self.hitbox.height)
			if sprite.hitbox.colliderect(raycast_box):
				return True
		return False

	def ladder_physics(self, dt):

		# x direction (multiply friction by 4 so easier to manage x direction on ladders)
		self.acc.x += self.vel.x * self.fric * 4
		self.vel.x += self.acc.x * dt
		self.pos.x += self.vel.x * dt + (0.5 * self.vel.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collisions_x()
		
		#y direction
		self.acc.y += self.vel.y * self.fric * 2
		self.vel.y += self.acc.y * dt
		self.pos.y += self.vel.y * dt + (0.5 * self.vel.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collisions_y()

	def handle_jumping(self, dt):
		# Double the gravity if not holding jump key to allow variale jump height
		if not pygame.key.get_pressed()[pygame.K_z] and self.vel.y < 0:
			self.acc.y = self.gravity * 2.5
		else:
			self.acc.y = self.gravity

		# incrememnt cyote timer when not on ground
		if not self.on_ground: 
			self.cyote_timer += dt
		else: 
			self.cyote_timer = 0

		# # if falling, this gives the player one jump if they have double jump
		# if self.jump_counter == 0 and self.cyote_timer < self.cyote_timer_threshold:
		# 	self.jump_counter = 1

		# jump buffer activated if pressing jump in air
		if self.jump_buffer_active:
			self.jump_buffer += dt
			if self.jump_buffer >= self.jump_buffer_threshold:
				self.jump_buffer = 0
				self.jump_buffer_active = False


	def state_logic(self):
		new_state = self.state.state_logic(self)
		if new_state: self.state = new_state
		else: self.state

	def update(self, dt):

		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()
		self.state_logic()
		self.state.update(self, dt)
		if self.alive:
			self.handle_jumping(dt)
			
		


	


		
		
		





