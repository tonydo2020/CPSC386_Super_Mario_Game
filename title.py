from pygame import image, sprite, font, K_RETURN, KEYDOWN
import json


class Logo(sprite.Sprite):
    # logo on title screen
    def __init__(self, screen):
        self.screen = screen
        self.image = image.load('images/Super-Mario-Logo.png')
        self.rect = self.image.get_rect()
        self.position()
        super(Logo, self).__init__()

    def position(self):
        # position the logo on the screen
        self.rect.centerx = int(self.screen.get_width() * 0.5)
        self.rect.centery = int(self.screen.get_height() * 0.4)

    def blit(self):
        self.screen.blit(self.image, self.rect)


class TextDisplay(sprite.Sprite):
    # text on the title screen
    def __init__(self, x, y, text, screen, size=24):
        self.text = text
        self.font = font.Font('fonts/PressStart2P-Regular.ttf', size)
        self.screen = screen
        self.x_pos, self.y_pos = x, y
        self.image = None
        self.rect = None
        self.render()
        super(TextDisplay, self).__init__()

    def update(self, n_text):
        self.text = str(n_text)
        self.render()

    def render(self):
        self.image = self.font.render(self.text, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.x_pos, self.y_pos

    def blit(self):
        self.screen.blit(self.image, self.rect)


class HighScore(sprite.Sprite):
    def __init__(self, x, y, screen):
        self.score = None
        self.retrieve()
        text = 'High Score - ' + str(self.score)
        self.display = TextDisplay(x, y, text, screen)
        super(HighScore, self).__init__()

    def save(self, n_score):
        if int(n_score) > self.score:
            with open('high_score.json', 'w') as outfile:
                json.dump(n_score, outfile)
            self.score = n_score
            text = 'High Score - ' + str(self.score)
            self.display.update(text)

    def retrieve(self):
        try:
            with open('high_score.json', 'r') as infile:
                self.score = int(json.load(infile))
        except (FileNotFoundError, ValueError):
            self.score = 0

    def blit(self):
        self.display.blit()


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.logo = Logo(screen)
        start_text_x, start_text_y = int(screen.get_width() * 0.5), int(screen.get_height() * 0.7)
        self.start_text = TextDisplay(start_text_x, start_text_y, 'Press Enter', screen)
        hs_x, hs_y = int(screen.get_width() * 0.5), int(screen.get_height() * 0.85)
        self.high_score = HighScore(hs_x, hs_y, screen)
        self.action_map = {KEYDOWN: self.check_start, }
        self.start = False

    def check_start(self, event):
        key = event.key
        if key == K_RETURN:
            self.start = True

    def blit(self):
        self.logo.blit()
        self.start_text.blit()
        self.high_score.blit()
