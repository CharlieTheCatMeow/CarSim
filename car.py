import math
import pygame

import brain

class Car:
	def __init__(self, x, y, heading = 0.0):
		# Things that change
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		self.lateral_speed = 0.0
		self.velocity_x, self.velocity_y = 0.0, 0.0
		self.is_drifting = False
		
		# Stats
		self.drag = 0.3
		self.max_speed = 600
		self.max_reverse_speed = -80
		self.turn_rate = 7.0
		self.brake_force = 450.0
		self.accel = 150.0
		self.grip = 18.0
		self.drift_grip = 7.5
		
		# Ray casting stuff
		self.ray_count = 5
		self.fov = math.radians(120)
		self.ray_length = 300
		self.show_rays = False
		
		# Also things that change but not really
		self.length, self.width = 28, 14
		self.previous_rear_wheel_pos = self.get_rear_wheel_pos()
		self.alive = True
		self.time_alive = 0.0
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		self.time_since_last_checkpoint = 0.0
		
		# For RL
		self.brain = brain.Brain(input_size = self.ray_count + 3, hidden_sizes = [10], output_size = 2)
		self.fitness = 0.0
		
	def reset(self, x, y, heading = 0.0):
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		self.lateral_speed = 0.0
		self.velocity_x, self.velocity_y = 0.0, 0.0
		self.alive = True
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		self.time_since_last_checkpoint = 0.0
		self.fitness = 0.0
		self.time_alive = 0.0
		self.is_drifting = False
		self.previous_rear_wheel_pos = self.get_rear_wheel_pos()
		
	# Drive the car
	# Negative throttle is basically breaking
	def update(self, throttle, steering, dt):
		if not self.alive:
			return
		
		throttle = max(-1.0, min(1.0, throttle))
		steering = max(-1.0, min(1.0, steering))
		
		abs_speed = math.hypot(self.velocity_x, self.velocity_y)
		speed_ratio = min(1.0, abs_speed / max(1.0, self.max_speed))
		
		# Turning :O
		low_speed_turn = min(1.0, abs_speed / (self.max_speed * 0.20))
		high_speed_understeer = 1.0 - (speed_ratio * 0.55)
		if self.speed >= 0:
			direction = 1.0
		else:
			direction = -1.0
		effective_turn = self.turn_rate * low_speed_turn * high_speed_understeer * direction
		self.heading += steering * effective_turn * dt
		
		forward_x = math.cos(self.heading)
		forward_y = math.sin(self.heading)
		right_x = -forward_y
		right_y = forward_x
		
		forward_speed = self.velocity_x * forward_x + self.velocity_y * forward_y
		lateral_speed = self.velocity_x * right_x + self.velocity_y * right_y
		
		# Acceleration and braking too
		cornering_load = abs(steering) * speed_ratio
		if throttle > 0:
			power_curve = 1.0 - (speed_ratio ** 1.5) * 0.7
			forward_speed += self.accel * throttle * power_curve * dt
		elif throttle < 0:
			if self.speed > 5:
				forward_speed += self.brake_force * throttle * dt
			else:
				forward_speed += self.accel * throttle * 0.4 * dt
		
		# Grip?
		slip_ratio = abs(lateral_speed) / max(150.0, abs_speed)
		if slip_ratio > 0.15 and speed_ratio > 0.25:
			current_grip = self.drift_grip
			self.is_drifting = True
		else:
			current_grip = self.grip
			self.is_drifting = False
		
		lateral_speed *= max(0.0, 1.0 - current_grip * dt)
		
		# Drag and stuff
		aero_drag = self.drag * (speed_ratio ** 2) * forward_speed
		rolling_drag = self.drag * 0.15 * forward_speed
		corner_scrub = abs(steering) * speed_ratio * 0.35 * forward_speed
		forward_speed -= (aero_drag + rolling_drag + corner_scrub) * dt
		forward_speed = max(self.max_reverse_speed, min(self.max_speed, forward_speed))
		
		self.speed = forward_speed
		self.lateral_speed = lateral_speed
		self.velocity_x = forward_x * forward_speed + right_x * lateral_speed
		self.velocity_y = forward_y * forward_speed + right_y * lateral_speed
		
		self.previous_rear_wheel_pos = self.get_rear_wheel_pos()
		
		self.x += self.velocity_x * dt
		self.y += self.velocity_y * dt
		
		self.time_since_last_checkpoint += dt
		self.time_alive += dt
	
	# Uh I think this is where the ray casting stuff goes (For AI later on)
	# Lets hope I don't forget to delete the "for AI later on" part when I actually add it
	def cast_rays(self, track, ray_count = 5, fov = math.radians(120), ray_length = 200):
		ray_distances = []
		start_angle = self.heading - fov / 2
		for i in range(ray_count):
			ray_angle = start_angle + fov * (i / (ray_count - 1))
			distance = track.cast_ray(self.x, self.y, ray_angle, ray_length)
			ray_distances.append(distance / ray_length)
		return ray_distances
	
	# Angle to next checkpoint for the neural thing as an input
	def angle_to_next_checkpoint(self, track):
		target = track.checkpoints[self.next_checkpoint_index]
		dx = target[0] - self.x
		dy = target[1] - self.y
		angle_to_target = math.atan2(dy, dx) - self.heading
		angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi
		return angle_to_target
	
	def get_inputs(self, rays, track):
		output = []
		for ray in rays:
			output.append(max(0.0, min(1.0, ray)))
		output.append(self.speed / self.max_speed)
		output.append(self.angle_to_next_checkpoint(track) / math.pi)
		output.append(self.lateral_speed / self.max_speed)
		return output

	# Change car properties
	def change_properties(self, key, value):
		if key == "drag":
			self.drag = value
		elif key == "max_speed":
			self.max_speed = value
		elif key == "max_reverse_speed":
			self.max_reverse_speed = value
		elif key == "turn_rate":
			self.turn_rate = value
		elif key == "brake_force":
			self.brake_force = value
		elif key == "accel":
			self.accel = value
		elif key == "ray_count":
			new_ray_count = max(2, int(value))
			if new_ray_count != self.ray_count:
				self.ray_count = new_ray_count
				self.brain = brain.Brain(
					input_size=self.ray_count + 3,
					hidden_sizes=self.brain.hidden_sizes,
					output_size=self.brain.output_size
				)
		elif key == "fov":
			self.fov = math.radians(value)
		elif key == "ray_length":
			self.ray_length = value
		elif key == "grip":
			self.grip = value
		elif key == "drift_grip":
			self.drift_grip = value
	
	_sprite_cache = {}
	_shadow_surface = None
	
	def _get_car_surfaces(self, color = (0, 155, 155)):
		width, height = self.length + 6, self.width + 6
		
		if Car._shadow_surface is None:
			shadow = pygame.Surface((width, height), pygame.SRCALPHA)
			pygame.draw.rect(shadow, (0, 0, 0, 95), (2, 2, self.length + 2, self.width + 2), border_radius=5)
			Car._shadow_surface = shadow
		
		if color not in Car._sprite_cache:
			surface = pygame.Surface((width, height), pygame.SRCALPHA)
			body_x, body_y = 3, 3
			body_width, body_height = self.length, self.width
			
			wheel_color = (20, 20, 22)
			pygame.draw.rect(surface, wheel_color, (body_x + 4, body_y - 2, 6, 3), border_radius=1)
			pygame.draw.rect(surface, wheel_color, (body_x + 4, body_y + body_height - 1, 6, 3), border_radius=1)
			pygame.draw.rect(surface, wheel_color, (body_x + body_width - 9, body_y - 2, 6, 3), border_radius=1)
			pygame.draw.rect(surface, wheel_color, (body_x + body_width - 9, body_y + body_height - 1, 6, 3), border_radius=1)
			
			dark_color = (max(0, color[0] - 45), max(0, color[1] - 45), max(0, color[2] - 45))
			light_color = (min(255, color[0] + 45), min(255, color[1] + 45), min(255, color[2] + 45))
			pygame.draw.rect(surface, dark_color, (body_x, body_y, body_width, body_height), border_radius=4)
			
			stripe_color = (235, 235, 235, 160)
			pygame.draw.rect(surface, stripe_color, (body_x + 2, body_y + body_height // 2 - 1, body_width - 4, 2))
			
			glass_color = (30, 40, 55)
			pygame.draw.polygon(surface, glass_color, [
				(body_x + 14, body_y + 3),
				(body_x + 20, body_y + 2),
				(body_x + 20, body_y + body_height - 2),
				(body_x + 14, body_y + body_height - 3),
			])
			
			pygame.draw.rect(surface, light_color, (body_x + 8, body_y + 3, 7, body_height - 6), border_radius=2)
			
			pygame.draw.polygon(surface, glass_color, [
				(body_x + 5, body_y + 2),
				(body_x + 8, body_y + 3),
				(body_x + 8, body_y + body_height - 3),
				(body_x + 5, body_y + body_height - 2),
			])
			
			pygame.draw.rect(surface, dark_color, (body_x + 1, body_y + 3, 3, body_height - 2), border_radius=1)
			
			pygame.draw.rect(surface, (255, 245, 180), (body_x + body_width - 2, body_y + 2, 2, 3), border_radius=1)
			pygame.draw.rect(surface, (255, 245, 180), (body_x + body_width - 2, body_y + body_height - 5, 2, 3), border_radius=1)
			pygame.draw.rect(surface, (220, 30, 30), (body_x, body_y + 2, 2, 3))
			pygame.draw.rect(surface, (220, 30, 30), (body_x, body_y + body_height - 5, 2, 3))
			
			Car._sprite_cache[color] = surface
		
		return Car._sprite_cache[color], Car._shadow_surface
	
	# Draw the car
	def draw(self, screen, color = (0, 155, 155)):
		if not self.alive:
			color = (90, 90, 95)
		car_surface, shadow_surface = self._get_car_surfaces(color)
		angle = -math.degrees(self.heading)
		rotated_shadow = pygame.transform.rotate(shadow_surface, angle)
		screen.blit(rotated_shadow, rotated_shadow.get_rect(center=(self.x + 4, self.y + 4)))
		rotated_car = pygame.transform.rotate(car_surface, angle)
		screen.blit(rotated_car, rotated_car.get_rect(center=(self.x, self.y)))
	
	def get_rear_wheel_pos(self):
		rear_offset = self.length * 0.32
		rear_x = self.x - math.cos(self.heading) * rear_offset
		rear_y = self.y - math.sin(self.heading) * rear_offset
		
		side_offset = self.width * 0.38
		perpendicular_x = -math.sin(self.heading) * side_offset
		perpendicular_y = math.cos(self.heading) * side_offset
		
		left_wheel_pos = (rear_x + perpendicular_x, rear_y + perpendicular_y)
		right_wheel_pos = (rear_x - perpendicular_x, rear_y - perpendicular_y)
		return left_wheel_pos, right_wheel_pos
		
		
		