import pygame

import car
import track

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

cars = car.Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

track = track.Track(SCREEN_WIDTH, SCREEN_HEIGHT)

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	keys = pygame.key.get_pressed()
	throttle = keys[pygame.K_UP] - keys[pygame.K_DOWN]
	steering = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
	
	screen.fill((0, 0, 0))

	cars.update(throttle, steering, 1/60)
	
	track.draw(screen)
	cars.draw(screen)

	pygame.display.flip()   # Update the display
	clock.tick(60)          # Limit the frame rate to 60 FPS
	