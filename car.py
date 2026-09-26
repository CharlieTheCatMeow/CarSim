import math
import pygame

class Car:
	def __init__(self, x, y, heading = 0.0):
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		
		self.drag = 0.5
		self.max_speed = 400
		self.max_reverse_speed = -80
		self.turn_rate = 4.0
		self.brake_force = 450.0
		self.accel = 250.0
		
		self.length, self.width = 34, 18
		self.alive = True
		self.laps_completed = 0
		self.next_checkpoint_index = 0
		
	def reset(self, x, y, heading = 0.0):
		self.x, self.y = x, y
		self.heading = heading
		self.speed = 0.0
		self.alive = True
		
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
		
	def draw(self, screen, color = (0, 155, 155)):
		surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
		surface.fill(color)
		rotated = pygame.transform.rotate(surface, -math.degrees(self.heading))
		screen.blit(rotated, rotated.get_rect(center=(self.x, self.y)))
	
		
		
		
		