import random
import pygame
import math

from car import Car
import track
import menu_stuff

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CAR_STUCK_TIME = 4.0

car_count = 100
time_per_generation = 20.0

simulation_speed = 1
show_best_car = False
generation_count = 1
highest_fitness = 0.0
timer = time_per_generation

game_state = "start_menu"
running = True
menu_cooldown = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Consolas", 20)
title_font = pygame.font.SysFont("Consolas", 48)
menu_font = pygame.font.SysFont("Consolas", 24)

def create_start_menu_buttons():
	center_screen_x = SCREEN_WIDTH / 2
	return [
		menu_stuff.Button((center_screen_x - 100, 340, 200, 40), "Begin!", menu_font, "start"),
		menu_stuff.Button((center_screen_x - 100, 400, 200, 40), "Quit", menu_font, "quit"),
	]

def create_pause_menu_buttons():
	center_screen_x = SCREEN_WIDTH / 2
	return [
		menu_stuff.Button((center_screen_x - 100, 340, 200, 40), "Resume", menu_font, "resume"),
		menu_stuff.Button((center_screen_x - 100, 410, 200, 40), "Options", menu_font, "options"),
		menu_stuff.Button((center_screen_x - 100, 480, 200, 40), "Return to Menu", menu_font, "return_to_menu"),
		menu_stuff.Button((center_screen_x - 100, 550, 200, 40), "Quit", menu_font, "quit")
	]

def create_options_menu_input_fields():
	center_screen_x = SCREEN_WIDTH / 2
	return [
		menu_stuff.InputField((center_screen_x - 100, 340, 200, 40), str(car_count), menu_font, max_length=5, title="Car Count", key="car_count"),
	]

def create_options_menu_buttons():
	center_screen_x = SCREEN_WIDTH / 2
	return [
		menu_stuff.Button((center_screen_x - 100, 410, 200, 40), "Return", menu_font, "back"),
	]

start_menu_buttons = create_start_menu_buttons()
pause_menu_buttons = create_pause_menu_buttons()
options_menu_input_fields = create_options_menu_input_fields()
options_menu_buttons = create_options_menu_buttons()

track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT)
start_x, start_y = track_object.checkpoints[0]

cars = []
for i in range(car_count):
	cars.append(Car(start_x, start_y, math.radians(0)))
	cars[-1].laps_completed = 0

def apply_changes():
	global car_count, time_per_generation, cars, generation_count, timer, highest_fitness
	for field in options_menu_input_fields:
		if field.key == "car_count":
			car_count = field.get_number(car_count)
		elif field.key == "time_per_generation":
			time_per_generation = float(field.get_number(int(time_per_generation)))
	
	if len(cars) > car_count:
		cars = cars[:car_count]
	else:
		while len(cars) < car_count:
			new_car = Car(start_x, start_y, math.radians(0))
			new_car.laps_completed = 0
			cars.append(new_car)

while running:
	# Keybinds
	for event in pygame.event.get():
		if game_state == "options":
			for input_field in options_menu_input_fields:
				input_field.handle_event(event)
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				if game_state == "playing":
					game_state = "paused"
					break
				else:
					game_state = "playing"
					break
			elif game_state == "playing":
				if event.key == pygame.K_1:
					simulation_speed = 1
				elif event.key == pygame.K_2:
					simulation_speed = 5
				elif event.key == pygame.K_3:
					simulation_speed = 15
				elif event.key == pygame.K_4:
					simulation_speed = 40
				elif event.key == pygame.K_h:
					show_best_car = not show_best_car
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if menu_cooldown > 0:
				continue
			if game_state == "paused":
				for button in pause_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "resume":
							game_state = "playing"
							break
						elif button.action == "options":
							game_state = "options"
							break
						elif button.action == "return_to_menu":
							game_state = "start_menu"
							menu_cooldown = 10
							break
						elif button.action == "quit":
							running = False
							break
			elif game_state == "start_menu":
				for button in start_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "start":
							game_state = "playing"
							menu_cooldown = 10
							break
						elif button.action == "quit":
							running = False
							break
			elif game_state == "options":
				for button in options_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "back":
							apply_changes()
							game_state = "paused"
							menu_cooldown = 10
							break
	if menu_cooldown > 0:
		menu_cooldown -= 1
	
	if game_state == "playing":
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
					car.fitness = (car.next_checkpoint_index + car.laps_completed * len(
						track_object.checkpoints) - average_time_per_checkpoint * 0.1)
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
			timer -= 1 / 60
	
	# Drawing cars and track
	screen.fill((0, 0, 0))
	track_object.draw(screen)
	best_car = max(cars, key=lambda c: c.fitness)
	for car in cars:
		if show_best_car and car != best_car:
			continue
		if car is best_car:
			car.draw(screen, (255, 0, 0))
		else:
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
		text_surface = font.render(line, True, (255, 255, 255))
		screen.blit(text_surface, (10, 10 + i * 30))
	
	# Pause menu
	if game_state == "paused":
		pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		pause_overlay.set_alpha(180)
		pause_overlay.fill((0, 0, 0))
		screen.blit(pause_overlay, (0, 0))
	
		title_surface = title_font.render("PAUSED", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 260)))
		
		mouse_pos = pygame.mouse.get_pos()
		for button in pause_menu_buttons:
			button.draw(screen, mouse_pos)
	elif game_state == "start_menu":
		start_menu_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		start_menu_overlay.fill((85, 128, 85))
		screen.blit(start_menu_overlay, (0, 0))
		
		title_surface = title_font.render("CarSim", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 260)))
		
		mouse_pos = pygame.mouse.get_pos()
		for button in create_start_menu_buttons():
			button.draw(screen, mouse_pos)
	elif game_state == "options":
		options_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		options_overlay.fill((85, 128, 85))
		screen.blit(options_overlay, (0, 0))
		
		title_surface = title_font.render("Options", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 260)))
		
		for input_field in options_menu_input_fields:
			input_field.draw(screen)
		mouse_pos = pygame.mouse.get_pos()
		for button in options_menu_buttons:
			button.draw(screen, mouse_pos)

	#Stuff
	pygame.display.flip()  # Update the display
	clock.tick(60)  # Limit the frame rate to 60 FPS
