import random
import pygame
import math

import car
import track

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

car_count = 100
simulation_speed = 1
timer = 5.0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT)
start_x, start_y = track_object.checkpoints[0]

cars = []
for i in range(car_count):
    cars.append(car.Car(start_x, start_y, math.radians(0)))
    cars[-1].laps_completed = 0

while running:
	# Keybinds
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_1:
				simulation_speed = 1
			elif event.key == pygame.K_2:
				simulation_speed = 5
			elif event.key == pygame.K_3:
				simulation_speed = 15
			elif event.key == pygame.K_4:
				simulation_speed = 30
	screen.fill((0, 0, 0))
	
	track_object.draw(screen)
	for _ in range(simulation_speed):
		for car in cars:
			# Check if car is on track
			if not track_object.is_on_track(car.x, car.y):
				car.alive = False
				# Add point reduction system for AI later on
				pass
			
			# This is just to see the distance
			closest_point = track_object.closest_point(car.x, car.y)
			
			# Reinforcement learning stuff?
			car_inputs = car.get_inputs(car.cast_rays(track_object, car.ray_count, car.fov, car.ray_length), track_object)
			throttle, steering = car.brain.think(car_inputs)
			
			# Checkpoints and stuff
			car.next_checkpoint_index, car.lap_completed = track_object.count_checkpoints(car.x, car.y, car.next_checkpoint_index)
			# Fitness because cars have to be fit
			car.fitness = car.next_checkpoint_index + car.laps_completed * len(track_object.checkpoints)
			
			if car.lap_completed:
				print("Lap completed: " + str(car.laps_completed + 1))
				car.laps_completed += 1
				
			# Drive and draw the car
			if not car.alive:
				continue
			car.update(throttle, steering, 1 / 60)
			car.draw(screen)
		
		# Car evolution
		if timer <= 0.0 or not any(car.alive for car in cars):
			cars_ranked_by_fitness = sorted(cars, key=lambda c: c.fitness, reverse=True)
			survivors = cars_ranked_by_fitness[:max(1, len(cars_ranked_by_fitness) // 8)]
			for i, car in enumerate(cars):
				if i == 0:
					car.brain = survivors[i].brain.copy()
				else:
					parent_car = random.choice(survivors)
					car.brain = parent_car.brain.mutated_copy(mutation_rate=0.1)
				car.reset(track_object.checkpoints[0][0], track_object.checkpoints[0][1], math.radians(0))
			timer = 5.0
			print("Timer reset")
		timer -= 1/60

	#Stuff
	pygame.display.flip()   # Update the display
	clock.tick(60)          # Limit the frame rate to 60 FPS
	