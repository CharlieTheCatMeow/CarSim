import math
import pygame
import random

class Track:
	def __init__(self, width, height, track_index=0, custom_waypoints=None):
		self.width = width
		self.height = height
		
		self.track_presets = [
			[
				(320, 610), (980, 610), (1140, 590), (1170, 470), (1020, 400),
				(880, 380), (920, 270), (1140, 240), (1160, 110), (980, 80),
				(680, 80), (540, 110), (520, 230), (660, 310), (620, 440),
				(440, 440), (340, 310), (180, 280), (110, 370), (120, 540),
				(200, 610),
			],
			[
				(380, 125), (620, 110), (860, 95), (950, 95), (990, 130),
				(945, 175), (820, 175), (690, 175), (625, 210), (635, 265),
				(730, 275), (800, 315), (745, 375), (570, 380), (510, 435),
				(560, 500), (740, 515), (830, 480), (920, 515), (1040, 565),
				(1115, 600), (1075, 650), (860, 645), (580, 610), (360, 560),
				(265, 535), (240, 570), (190, 545), (135, 465), (105, 395),
				(155, 375), (255, 410), (310, 365), (295, 275), (325, 185),
			],
			[
				(320, 180), (620, 180), (920, 180), (1090, 180), (1135, 205),
				(1115, 275), (970, 280), (915, 330), (1045, 365), (1055, 455),
				(920, 465), (845, 370), (745, 355), (690, 425), (740, 520),
				(855, 540), (885, 605), (790, 645), (540, 605), (310, 565),
				(215, 630), (155, 595), (245, 490), (330, 490), (395, 425),
				(485, 435), (545, 360), (455, 305), (345, 315), (235, 280),
				(125, 245), (110, 185), (185, 180),
			],
			[
				(300, 150), (580, 150), (860, 150), (935, 150), (955, 185),
				(1015, 175), (1115, 225), (1155, 340), (1140, 470), (1085, 515),
				(1065, 565), (1010, 620), (920, 610), (875, 540), (810, 475),
				(670, 415), (550, 375), (485, 380), (445, 330), (385, 325),
				(270, 320), (165, 315), (110, 275), (110, 195), (180, 155),
			],
			[
				(680, 565), (860, 565), (1020, 560), (1135, 520), (1155, 430),
				(1065, 375), (1095, 305), (995, 260), (1035, 190), (940, 145),
				(820, 110), (700, 130), (660, 210), (575, 330), (475, 475),
				(410, 565), (335, 540), (365, 445), (310, 340), (195, 265),
				(120, 200), (125, 115), (230, 105), (335, 165), (495, 275),
				(665, 390), (815, 465), (740, 495), (615, 515), (610, 560),
			],
			[
				(260, 440), (450, 440), (590, 440), (650, 435), (635, 355),
				(745, 245), (875, 145), (1005, 85), (1125, 95), (1160, 175),
				(1085, 225), (970, 220), (915, 275), (1035, 315), (1135, 355),
				(1155, 445), (1055, 515), (885, 545), (760, 560), (715, 520),
				(655, 560), (515, 560), (455, 630), (335, 630), (280, 565),
				(165, 565), (125, 505), (175, 445),
			],
		]
		if custom_waypoints is not None and len(custom_waypoints) >= 3:
			self.waypoints = list(custom_waypoints)
		else:
			self.waypoints = self.track_presets[track_index % len(self.track_presets)]
		
		self.road_width = 60
		self.smoothed_points = self._chaikin_smoothing(self.waypoints)
		self._segments = list(zip(self.smoothed_points, self.smoothed_points[1:] + self.smoothed_points[:1]))
		self.checkpoints = self._create_checkpoints(150)
		
		road_surface = pygame.Surface((self.width, self.height))
		self._draw_track_layer(road_surface, (255, 255, 255), self.road_width)
		self._track_bytes = pygame.image.tobytes(road_surface, "RGB")[::3]
		
		self.mask_surface = pygame.Surface((self.width, self.height))
		self._render_environment(self.mask_surface)
	
	# Using the chaikin thingy to smooth the track points, looks bad otherwise
	def _chaikin_smoothing(self, points, corner_rounding = 0.9, iterations = 3):
		for _ in range(iterations):
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
		self._draw_start_line(surface)
		
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
	
	def _draw_start_line(self, surface):
		(x0, y0), (x1, y1) = self.checkpoints[0], self.checkpoints[1]
		dx, dy = x1 - x0, y1 - y0
		length = math.hypot(dx, dy)
		if length == 0:
			return
		normal_x, normal_y = -dy / length, dx / length
		half_width = self.road_width / 2
		start_pos = (x0 + normal_x * half_width, y0 + normal_y * half_width)
		end_pos = (x0 - normal_x * half_width, y0 - normal_y * half_width)
		pygame.draw.line(surface, (240, 240, 240), start_pos, end_pos, 5)
	
	def draw(self, screen):
		screen.blit(self.mask_surface, (0, 0))
	
	# Check if car is on track
	def is_on_track(self, x, y):
		ix, iy = int(x), int(y)
		if 0 <= ix < self.width and 0 <= iy < self.height:
			return self._track_bytes[iy * self.width + ix] != 0
		return False
		
	@staticmethod
	def _distance_to_track_center(point_x, point_y, point_a, point_b):
		ax, ay = point_a
		bx, by = point_b
		dx, dy = bx - ax, by - ay
		length_squared = dx**2 + dy**2
		
		if length_squared == 0:
			return ax, ay, math.hypot(point_x - ax, point_y - ay)
		
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
		if total_length <= 1e-6:
			return [points[0], points[1 % len(points)]]
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
	def cast_ray(self, x, y, angle, length, step = 16):
		dx = math.cos(angle)
		dy = math.sin(angle)
		distance = step
		while distance <= length:
			if not self.is_on_track(x + dx * distance, y + dy * distance):
				low = distance - step
				high = distance
				for _ in range(4):
					mid = (low + high) / 2
					if not self.is_on_track(x + dx * mid, y + dy * mid):
						high = mid
					else:
						low = mid
				return high
			distance += step
		return length
		
	def get_start_pos(self):
		x0, y0 = self.checkpoints[0]
		x1, y1 = self.checkpoints[1]
		heading = math.atan2(y1 - y0, x1 - x0)
		return x0, y0, heading
		
	
	
	














	