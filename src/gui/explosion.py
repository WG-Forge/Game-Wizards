import pygame
from src.constants import EXP_IMAGES


class Explosion(pygame.sprite.Sprite):

    def __init__(self, coordinates: tuple[int, int]):
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.images = [pygame.transform.scale(pygame.image.load(path).convert_alpha(), (21, 21)) for path in EXP_IMAGES]
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (coordinates[0], coordinates[1])

    def update(self):
        self.index += 0.001

        self.image = self.images[int(self.index)]

        # if the animation is complete, reset the index
        if self.index >= len(self.images) - 1:
            self.kill()
