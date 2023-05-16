import pygame
from src.constants import EXP_IMAGES


class Explosion(pygame.sprite.Sprite):
    __IMAGES = [pygame.transform.scale(pygame.image.load(path), (28, 28)) for path in EXP_IMAGES]

    def __init__(self, coordinates: tuple[int, int]):
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.image = Explosion.__IMAGES[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (coordinates[0], coordinates[1])
        self.counter = 0

    def update(self):
        # update explosion animation
        self.counter += 1

        if self.counter >= 1 and self.index < len(Explosion.__IMAGES) - 1:
            self.counter = 0
            self.index += 1
            self.image = Explosion.__IMAGES[self.index]

        # if the animation is complete, reset animation index
        if self.index >= len(Explosion.__IMAGES) - 1 and self.counter >= 1:
            self.kill()
