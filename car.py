import math
import pygame

class Car:
	def __init__(self, x, y, heading = 0.0):
		# Things that change
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		
		# Stats
		self.drag = 0.5
		self.max_speed = 400
		self.max_reverse_speed = -80
		self.turn_rate = 4.0
		self.brake_force = 450.0
		self.accel = 250.0
		
		# Ray casting stuff
		self.ray_count = 5
		self.fov = math.radians(120)
		self.ray_length = 200
		
		# Also things that change but not really
		self.length, self.width = 34, 18
		self.alive = True
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		
	def reset(self, x, y, heading = 0.0):
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		self.alive = True
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		
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
	
	# Draw the car
	def draw(self, screen, color = (0, 155, 155)):
		surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
		surface.fill(color)
		rotated = pygame.transform.rotate(surface, -math.degrees(self.heading))
		screen.blit(rotated, rotated.get_rect(center=(self.x, self.y)))
	
		
		
		
		