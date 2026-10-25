import random
import pygame
import math
import ctypes

from car import Car
import track
import menu_stuff

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CAR_STUCK_TIME = 4.0

car_count = 100
time_per_generation = 20.0

car_properties = {
	"drag": 0.3,
	"max_speed": 600,
	"max_reverse_speed": 80,
	"turn_rate": 7.0,
	"brake_force": 450,
	"accel": 150,
	"ray_count": 5,
	"fov": 120,
	"ray_length": 300,
	"grip": 18.0,
	"drift_grip": 7.5,
}

simulation_speed = 1
show_best_car = False
generation_count = 1
highest_fitness = 0.0
timer = time_per_generation

game_state = "start_menu"
last_game_state = "start_menu"
running = True
menu_cooldown = 0

pygame.init()
pygame.display.set_caption("CarSim")
icon = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.rect(icon, (220, 50, 50), (4, 8, 24, 16), border_radius=5)
pygame.draw.rect(icon, (180, 220, 255), (18, 10, 6, 12), border_radius=2)
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
try:
	hwnd = pygame.display.get_wm_info()["window"]
	ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
	r, g, b = 30, 30, 40
	colorref = r | (g << 8) | (b << 16)
	ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(ctypes.c_int(colorref)), 4)
except Exception:
	pass

clock = pygame.time.Clock()

font = pygame.font.SysFont("Consolas", 20)
title_font = pygame.font.SysFont("Consolas", 48)
menu_font = pygame.font.SysFont("Consolas", 24)

def create_start_menu_buttons():
	center_screen_x = SCREEN_WIDTH // 2
	btn_w, btn_h = 220, 44
	return [
		menu_stuff.Button((center_screen_x - btn_w // 2, 300, btn_w, btn_h), "Begin!", menu_font, "start"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 365, btn_w, btn_h), "Options", menu_font, "options"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 425, btn_w, btn_h), "Quit", menu_font, "quit"),
	]


def create_pause_menu_buttons():
	center_screen_x = SCREEN_WIDTH // 2
	btn_w, btn_h = 220, 44
	return [
		menu_stuff.Button((center_screen_x - btn_w // 2, 260, btn_w, btn_h), "Resume", menu_font, "resume"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 325, btn_w, btn_h), "Next Track", menu_font, "next_track"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 390, btn_w, btn_h), "Options", menu_font, "options"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 455, btn_w, btn_h), "Return to Menu", menu_font, "return_to_menu"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 520, btn_w, btn_h), "Quit", menu_font, "quit"),
	]


def create_options_menu_input_fields():
	center_screen_x = SCREEN_WIDTH // 2
	field_w, field_h = 220, 40
	return [
		menu_stuff.InputField((center_screen_x - field_w // 2, 240, field_w, field_h), str(car_count), menu_font, max_length=5, title="Car Count", key="car_count"),
		menu_stuff.InputField((center_screen_x - field_w // 2, 335, field_w, field_h), str(int(time_per_generation)), menu_font, max_length=5, title="Time per Generation (seconds)", key="time_per_generation"),
	]


def create_options_menu_buttons():
	center_screen_x = SCREEN_WIDTH // 2
	btn_w, btn_h = 220, 44
	left_x = center_screen_x - btn_w - 12
	right_x = center_screen_x + 12
	return [
		menu_stuff.Button((left_x, 420, btn_w, btn_h), "Reset", menu_font, "reset"),
		menu_stuff.Button((right_x, 420, btn_w, btn_h), "Show Rays", menu_font, "show_rays"),
		menu_stuff.Button((left_x, 485, btn_w, btn_h), "Save Brain", menu_font, "save_brain"),
		menu_stuff.Button((right_x, 485, btn_w, btn_h), "Load Brain", menu_font, "load_brain"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 550, btn_w, btn_h), "Car Options", menu_font, "car_options"),
		menu_stuff.Button((center_screen_x - btn_w // 2, 615, btn_w, btn_h), "Return", menu_font, "back"),
	]


def create_car_options_menu_input_fields():
	center_screen_x = SCREEN_WIDTH // 2
	field_w, field_h = 220, 40
	col1_x = center_screen_x - 380
	col2_x = center_screen_x - field_w // 2
	col3_x = center_screen_x + 160
	row1_y, row2_y, row3_y, row4_y = 220, 310, 400, 490
	return [
		menu_stuff.InputField((col1_x, row1_y, field_w, field_h), str(car_properties["drag"]), menu_font, max_length=5, title="Drag", key="drag", allow_decimals=True),
		menu_stuff.InputField((col2_x, row1_y, field_w, field_h), str(car_properties["max_speed"]), menu_font, max_length=5, title="Max Speed", key="max_speed"),
		menu_stuff.InputField((col3_x, row1_y, field_w, field_h), str(car_properties["max_reverse_speed"]), menu_font, max_length=5, title="Max Reverse Speed", key="max_reverse_speed"),
		menu_stuff.InputField((col1_x, row2_y, field_w, field_h), str(car_properties["accel"]), menu_font, max_length=5, title="Acceleration", key="accel"),
		menu_stuff.InputField((col2_x, row2_y, field_w, field_h), str(car_properties["brake_force"]), menu_font, max_length=5, title="Brake Force", key="brake_force"),
		menu_stuff.InputField((col3_x, row2_y, field_w, field_h), str(car_properties["turn_rate"]), menu_font, max_length=5, title="Turn Rate", key="turn_rate", allow_decimals=True),
		menu_stuff.InputField((col1_x, row3_y, field_w, field_h), str(car_properties["ray_count"]), menu_font, max_length=5, title="Ray Count", key="ray_count"),
		menu_stuff.InputField((col2_x, row3_y, field_w, field_h), str(car_properties["fov"]), menu_font, max_length=5, title="Field of View (degrees)", key="fov"),
		menu_stuff.InputField((col3_x, row3_y, field_w, field_h), str(car_properties["ray_length"]), menu_font, max_length=5, title="Ray Length", key="ray_length"),
		menu_stuff.InputField((col1_x, row4_y, field_w, field_h), str(car_properties["grip"]), menu_font, max_length=5, title="Grip", key="grip", allow_decimals=True),
		menu_stuff.InputField((col2_x, row4_y, field_w, field_h), str(car_properties["drift_grip"]), menu_font, max_length=5, title="Drift Grip", key="drift_grip", allow_decimals=True),
	]


def create_car_options_menu_buttons():
	center_screen_x = SCREEN_WIDTH // 2
	btn_w, btn_h = 220, 44
	return [
		menu_stuff.Button((center_screen_x - btn_w // 2, 580, btn_w, btn_h), "Return", menu_font, "back"),
	]

start_menu_buttons = create_start_menu_buttons()
pause_menu_buttons = create_pause_menu_buttons()
options_menu_input_fields = create_options_menu_input_fields()
options_menu_buttons = create_options_menu_buttons()
car_options_menu_input_fields = create_car_options_menu_input_fields()
car_options_menu_buttons = create_car_options_menu_buttons()

status_message = ""
status_timer = 0

current_track_index = 0
track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT, current_track_index)
skid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

def apply_car_properties(car_to_change):
	for key, value in car_properties.items():
		if key == "max_reverse_speed":
			value = -value
		car_to_change.change_properties(key, value)


def create_cars(car_count):
	cars = []
	for i in range(car_count):
		cars.append(Car(*track_object.get_start_pos()))
		cars[-1].laps_completed = 0
		apply_car_properties(cars[-1])
	return cars


cars = create_cars(car_count)


def apply_changes():
	global car_count, time_per_generation, cars, generation_count, timer, highest_fitness
	for field in options_menu_input_fields:
		if field.key == "car_count":
			car_count = field.get_number(car_count)
		elif field.key == "time_per_generation":
			time_per_generation = float(field.get_number(int(time_per_generation)))
	
	if len(cars) > car_count:
		cars = sorted(cars, key=lambda c: c.fitness, reverse=True)[:car_count]
	elif len(cars) < car_count:
		best_existing_car = max(cars, key=lambda c: c.fitness)
		while len(cars) < car_count:
			new_car = Car(*track_object.get_start_pos())
			new_car.laps_completed = 0
			apply_car_properties(new_car)
			new_car.brain = best_existing_car.brain.mutated_copy(mutation_rate=0.05)
			cars.append(new_car)
		for car in cars:
			car.reset(*track_object.get_start_pos())
		skid_surface.fill(0, 0, 0, 0)
		timer = time_per_generation
		highest_fitness = 0


def apply_car_changes():
	for field in car_options_menu_input_fields:
		car_properties[field.key] = field.get_number(car_properties[field.key])
	for car_to_change in cars:
		apply_car_properties(car_to_change)


while running:
	# Keybinds
	for event in pygame.event.get():
		if game_state == "options":
			for input_field in options_menu_input_fields:
				input_field.handle_event(event)
		if game_state == "car_options":
			for input_field in car_options_menu_input_fields:
				input_field.handle_event(event)
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				if game_state == "playing":
					game_state = "paused"
					break
				elif game_state == "paused":
					game_state = "playing"
					break
				elif game_state == "options":
					apply_changes()
					game_state = last_game_state
					break
				elif game_state == "car_options":
					apply_car_changes()
					game_state = "options"
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
		elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			if menu_cooldown > 0:
				continue
			if game_state == "paused":
				for button in pause_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "resume":
							game_state = "playing"
							break
						elif button.action == "next_track":
							current_track_index += 1
							track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT, current_track_index)
							for car in cars:
								car.reset(*track_object.get_start_pos())
							timer = time_per_generation
							highest_fitness = 0
							skid_surface.fill((0, 0, 0, 0))
							break
						elif button.action == "options":
							last_game_state = game_state
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
						elif button.action == "options":
							last_game_state = game_state
							game_state = "options"
							menu_cooldown = 10
							break
						elif button.action == "quit":
							running = False
							break
			elif game_state == "options":
				for button in options_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "reset":
							apply_changes()
							generation_count = 1
							timer = time_per_generation
							highest_fitness = 0.0
							cars = create_cars(car_count)
							status_message = "Reset cars"
							status_timer = 90
							skid_surface.fill((0, 0, 0, 0))
						elif button.action == "show_rays":
							for car in cars:
								car.show_rays = not car.show_rays
							if cars[0].show_rays:
								state_text = "ON"
							else:
								state_text = "OFF"
							button.text = f"Show Rays: {state_text}"
						elif button.action == "save_brain":
							best_car_to_save = max(cars, key=lambda c: c.fitness)
							best_car_to_save.brain.save("brain.npz")
							print("Saved best brain to brain.npz")
							status_message = "Saved the neural engine"
							status_timer = 90
						elif button.action == "load_brain":
							try:
								cars[0].brain.load("brain.npz")
								for car in cars[1:]:
									car.brain = cars[0].brain.mutated_copy(mutation_rate=0.05)
								for car in cars:
									car.reset(*track_object.get_start_pos())
								timer = time_per_generation
								print("Loaded brain from brain.npz")
								status_message = "Loaded the neural engine"
								status_timer = 90
								skid_surface.fill((0, 0, 0, 0))
							except FileNotFoundError:
								print("No saved brain.npz found yet!")
								status_message = "Loading failed D:"
								status_timer = 90
						elif button.action == "car_options":
							apply_changes()
							game_state = "car_options"
							menu_cooldown = 10
							break
						elif button.action == "back":
							apply_changes()
							game_state = last_game_state
							menu_cooldown = 10
							break
			elif game_state == "car_options":
				for button in car_options_menu_buttons:
					if button.is_clicked(event.pos):
						if button.action == "back":
							apply_car_changes()
							game_state = "options"
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
				# Laps
				if car.lap_completed:
					print("Lap completed: " + str(car.laps_completed + 1))
					car.laps_completed += 1
				
				total_checkpoints = car.next_checkpoint_index + car.laps_completed * len(track_object.checkpoints)
				
				previous_checkpoint = track_object.checkpoints[car.next_checkpoint_index - 1]
				next_checkpoint = track_object.checkpoints[car.next_checkpoint_index]
				segment_distance = math.hypot(next_checkpoint[0] - previous_checkpoint[0], next_checkpoint[1] - previous_checkpoint[1])
				distance_to_next_checkpoint = math.hypot(next_checkpoint[0] - car.x, next_checkpoint[1] - car.y)
				progress_fraction = max(0.0, min(1.0, 1.0 - (distance_to_next_checkpoint / max(1.0, segment_distance))))
				
				if total_checkpoints > 0:
					average_time = car.time_alive / total_checkpoints
					car.fitness = total_checkpoints + progress_fraction - (average_time * 0.1)
				else:
					car.fitness = progress_fraction - (car.time_alive * 0.1)
				
				# Update the car
				car.update(throttle, steering, 1 / 60)
				
				if car.is_drifting and car.alive:
					old_left, old_right = car.previous_rear_wheel_pos
					new_left, new_right = car.get_rear_wheel_pos()
					skid_color = (20, 20, 22, 75)
					pygame.draw.line(skid_surface, skid_color, old_left, new_left, 3)
					pygame.draw.line(skid_surface, skid_color, old_right, new_right, 3)
			
			# Car evolution
			if timer <= 0.0 or not any(car.alive for car in cars):
				cars_ranked_by_fitness = sorted(cars, key=lambda c: c.fitness, reverse=True)
				survivors = cars_ranked_by_fitness[:max(1, len(cars_ranked_by_fitness) // 8)]
				for i, car in enumerate(cars):
					if i < min(2, len(survivors)):
						car.brain = survivors[i].brain.copy()
					elif i < len(cars) // 2 and len(survivors) >= 2:
						p1, p2 = random.sample(survivors, 2)
						car.brain = p1.brain.crossover(p2.brain).mutated_copy(mutation_rate=0.1)
					else:
						parent_car = random.choice(survivors)
						car.brain = parent_car.brain.mutated_copy(mutation_rate=0.15)
					car.reset(*track_object.get_start_pos())
				skid_surface.fill((0, 0, 0, 0))
				timer = time_per_generation
				generation_count += 1
				print("Timer reset")
			timer -= 1 / 60
	
	# Drawing cars and track
	screen.fill((0, 0, 0))
	track_object.draw(screen)
	screen.blit(skid_surface, (0, 0))
	best_car = max(cars, key=lambda c: c.fitness)
	for car in cars:
		if show_best_car and car != best_car:
			continue
			# Maybe show the rays
		if car.show_rays:
			for i in range(car.ray_count):
				ray_angle = car.heading - car.fov / 2 + car.fov * (i / (car.ray_count - 1))
				distance = track_object.cast_ray(car.x, car.y, ray_angle, car.ray_length)
				end_x = car.x + math.cos(ray_angle) * distance
				end_y = car.y + math.sin(ray_angle) * distance
				pygame.draw.line(screen, (0, 0, 255), (car.x, car.y), (end_x, end_y), 1)
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
		screen.blit(text_surface, (16, 16 + i * 28))
	
	# Pause menu
	if game_state == "paused":
		pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		pause_overlay.set_alpha(180)
		pause_overlay.fill((0, 0, 0))
		screen.blit(pause_overlay, (0, 0))
		
		title_surface = title_font.render("PAUSED", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 200)))
		
		mouse_pos = pygame.mouse.get_pos()
		for button in pause_menu_buttons:
			button.draw(screen, mouse_pos)
	elif game_state == "start_menu":
		start_menu_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		start_menu_overlay.fill((85, 128, 85))
		screen.blit(start_menu_overlay, (0, 0))
		
		title_surface = title_font.render("CarSim", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 240)))
		
		mouse_pos = pygame.mouse.get_pos()
		for button in start_menu_buttons:
			button.draw(screen, mouse_pos)
	elif game_state == "options":
		options_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		options_overlay.fill((85, 128, 85))
		screen.blit(options_overlay, (0, 0))
		
		title_surface = title_font.render("Options", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 140)))
		
		for input_field in options_menu_input_fields:
			input_field.draw(screen)
		mouse_pos = pygame.mouse.get_pos()
		for button in options_menu_buttons:
			button.draw(screen, mouse_pos)
	elif game_state == "car_options":
		car_options_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		car_options_overlay.fill((85, 128, 85))
		screen.blit(car_options_overlay, (0, 0))
		
		title_surface = title_font.render("Car Options", True, (255, 255, 255))
		screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 140)))
		
		for input_field in car_options_menu_input_fields:
			input_field.draw(screen)
		mouse_pos = pygame.mouse.get_pos()
		for button in car_options_menu_buttons:
			button.draw(screen, mouse_pos)
	
	if status_timer > 0:
		status_timer -= 1
		message_surface = menu_font.render(status_message, True, (255, 240, 120))
		screen.blit(message_surface, message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))
	
	# Stuff
	pygame.display.flip()  # Update the display
	clock.tick(60)  # Limit the frame rate to 60 FPS
