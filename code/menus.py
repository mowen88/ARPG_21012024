
import random
from state import State
from scene import Scene
from settings import *

class MenuBG(pygame.sprite.Sprite):
	def __init__(self, menu):

		self.menu = menu
		self.image = pygame.Surface((random.random()*TILESIZE, random.random()*TILESIZE))
		self.image.fill(DARK_GREEN)
		self.rect = self.image.get_rect()
		self.alpha = 255

		self.speed = (random.uniform(0.1, 1.0), random.uniform(0.1, 1.0))
		self.vel = pygame.math.Vector2(self.speed)
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.pos = (random.random() * WIDTH, random.random() * HEIGHT)

	def update(self, dt):
		self.alpha = random.randrange(0, 255)
		self.pos += self.vel * dt
		self.rect.topleft = self.pos

		if self.rect.x > WIDTH:
			self.pos.x = -self.rect.width
		if self.rect.y > HEIGHT:
			self.pos.y = -self.rect.height

	def draw(self, screen):
		self.image.set_alpha(self.alpha)
		screen.blit(self.image, self.rect)

class MenuTransition(pygame.sprite.Sprite):
	def __init__(self, menu):

		self.menu = menu
		self.surf = pygame.Surface((RES))
		self.surf.fill(WHITE)
		self.alpha = 255
		self.timer = RES * 0.1
		self.fade_in_duration = 600
		self.fade_out_duration = 750

	def update(self, dt):

		if not self.menu.transitioning:
			self.alpha -= self.fade_in_duration * dt
			if self.alpha <= 0: 
				self.alpha = 0
		else:
			self.alpha += self.fade_out_duration * dt
			if self.alpha >= 255:
				self.menu.go_to(self.menu.next_menu)

	def draw(self, screen):
		self.surf.set_alpha(self.alpha)
		screen.blit(self.surf, (0,0))

class PygameLogo(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.game = game
		self.timer = 1

		# logo
		self.logo_surf = pygame.image.load('../assets/pygame_logo.png').convert_alpha()
		self.logo_rect = self.logo_surf.get_rect(center = (HALF_WIDTH, HEIGHT * 0.6))

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)
		self.scene = Scene(self.game)
		self.main_menu = MainMenu(self.game)

	def go_to(self, state):
		#self.main_menu.enter_state()
		self.scene.enter_state()

	def update(self, dt):

		self.transition_screen.update(dt)

		self.timer -= dt
		if self.timer <= 0:
			self.next_menu = 'main_menu'
			self.transitioning = True
			self.game.reset_keys()

	def draw(self, screen):
		screen.fill(WHITE)
		screen.blit(self.logo_surf, self.logo_rect)
		self.game.render_text('Made with', BLACK, self.game.font, (HALF_WIDTH, HEIGHT * 0.3))
		self.transition_screen.draw(screen)

class MainMenu(State):
	def __init__(self, game):
		State.__init__(self, game)

		if len(self.game.stack) > 1:
			self.game.stack.pop()

		self.game = game
		self.alpha = 255
		self.next_menu = None
		self.padding = 24

		self.buttons = {
						'Start': [(HALF_WIDTH, HEIGHT * 0.2), 'slot_menu'],
						'Controls': [(HALF_WIDTH, HEIGHT * 0.2 + self.padding), 'controls_menu'],
						'Quit': [(HALF_WIDTH, HEIGHT * 0.2 + self.padding * 2), 'quit_game'],
						}

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)
		self.boxes = self.get_boxes()

		self.scene = Scene(self.game)

	def get_boxes(self):
		boxes = []
		for x in range(int(RES.magnitude()//2)):
			boxes.append(MenuBG(self))
		return boxes

	def render_button(self, screen, current_menu, next_menu, text_colour, button_colour, hover_colour, pos):
		mx, my = pygame.mouse.get_pos()

		colour = text_colour

		surf = self.game.font.render(current_menu, False, colour)
		rect = pygame.Rect(0,0, surf.get_width() + 16, surf.get_height() * 2)
		rect.center = pos

		if rect.collidepoint(mx, my) and not self.transitioning:
			pygame.draw.rect(screen, hover_colour, rect, 1)#int(HEIGHT * 0.05))
			pygame.draw.line(screen, NEON_GREEN, rect.midleft, (0, rect.centery), 1)
			pygame.draw.line(screen, NEON_GREEN, rect.midright, (WIDTH, rect.centery), 1)
			self.game.render_text(current_menu, text_colour, self.game.font, pos)
			if ACTIONS['left_click']:
				self.next_menu = next_menu
		else:
			#pygame.draw.rect(screen, button_colour, rect)#int(HEIGHT * 0.05))
			self.game.render_text(current_menu, text_colour, self.game.font, pos)

	def go_to(self, state):
		if state == 'quit_game':
			self.game.running = False
		else:
			self.scene.enter_state()

	def update(self, dt):

		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

		self.game.render_text('a fan game by Matt Owen', WHITE, self.game.font, (WIDTH * 0.82, HEIGHT * 0.95))

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.transition_screen.draw(screen)