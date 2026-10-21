import math
import pygame

import brain

class Car:
	def __init__(self, x, y, heading = 0.0):
		# Things that change
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		
		# Stats
		self.drag = 0.3
		self.max_speed = 600
		self.max_reverse_speed = -80
		self.turn_rate = 7.0
		self.brake_force = 450.0
		self.accel = 150.0
		
		# Ray casting stuff
		self.ray_count = 5
		self.fov = math.radians(120)
		self.ray_length = 300
		self.show_rays = False
		
		# Also things that change but not really
		self.length, self.width = 28, 14
		self.alive = True
		self.time_alive = 0.0
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		self.time_since_last_checkpoint = 0.0
		
		# For RL
		self.brain = brain.Brain(input_size = self.ray_count + 2, hidden_sizes = [10], output_size = 2)
		self.fitness = 0.0
		
	def reset(self, x, y, heading = 0.0):
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		self.alive = True
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		self.time_since_last_checkpoint = 0.0
		self.fitness = 0.0
		
	# Drive the car
	# Negative throttle is basically breaking
	def update(self, throttle, steering, dt):
		if not self.alive:
			return
		
		throttle = max(-1.0, min(1.0, throttle))
		steering = max(-1.0, min(1.0, steering))
		
		# Acceleration
		if throttle > 0:
			speed_ratio = max(0.0, self.speed) / self.max_speed
			self.speed += self.accel * throttle * (1.0 - speed_ratio) * dt
		elif throttle < 0:
			if self.speed > 0:
				self.speed += self.brake_force * throttle * dt
			else:
				self.speed += self.accel * throttle * 0.5 * dt
		
		# Drag and stuff
		self.speed *= (1.0 - self.drag * dt)
		self.speed = max(self.max_reverse_speed, min(self.max_speed, self.speed))
		
		# Turning :O
		speed_factor = self.speed / self.max_speed
		self.heading += steering * self.turn_rate * speed_factor * dt
		
		self.x += math.cos(self.heading) * self.speed * dt
		self.y += math.sin(self.heading) * self.speed * dt
		
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
					input_size=self.ray_count + 2,
					hidden_sizes=self.brain.hidden_sizes,
					output_size=self.brain.output_size
				)
		elif key == "fov":
			self.fov = math.radians(value)
		elif key == "ray_length":
			self.ray_length = value
	
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
			pygame.draw.rect(surface, wheel_color, (body_x + 4, body_y - body_height - 1, 6, 3), border_radius=1)
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
	
		
		
		
		