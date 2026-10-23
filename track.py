import math
import pygame
import random

class Track:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
		self.waypoints = [
			(320, 610),
			(980, 610),
			(1140, 590),
			(1170, 470),
			(1020, 400),
			(880, 380),
			(920, 270),
			(1140, 240),
			(1160, 110),
			(980, 80),
			(680, 80),
			(540, 110),
			(520, 230),
			(660, 310),
			(620, 440),
			(440, 440),
			(340, 310),
			(180, 280),
			(110, 370),
			(120, 540),
			(200, 610),
		]
		
		self.road_width = 60
		self.smoothed_points = self._chaikin_smoothing(self.waypoints)
		self._segments = list(zip(self.smoothed_points, self.smoothed_points[1:] + self.smoothed_points[:1]))
		self.checkpoints = self._create_checkpoints(150)
		
		self.grid_cell_size = 10
		self._track_grid = self._create_track_grid()
		
		self.mask_surface = pygame.Surface((self.width, self.height))
		self._render_environment(self.mask_surface)
	
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
	
	# Render track but now in multiple parts and prettier
	def _render_environment(self, surface):
		# Background grass with some stripes (looked a bit flat before)
		stripe_width = 40
		for x in range(0, self.width, stripe_width):
			if (x // stripe_width) % 2 == 0:
				grass_color = (82, 128, 82)
			else:
				grass_color = (75, 120, 75)
			pygame.draw.rect(surface, grass_color, (x, 0, stripe_width, self.height))
		
		# Small grass details
		rng = random.Random(42)
		for _ in range(500):
			grass_x, grass_y = rng.randint(0, self.width - 1), rng.randint(0, self.height - 1)
			if rng.random() < 0.5:
				grass_specks_color = (65, 108, 65)
			else:
				grass_specks_color = (92, 140, 92)
			surface.fill(grass_specks_color, (grass_x, grass_y, 2, 2))
			
		# All the other functions:
		self._draw_track_layer(surface, (48, 78, 48), self.road_width + 14, width_offset=(5, 5))
		self._draw_curbs(surface, self.road_width + 8)
		self._draw_track_layer(surface, (30, 33, 37), self.road_width + 2)
		self._draw_track_layer(surface, (48, 52, 58), self.road_width)
		self._draw_track_layer(surface, (55, 60, 66), self.road_width - 20)
		
	def _draw_track_layer(self, surface, color, width, width_offset=(0, 0)):
		offset_x, offset_y = width_offset
		width_half = width / 2      # Shocking
		for a, b in self._segments:
			ax, ay = a[0] + offset_x, a[1] + offset_y
			bx, by = b[0] + offset_x, b[1] + offset_y
			dx, dy = bx - ax, by - ay
			length = math.hypot(dx, dy)
			if length == 0:
				continue
			normal_x, normal_y = -dy / length, dx / length
			quad = [
				(ax + normal_x * width_half, ay + normal_y * width_half),
				(ax - normal_x * width_half, ay - normal_y * width_half),
				(bx - normal_x * width_half, by - normal_y * width_half),
				(bx + normal_x * width_half, by + normal_y * width_half),
			]
			pygame.draw.polygon(surface, color, quad)
			pygame.draw.circle(surface, color, (int(ax), int(ay)), int(width_half))
			
	def _draw_curbs(self, surface, width):
		width_half = width / 2      # Shocking, again
		stripe_length = 10.0
		corner_radius = 65.0
		corners = []
		waypoint_amount = len(self.waypoints)
		for i in range(waypoint_amount):
			previous_point = self.waypoints[(i - 1) % waypoint_amount]
			current_point = self.waypoints[i % waypoint_amount]
			next_point = self.waypoints[(i + 1) % waypoint_amount]
			
			angle1 = math.atan2(current_point[1] - previous_point[1], current_point[0] - previous_point[0])
			angle2 = math.atan2(next_point[1] - current_point[1], next_point[0] - current_point[0])
			turn_angle = abs((angle2 - angle1 + math.pi) % (2 * math.pi) - math.pi)
			if turn_angle > math.radians(25):
				corners.append(current_point)
				
			total_distance = 0.0
			for a, b in self._segments:
				dx, dy = b[0] - a[0], b[1] - a[1]
				segment_length = math.hypot(dx, dy)
				if segment_length == 0:
					continue
				ux, uy = dx / segment_length, dy / segment_length
				normal_x, normal_y = -uy, ux
				
				steps = max(1, int(math.ceil(segment_length / stripe_length)))
				step_length = segment_length / steps
				
				for s in range(steps):
					d0 = s * step_length
					d1 = (s + 1) * step_length
					middle_x = a[0] + ux * (d0 + d1) / 2
					middle_y = a[1] + uy * (d0 + d1) / 2
					if any(math.hypot(middle_x - cx, middle_y - cy) < corner_radius for cx, cy in corners):
						stripe_index = int((total_distance + d0) // stripe_length)
						if stripe_index % 2 == 0:
							color = (210, 45, 45)
						else:
							color = (235, 235, 235)
						point0_x, point0_y = a[0] + ux * d0, a[1] + uy * d0
						point1_x, point1_y = a[0] + ux * (d1 + 1.5), a[1] + uy * (d1 + 1.5)
						quad = [
							(point0_x + normal_x * width_half, point0_y + normal_y * width_half),
							(point0_x - normal_x * width_half, point0_y - normal_y * width_half),
							(point1_x - normal_x * width_half, point1_y - normal_y * width_half),
							(point1_x + normal_x * width_half, point1_y + normal_y * width_half),
						]
						pygame.draw.polygon(surface, color, quad)
				total_distance += segment_length
				
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
		
		
	
	
	














	