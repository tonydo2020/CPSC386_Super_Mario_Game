from animate import Animate
from pygame.sprite import Sprite


class Coin(Sprite):
    def __init__(self, x, y, screen, points=100):
        super(Coin, self).__init__()
        images = ['images/Coin-1.png', 'images/Coin-2.png', 'images/Coin-3.png', 'images/Coin-4.png']
        self.animator = Animate(images)
        self.image = self.animator.get_image()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.screen = screen
        self.points = points

    def update(self):
        self.image = self.animator.get_image()

    def blit(self):
        self.screen.blit(self.image, self.rect)
