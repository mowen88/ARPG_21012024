class State():
	def __init__(self, game):
		self.game = game
		self.prev_state = None

	def update(self, dt):
		pass

	def draw(self, screen):
		pass

	def enter_state(self):
		if len(self.game.stack) > 1:
			self.prev_state = self.game.stack[-1]
		self.game.stack.append(self)

	def exit_state(self):
		self.game.stack.pop()