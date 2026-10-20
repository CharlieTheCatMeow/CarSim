import pygame


class Button:
	def __init__(self, rect, text, font, action):
		self.rect = pygame.Rect(rect)
		self.text = text
		self.font = font
		self.action = action
	
	def draw(self, screen, mouse_pos):
		hovered = self.rect.collidepoint(mouse_pos)
		if hovered:
			color = (90, 90, 90)
		else:
			color = (60, 60, 60)
		pygame.draw.rect(screen, color, self.rect, border_radius=7)
		pygame.draw.rect(screen, (200, 200, 200), self.rect, width=2, border_radius=7)
		
		text_surface = self.font.render(self.text, True, (255, 255, 255))
		screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))
	
	def is_clicked(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)


class InputField:
	def __init__(self, rect, text, font, max_length=5, title="", key=None, allow_decimals=False):
		self.rect = pygame.Rect(rect)
		self.text = text
		self.font = font
		self.key = key
		self.max_length = max_length
		self.numeric_only = True
		self.active = False
		self.title = title
		self.allow_decimals = allow_decimals
	
	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			self.active = self.rect.collidepoint(event.pos)
		if event.type == pygame.KEYDOWN and self.active:
			if event.key == pygame.K_BACKSPACE:
				self.text = self.text[:-1]
			elif event.key == pygame.K_RETURN:
				self.active = False
			elif event.key == pygame.K_ESCAPE:
				pass
			elif len(self.text) < self.max_length:
				char = event.unicode
				if char and (not self.numeric_only or char.isdigit() or (
						self.allow_decimals and char == "." and "." not in self.text)):
					self.text += char
	
	def get_number(self, fallback):
		try:
			if self.allow_decimals:
				value = float(self.text)
			else:
				value = int(self.text)
		except ValueError:
			value = 0
		if value > 0:
			return value
		self.text = str(fallback)
		return fallback
	
	def draw(self, screen):
		pygame.draw.rect(screen, (30, 30, 30), self.rect, border_radius=7)
		
		if self.active:
			border_color = (100, 180, 255)
		else:
			border_color = (200, 200, 200)
		
		pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=7)
		
		text_surface = self.font.render(self.text, True, (255, 255, 255))
		text_pos = (self.rect.x + 8, self.rect.centery - text_surface.get_height() // 2)
		screen.blit(text_surface, text_pos)
		
		if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
			cursor_x = text_pos[0] + text_surface.get_width() + 2
			pygame.draw.line(screen, (255, 255, 255), (cursor_x, self.rect.y + 6), (cursor_x, self.rect.bottom - 6), 2)
		
		if self.title:
			title_surface = self.font.render(self.title, True, (255, 255, 255))
			title_pos = (self.rect.centerx - title_surface.get_width() // 2, self.rect.y - title_surface.get_height() - 4)
			screen.blit(title_surface, title_pos)