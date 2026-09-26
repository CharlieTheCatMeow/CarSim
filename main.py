import pygame
import math

import car
import track

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

car_count = 5

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT)
cars = []
for i in range(car_count):
	cars.append(car.Car(track_object.waypoints[0][0], track_object.waypoints[0][1], math.radians(-90)))
	cars[-1].laps_completed = 0

while running:
	# Keybinds
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	keys = pygame.key.get_pressed()
	throttle = keys[pygame.K_UP] - keys[pygame.K_DOWN]
	steering = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
	
	screen.fill((0, 0, 0))
	
	track_object.draw(screen)
	for car in cars:
		car.update(throttle, steering, 1/60)
		car.draw(screen)
		# Check if car is on track
		if not track_object.is_on_track(car.x, car.y):
			# Add point reduction system for AI later on
			pass
		# This is just to see the distance
		closest_point = track_object.closest_point(car.x, car.y)
		if closest_point:
			pygame.draw.line(screen, (255, 0, 0), (car.x, car.y), closest_point, 2)
		
		# Checkpoints and stuff
		car.next_checkpoint_index = track_object.count_checkpoints(car.x, car.y, car.next_checkpoint_index)[0]
		if track_object.count_checkpoints(car.x, car.y, car.next_checkpoint_index)[1]:
			car.laps_completed += 1

	#Stuff
	pygame.display.flip()   # Update the display
	clock.tick(60)          # Limit the frame rate to 60 FPS
	