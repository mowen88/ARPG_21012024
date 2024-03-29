import pygame
from settings import *

class Death:
	def __init__(self, player):
		
		player.scene.create_particle('chunk',player.rect.center)
		player.scene.drawn_sprites.remove(player)
		player.gun_sprite.kill()
		self.timer = 100

	def state_logic(self, player):
		if self.timer < 0:
			player.scene.respawn()

	def update(self, player, dt):
		self.timer -= dt

class Fall:
	def __init__(self, player):
		
		player.frame_index = 0
		self.timer = 10

	def state_logic(self, player):

		# if player.collide_ladders() and player.vel.y > 0:
		# 	return OnLadderIdle(player)

		if not player.alive:
			return Death(player)
		if ACTIONS['x'] and player.can_attack:
			return AirAttack(player)
		if ACTIONS['c'] and player.can_dash:
			return AirDash(player)
		if ACTIONS['z']:
			player.jump_buffer_active = True
			ACTIONS['z'] = False
			if player.jump_counter > 0:
				if player.cyote_timer < player.cyote_timer_threshold:
					return Jump(player)
				else:
					return DoubleJump(player)

		if player.on_ground:
			if player.jump_buffer > 0:
				player.jump_counter = 1
				return Jump(player)
			elif ACTIONS['down']:
				return Crouch(player)
			else:
				return Landing(player)

	def update(self, player, dt):

		self.timer -= dt
		if self.timer < 0:
			player.drop_through = False

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('fall', 0.25 * dt, False)

class Idle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.combo_counter = 1
		player.frame_index = 0
		player.acc_rate = 0.4
		player.can_attack = True
		player.can_dash = True
		self.kill_weapon(player)

	def kill_weapon(self, player):
		if player.weapon:
			player.weapon.kill()

	def state_logic(self, player):

		if player.scene.exiting:
			return Hold(player)

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['c']:
			return Dash(player)

		if ACTIONS['x'] and player.can_attack:
			return Attack(player)

		if ACTIONS['down'] and not player.drop_through:
			return Crouch(player)

		if ACTIONS['z']:
			ACTIONS['z'] = False
			return Jump(player)

		if ACTIONS['z'] and player.collide_ladders():
			return OnLadderIdle(player)

		if not (ACTIONS['left'] and ACTIONS['right']) and (ACTIONS['left'] or ACTIONS['right']):
			return Move(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('idle', 0.25 * dt, False)

		player.get_on_ground()

class Move(Idle):
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0
		self.kill_weapon(player)

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['c']:
			return Dash(player)

		if ACTIONS['x']:
			return Attack(player)

		if ACTIONS['z']:
			ACTIONS['z'] = False
			return Jump(player)

		if ACTIONS['z'] and player.collide_ladders():
			return OnLadderIdle(player)

		if ACTIONS['down']:
			return Crouch(player)
			
		if not ACTIONS['left'] and not ACTIONS['right'] or (ACTIONS['left'] and ACTIONS['right']):
			return Idle(player)

	def update(self, player, dt):

		player.get_on_ground()
		
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('run', 0.25 * dt)

class Dash(Move):
	def __init__(self, player):
		
		player.frame_index = 0
		ACTIONS['c'] = False
		self.attack_pending = False
		self.timer = 48
		self.transition_time = 40
		player.vel.x = 24 * player.facing

	def state_logic(self, player):

		if player.frame_index <= len(player.animations['dash'])-1:
			if ACTIONS['z']:
				ACTIONS['z'] = False
				return Jump(player)
			if self.timer <= self.transition_time:
				if self.attack_pending:
					return Attack(player)
				elif not (ACTIONS['left'] and ACTIONS['right']) and (ACTIONS['left'] or ACTIONS['right']):
					return Move(player)
		else:
			return Idle(player)

	def update(self, player, dt):
		self.timer -= dt
		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('dash', 0.25 * dt, False)

class AirDash:
	def __init__(self, player):
		Dash. __init__(self, player)

		player.can_dash = False
		ACTIONS['c'] = False

	def state_logic(self, player):

		if player.frame_index <= len(player.animations['air_dash'])-1:
			if ACTIONS['z']:
				ACTIONS['z'] = False
				if player.jump_counter > 0:
					return DoubleJump(player)
			if self.timer <= self.transition_time:
				if self.attack_pending:
					return Attack(player)
				elif not (ACTIONS['left'] and ACTIONS['right']) and (ACTIONS['left'] or ACTIONS['right']):
					return Fall(player)
		else:
			return Fall(player)


	def update(self, player, dt):
		self.timer -= dt
		player.acc.x = 0
		player.vel.x -= 0.04 * dt * player.facing
		player.vel.y = 0
		player.physics_x(dt)
		player.animate('air_dash', 0.25 * dt, False)

class Attack(Dash):
	def __init__(self, player):

		self.interval_times = {1:18, 2:18, 3:32}
		
		player.frame_index = 0
		ACTIONS['x'] = False
		self.attack_pending = False
		self.timer = 48
		self.transition_time = self.attack_cancel_intervals(player)
		self.special_time = 16
		self.special_timer = 0
		player.vel.x = 4 * player.facing

		self.kill_weapon(player)
		player.scene.create_melee('sword', f'attack_{player.combo_counter}')

	def attack_cancel_intervals(self, player):
		for key, value in self.interval_times.items():
			if player.combo_counter == key:
				return self.timer - value

	def stop(self, player):
		if abs(player.vel.x) < 0.2:
			player.vel.x = 0

	def increment_combo_count(self, player):
		if player.combo_counter < 3:
			player.combo_counter += 1
		else:
			player.combo_counter = 1

	def build_up_special(self, player, dt):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_x]:
			self.special_timer += dt
		else:
			self.special_timer = 0

	def state_logic(self, player):

		if ACTIONS['x']:
			self.attack_pending = True

		if player.frame_index <= len(player.animations[f'attack_{player.combo_counter}'])-1:
			if self.special_timer >= self.special_time:
				return UpAttack(player)
			elif self.timer <= self.transition_time:
				if self.attack_pending:
					self.increment_combo_count(player)
					if player.on_ground:
						return Attack(player)
					else:
						return AirAttack(player)
				elif not (ACTIONS['left'] and ACTIONS['right']) and (ACTIONS['left'] or ACTIONS['right']):
					return Move(player)
		else:
			return Idle(player)

	def update(self, player, dt):

		self.timer -= dt
		self.build_up_special(player, dt)
		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate(f'attack_{player.combo_counter}', 0.25 * dt, False)

class AirAttack(Attack):
	def __init__(self, player):
		Attack.__init__(self, player)

		player.can_attack = False

	def state_logic(self, player):
		if ACTIONS['x']:
			self.attack_pending = True

		if player.frame_index <= len(player.animations[f'attack_{player.combo_counter}'])-1:
			
			if self.special_timer >= self.special_time:
				return DownAttack(player)
			elif self.timer <= self.transition_time:
				if self.attack_pending:
					self.increment_combo_count(player)
					return AirAttack(player)
				elif not (ACTIONS['left'] and ACTIONS['right']) and (ACTIONS['left'] or ACTIONS['right']):
					return Fall(player)
		else:
			return Fall(player)

	def update(self, player, dt):
		self.timer -= dt
		self.build_up_special(player, dt)
		player.acc.x = 0
		player.physics_x(dt)
		player.animate(f'attack_{player.combo_counter}', 0.25 * dt, False)

class UpAttack(Attack):
	def __init__(self, player):

		player.frame_index = 0
		player.combo_counter = 1
		ACTIONS['x'] = False
		player.jump(player.jump_height * 1.5)
		player.scene.create_particle('jump', player.hitbox.midbottom)
		self.kill_weapon(player)
		player.scene.create_melee('sword', 'up_attack')
		
	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y >= 0:
			return Fall(player)

		if ACTIONS['x']:
			return AirAttack(player)

		if ACTIONS['z'] and player.jump_counter > 0:
			ACTIONS['z'] = False

			return DoubleJump(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_y(dt)
		player.animate('up_attack', 0.25 * dt, False)

class DownAttack(Attack):
	def __init__(self, player):
		
		player.frame_index = 0
		ACTIONS['x'] = False
		self.kill_weapon(player)
		player.scene.create_melee('sword', 'down_attack')

	def state_logic(self, player):
		
		if player.on_ground:
			return Stomp(player)

	def update(self, player, dt):
		player.acc.x = 0
		player.vel.y += 1 * dt
		player.physics_y(dt)
		player.animate('down_attack', 0.25 * dt, False)

class Stomp(Attack):
	def __init__(self, player):

		player.frame_index = 0
		self.timer = 48
		self.kill_weapon(player)
		player.scene.create_melee('sword', 'stomp_attack')

	def state_logic(self, player):
		if self.timer <= 0:
			return Idle(player)

	def update(self, player, dt):
		self.timer -= dt
		player.vel.y = 0
		player.animate('stomp_attack', 0.25 * dt, False)
		
class Crouch:
	def __init__(self, player):
		
		player.frame_index = 0
		# slow the player if moving when crouched
		player.acc_rate = 0.2

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not ACTIONS['down'] and not player.got_headroom() or player.vel.y > 1:
			if hasattr(player.platform, 'direction'):
				player.hitbox.bottom = player.platform.hitbox.bottom
			elif player.platform is not None:
				if player.platform.vel == pygame.math.Vector2():
					player.hitbox.bottom = player.platform.hitbox.bottom
			return Idle(player)

		if ACTIONS['x']:
			player.fire()

		if ACTIONS['z']:
			player.drop_through = True
			ACTIONS['z'] = False

		if abs(player.vel.x) >= 0.1:
			return CrouchMove(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)

		# slow the player if moving when crouched
		# player.vel.x = player.vel.x / 2 * dt

		player.physics_y(dt)
		player.animate('crouch', 0.2 * dt, False)

		player.get_on_ground()

class CrouchMove:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not ACTIONS['down'] and not player.got_headroom() or player.vel.y > 1:
			if hasattr(player.platform, 'direction'):
				player.hitbox.bottom = player.platform.hitbox.bottom
			elif player.platform is not None:
				if player.platform.vel == pygame.math.Vector2():
					player.hitbox.bottom = player.platform.hitbox.bottom
			return Idle(player)

		if ACTIONS['x']:
			player.fire()

		if ACTIONS['z']:
			player.drop_through = True
			ACTIONS['z'] = False

		if abs(player.vel.x) <= 0.1:
			return Crouch(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('crouch', 0.25 * dt, False)
		player.get_on_ground()

class OnLadderIdle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.on_ground = True

		# remove gun sprite from player when using ladder
		player.gun_sprite.kill()

		# stop auto weapons firing
		ACTIONS['x'] = False

	def state_logic(self, player):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP] or keys[pygame.K_w]:
			player.acc.y = -player.acc_rate * 0.5
			
		elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
			player.acc.y = player.acc_rate * 0.5
			
		else:
			player.acc.y = 0

		if player.vel.magnitude() >= 0.1:
			return OnLadderMove(player)

		if not player.alive:
			return Death(player)

		if not player.collide_ladders():
			player.scene.create_player_gun()
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.ladder_physics(dt)

		player.animate('on_ladder_idle', 0.25 * dt, False)

class OnLadderMove:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0
		player.on_ground = True

	def state_logic(self, player):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP] or keys[pygame.K_w]:
			player.acc.y = -player.acc_rate * 0.5
		elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
			player.acc.y = player.acc_rate * 0.5
		else:
			player.acc.y = 0

		if player.vel.magnitude() <= 0.1:
			return OnLadderIdle(player)

		if not player.alive:
			return Death(player)

		if not player.collide_ladders():
			player.scene.create_player_gun()
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.ladder_physics(dt)

		player.animate('on_ladder_move', 0.25 * dt)

class Landing:
	def __init__(self, player):

		player.jump_counter = 1
		player.frame_index = 0
		player.scene.create_particle('landing', player.hitbox.midbottom)
		self.last_frame = len(player.animations['land'])-1

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['x']:
			return Attack(player)

		if ACTIONS['z']:
			ACTIONS['z'] = False
			return Jump(player)

		if player.frame_index > self.last_frame:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('land', 0.25 * dt)

class Jump(Fall):
	def __init__(self, player):

		player.frame_index = 0
		player.combo_counter = 1
		player.can_attack = True
		player.can_dash = True
		player.jump(player.jump_height)
		player.scene.create_particle('jump', player.hitbox.midbottom)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y >= 0:
			return Fall(player)

		if ACTIONS['x'] and player.can_attack:
			return AirAttack(player)

		if ACTIONS['c'] and player.can_dash:
			return AirDash(player)

		if ACTIONS['z'] and player.jump_counter > 0:
			ACTIONS['z'] = False

			return DoubleJump(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('jump', 0.25 * dt, False)

class DoubleJump(Fall):
	def __init__(self, player):

		player.jump_counter = 0
		player.frame_index = 0
		player.jump(player.jump_height)
		player.scene.create_particle('double_jump', player.hitbox.midbottom)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)
		if ACTIONS['x'] and player.can_attack:
			return AirAttack(player)
		if ACTIONS['c'] and player.can_dash:
			return AirDash(player)
		if player.vel.y >= 0:
			return Fall(player)

	def update(self, player, dt):
		
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('jump', 0.25 * dt, False)