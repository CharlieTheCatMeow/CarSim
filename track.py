import math

import pygame

class Track:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
		self.waypoints = [
			(200, 360), (300, 180), (600, 120), (950, 180),
			(1080, 360), (950, 560), (600, 610), (300, 560)
		]
		self.road_width = 80
		
		self.mask_surface = pygame.Surface((self.width, self.height))
		self.mask_surface.fill((40, 120, 40))
		self._draw_track(self.mask_surface, (255, 255, 255))
		
	def _draw_track(self, surface, color, corner_rounding = 0.9):
		points = self.waypoints
		
		for _ in range(3):
			if corner_rounding == 1:
				return
			chaikin_points = []
			length_points = len(points)
			for i in range(length_points):
				point0 = points[i]
				point1 = points[(i + 1) % length_points]
				
				q = (corner_rounding * point0[0] + (1 - corner_rounding) * point1[0], corner_rounding * point0[1] + (1 - corner_rounding) * point1[1])
				r = ((1 - corner_rounding) * point0[0] + corner_rounding * point1[0], (1 - corner_rounding) * point0[1] + corner_rounding * point1[1])
				
				chaikin_points.append(q)
				chaikin_points.append(r)
			points = chaikin_points
		
		half_width = self.road_width / 2
		for a, b in zip(points, points[1:] + points[:1]):
			dx = b[0] - a[0]
			dy = b[1] - a[1]
			length = math.hypot(dx, dy)
			nx = -dy / length
			ny = dx / length
			quad = [
				(a[0] + nx * half_width, a[1] + ny * half_width),
				(a[0] - nx * half_width, a[1] - ny * half_width),
				(b[0] - nx * half_width, b[1] - ny * half_width),
				(b[0] + nx * half_width, b[1] + ny * half_width)
			]
			pygame.draw.polygon(surface, color, quad)
			pygame.draw.circle(surface, color, a, int(half_width))
			
	def draw(self, screen):
		screen.blit(self.mask_surface, (0, 0))
		
		
		