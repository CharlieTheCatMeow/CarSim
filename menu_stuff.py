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
		pygame.draw.rect(screen, color, self.rect, border_radius = 7)
		pygame.draw.rect(screen, (200, 200, 200), self.rect, width=2, border_radius = 7)
		
		text_surface = self.font.render(self.text, True, (255, 255, 255))
		screen.blit(text_surface, text_surface.get_rect(center = self.rect.center))
		
	def is_clicked(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)































