from pygame.sprite import Sprite


class Decoration(Sprite):
    # Sprite for the background
    def __init__(self, x, y, image):
        super(Decoration, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
