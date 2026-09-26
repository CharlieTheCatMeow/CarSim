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
		self.checkpoints = self._create_checkpoints(50)
		
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
	
	# Checkpoints
	def _create_checkpoints(self, checkpoint_count = 50):
		points = self.smoothed_points
		total_length = self._total_track_length()
		spacing = total_length / checkpoint_count
		
		checkpoints = [points[0]]
		accumulated = 0.0
		
		for a, b in zip(points, points[1:] + points[:1]):
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
		for a, b in zip(points, points[1:] + points[:1]):
			total += math.hypot(b[0] - a[0], b[1] - a[1])
		return total
	
	def count_checkpoints(self, x, y, next_checkpoint_index):
		if next_checkpoint_index >= len(self.checkpoints):
			return next_checkpoint_index, True
		
		target = self.checkpoints[next_checkpoint_index]
		if self._distance_to_track_checkpoint(x, y, target) < self.road_width / 1.8:
			next_checkpoint_index += 1
			print(f"Checkpoint {next_checkpoint_index} reached!")
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
	def cast_ray(self, x, y, angle, length, step = 4):
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
		
		
	
	
	














	