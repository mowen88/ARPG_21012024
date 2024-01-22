import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,224)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)


HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False, 'left':False, 'right':False, 'e':False,
			'tab':False, 'left_click':False, 'right_click':False, 'scroll_up':False, 'scroll_down':False, 'r':False}

LAYERS = {'background':0,
		  'objects':1,
		  'player':2,
		  'particles':3,
		  'liquid':4,
		  'blocks':5,
		  'secret_blocks':6,
		  'foreground':7}

FONT = '../assets/homespun.ttf'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (212, 30, 60)
BLUE = (20,68,145)
NEON_BLUE = (120, 215, 225)
NEON_GREEN = (150, 225, 60)
DARK_GREEN = (23, 35, 23)
YELLOW = (255, 255, 64)
BROWN = (110, 74, 57)
DARK_BROWN = (23, 15, 11)
LIGHT_GREY = (146,143,184)