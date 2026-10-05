import random
import pygame
import math

import car
import track

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

CAR_STUCK_TIME = 4.0

car_count = 100
simulation_speed = 1
time_per_generation = 20.0
timer = time_per_generation

highest_fitness = 0.0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont("Consolas", 20)
generation_count = 1

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
	
	for _ in range(simulation_speed):
		for car in cars:
			if not car.alive:
				continue
			# Check if car is on track
			if not track_object.is_on_track(car.x, car.y):
				car.alive = False
				# Add point reduction system for AI later on
				pass
			
			# Reinforcement learning stuff?
			car_inputs = car.get_inputs(car.cast_rays(track_object, car.ray_count, car.fov, car.ray_length), track_object)
			throttle, steering = car.brain.think(car_inputs)
			
			# Checkpoints and stuff
			previous_checkpoint_index = car.next_checkpoint_index
			car.next_checkpoint_index, car.lap_completed = track_object.count_checkpoints(car.x, car.y, car.next_checkpoint_index)
			if previous_checkpoint_index != car.next_checkpoint_index:
				car.time_since_last_checkpoint = 0.0
			else:
				pass
			if car.time_since_last_checkpoint > CAR_STUCK_TIME:
				car.alive = False
			
			# Fitness because cars have to be fit
			if car.next_checkpoint_index > 0:
				average_time_per_checkpoint = car.time_alive / car.next_checkpoint_index
				car.fitness = (car.next_checkpoint_index + car.laps_completed * len(track_object.checkpoints) - average_time_per_checkpoint * 0.1)
			else:
				car.fitness = -car.time_alive
			
			# Laps
			if car.lap_completed:
				print("Lap completed: " + str(car.laps_completed + 1))
				car.laps_completed += 1
				
			# Update the car
			car.update(throttle, steering, 1 / 60)
		
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
			timer = time_per_generation
			generation_count += 1
			print("Timer reset")
		timer -= 1/60
	
	# Drawing cars and track
	screen.fill((0, 0, 0))
	track_object.draw(screen)
	for car in cars:
		car.draw(screen)
	
	# HUD
	cars_alive_count = sum(1 for car in cars if car.alive)
	best_fitness = max((car.fitness for car in cars), default=0.0)
	if best_fitness > highest_fitness:
		highest_fitness = best_fitness
	HUD_lines = [
		f"Generation: {generation_count}",
		f"Cars Alive: {cars_alive_count} / {len(cars)}",
		f"Best Fitness: {best_fitness:.1f}",
		f"Highest Fitness: {highest_fitness:.1f}",
		f"Timer: {max(0.0, timer):.1f}",
		f"Simulation Speed (press 1, 2, 3 or 4): {simulation_speed}x"
	]
	
	for i, line in enumerate(HUD_lines):
		text_surface = font.render(line, True, (0, 0, 0))
		screen.blit(text_surface, (10, 10 + i * 30))
	
	#Stuff
	pygame.display.flip()   # Update the display
	clock.tick(60)          # Limit the frame rate to 60 FPS
	