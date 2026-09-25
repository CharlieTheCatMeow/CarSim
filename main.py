import pygame

import car
import track

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

track_object = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT)
cars = car.Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	keys = pygame.key.get_pressed()
	throttle = keys[pygame.K_UP] - keys[pygame.K_DOWN]
	steering = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
	
	screen.fill((0, 0, 0))

	cars.update(throttle, steering, 1/60)
	
	track_object.draw(screen)
	cars.draw(screen)
	
	if not track_object.is_on_track(cars.x, cars.y):
		# Add point reduction system for AI later on
		print("Car left the track >:(")
		
	# This is just to let me see the distance
	closest_point = track_object.closest_point(cars.x, cars.y)
	if closest_point:
		pygame.draw.line(screen, (255, 0, 0), (cars.x, cars.y), closest_point, 2)
	
	#Stuff
	pygame.display.flip()   # Update the display
	clock.tick(60)          # Limit the frame rate to 60 FPS
	