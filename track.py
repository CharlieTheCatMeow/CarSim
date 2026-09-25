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
		self.smoothed_points = self._chaikin_smoothing(self.waypoints)
		
		self.mask_surface = pygame.Surface((self.width, self.height))
		self.mask_surface.fill((40, 120, 40))
		self._draw_track(self.mask_surface, (255, 255, 255))
	
	# Using the chaikin thingy to smooth the track points, looks bad otherwise
	def _chaikin_smoothing(self, points, corner_rounding = 0.9, iterations = 3):
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
		return points
	
	# Draw the track
	def _draw_track(self, surface, color):
		points = self.smoothed_points
		
		half_width = self.road_width / 2
		for a, b in zip(points, points[1:] + points[:1]):
			dx = b[0] - a[0]
			dy = b[1] - a[1]
			length = math.hypot(dx, dy)
			if length == 0:
				continue
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
		
	# Check if car is on track
	def is_on_track(self, x, y):
		if self._distance_to_centerline(x, y) > self.road_width / 2:
			return False
		return True

	def _distance_to_centerline(self, x, y):
		points = self.smoothed_points
		closest_distance = float("inf")
		for a, b in zip(points, points[1:] + points[:1]):
			px, py, distance = self._distance_to_track_center(x, y, a, b)
			closest_distance = min(closest_distance, distance)
		return closest_distance
		
	def closest_point(self, x, y):
		points = self.smoothed_points
		closest_point = None
		closest_distance = float("inf")
		for a, b in zip(points, points[1:] + points[:1]):
			point_x, point_y, distance = self._distance_to_track_center(x, y, a, b)
			if distance < closest_distance:
				closest_distance = distance
				closest_point = (point_x, point_y)
		return closest_point
		
	@staticmethod
	def _distance_to_track_center(point_x, point_y, point_a, point_b):
		ax, ay = point_a
		bx, by = point_b
		dx, dy = bx - ax, by - ay
		length_squared = dx**2 + dy**2
		
		if length_squared == 0:
			return math.hypot(point_x - ax, point_y - ay)
		
		t = ((point_x-ax) * dx + (point_y - ay) * dy) / length_squared
		t = max(0.0, min(1.0, t))
		
		closest_x = ax + t * dx
		closest_y = ay + t * dy
		distance = math.hypot(point_x - closest_x, point_y - closest_y)
		return closest_x, closest_y, distance
		
		