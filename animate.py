from pygame import image, time


class Animate:
    def __init__(self, image_list, delay=150, repeat=True):
        self.images = []
        for image_file in image_list:
            if isinstance(image_file, str):     # needs to be loaded
                self.images.append(image.load(image_file))
            else:       # already loaded
                self.images.append(image_file)
        self.image_index = 0
        self.last_frame = time.get_ticks()
        self.frame_delay = delay
        self.repeat = repeat
        self.done = False

    def reset(self):
        self.image_index = 0

    def is_animation_done(self):
        if self.repeat:
            return True
        return self.done

    def get_image(self):
        next_frame = abs(self.last_frame - time.get_ticks()) > self.frame_delay
        if next_frame and self.repeat:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.last_frame = time.get_ticks()
        elif next_frame and not self.image_index >= len(self.images) - 1:
            self.image_index += 1
            self.last_frame = time.get_ticks()
        elif next_frame and not self.repeat:
            self.done = True
        return self.images[self.image_index]
