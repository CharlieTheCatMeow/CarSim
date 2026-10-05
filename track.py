import math

import pygame

class Track:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
		self.waypoints = [
			(150, 450),
			(950, 450),
			(1120, 400),
			(1150, 280),
			(1080, 160),
			(900, 90),
			(650, 110),
			(600, 220),
			(680, 300),
			(560, 360),
			(480, 280),
			(380, 340),
			(300, 460),
			(380, 560),
			(300, 600),
			(200, 540),
		]
		
		self.road_width = 40
		self.smoothed_points = self._chaikin_smoothing(self.waypoints)
		self._segments = list(zip(self.smoothed_points, self.smoothed_points[1:] + self.smoothed_points[:1]))
		self.checkpoints = self._create_checkpoints(150)
		
		self.grid_cell_size = 10
		self._track_grid = self._create_track_grid()
		
		self.mask_surface = pygame.Surface((self.width, self.height))
		self.mask_surface.fill((40, 120, 40))
		self._draw_track(self.mask_surface, (255, 255, 255))
	
	# Using the chaikin thingy to smooth the track points, looks bad otherwise
	def _chaikin_smoothing(self, points, corner_rounding = 0.9, iterations = 3):
		for _ in range(3):
			if corner_rounding == 1:
				return points
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
		for a, b in self._segments:
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
		
	# Do a grid of the track first for performance?
	def _create_track_grid(self):
		columns = self.width // self.grid_cell_size + 1
		rows = self.height // self.grid_cell_size + 1
		grid = [[False] * rows for _ in range(columns)]
		for x in range(columns):
			for y in range(rows):
				cell_x = x * self.grid_cell_size
				cell_y = y * self.grid_cell_size
				grid[x][y] = self._distance_to_centerline(cell_x, cell_y) <= self.road_width / 2
		return grid
	
	# Check if car is on track
	def is_on_track(self, x, y):
		cell_x = int(x) // self.grid_cell_size
		cell_y = int(y) // self.grid_cell_size
		if 0 <= cell_x < len(self._track_grid) and 0 <= cell_y < len(self._track_grid[0]):
			return self._track_grid[cell_x][cell_y]
		return False

	def _distance_to_centerline(self, x, y):
		points = self.smoothed_points
		closest_distance = float("inf")
		for a, b in self._segments:
			px, py, distance = self._distance_to_track_center(x, y, a, b)
			closest_distance = min(closest_distance, distance)
		return closest_distance
		
	def closest_point(self, x, y):
		points = self.smoothed_points
		closest_point = None
		closest_distance = float("inf")
		for a, b in self._segments:
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
	
	# Checkpoints
	def _create_checkpoints(self, checkpoint_count = 50):
		points = self.smoothed_points
		total_length = self._total_track_length()
		spacing = total_length / checkpoint_count
		
		checkpoints = [points[0]]
		accumulated = 0.0
		
		for a, b in self._segments:
			segment_dx = b[0] - a[0]
			segment_dy = b[1] - a[1]
			segment_length = math.hypot(segment_dx, segment_dy)
			if segment_length == 0:
				continue
				
			segment_start = accumulated
			segment_end = accumulated + segment_length
			accumulated += segment_length
			while len(checkpoints) < checkpoint_count:
				next_threshold = len(checkpoints) * spacing
				if next_threshold > segment_end:
					break
				t = (next_threshold - segment_start) / segment_length
				checkpoint_x = a[0] + t * segment_dx
				checkpoint_y = a[1] + t * segment_dy
				checkpoints.append((checkpoint_x, checkpoint_y))
			if len(checkpoints) >= checkpoint_count:
				break
		return checkpoints
	
	# Self-explanatory
	def _total_track_length(self):
		points = self.smoothed_points
		total = 0.0
		for a, b in self._segments:
			total += math.hypot(b[0] - a[0], b[1] - a[1])
		return total
	
	def count_checkpoints(self, x, y, next_checkpoint_index):
		if next_checkpoint_index >= len(self.checkpoints):
			return next_checkpoint_index, True
		
		target = self.checkpoints[next_checkpoint_index]
		if self._distance_to_track_checkpoint(x, y, target) < self.road_width / 1.8:
			next_checkpoint_index += 1
			if next_checkpoint_index == len(self.checkpoints):
				next_checkpoint_index = 0
				return next_checkpoint_index, True
		return next_checkpoint_index, False
	
	@staticmethod
	def _distance_to_track_checkpoint(point_x, point_y, checkpoint):
		ax, ay = checkpoint
		dx, dy = ax - point_x, ay - point_y
		distance = math.hypot(dx, dy)
		return distance
	
	# Ray casting stuff for AI later on (Hope this works and is actually useful)
	def cast_ray(self, x, y, angle, length, step = 8):
		dx = math.cos(angle)
		dy = math.sin(angle)
		distance = 0
		while distance < length:
			point_x = x + dx * distance
			point_y = y + dy * distance
			if not self.is_on_track(point_x, point_y):
				return distance
			distance += step
		return length
		
		
	
	
	














	