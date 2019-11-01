from animate import Animate
from pygame.sprite import Sprite, Group, collide_rect
from pygame import image as pygimg
from pygame import time, transform


class Item(Sprite):
    MUSHROOM = 'mushroom'
    ONE_UP = '1-up'
    FIRE_FLOWER = 'fire-flower'
    STARMAN = 'starman'

    def __init__(self, x, y, image, speed, obstacles, floor, item_type, rise_from=None, animated=False):
        super(Item, self).__init__()
        if animated:
            self.animator = Animate(image)
            self.image = self.animator.get_image()
        else:
            self.animator = None
            self.image = image
        self.item_type = item_type
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.speed = speed
        self.jump_speed = 0
        self.obstacles = obstacles  # objects that the item may collide with
        self.floor = floor      # rects for the floor
        self.rise_from = rise_from

    def rise(self):
        if not self.rise_from:
            raise ValueError('Cannot rise from an object when that object is None')
        if self.rect.bottom <= self.rise_from.rect.top:
            self.rise_from = None
        else:
            self.rect.bottom -= 2

    def jump(self):
        if self.speed >= 0:
            self.jump_speed = -(self.speed * 5)
        else:
            self.jump_speed = (self.speed * 5)

    def flip_direction(self):
        # make the item go in the opposite direction
        self.speed = -self.speed
        self.rect.left += self.speed

    def bounce_off_obstacles(self):
        # checks if the item has hit any obstacles
        for obs in self.obstacles:
            pts = [obs.rect.bottomleft, obs.rect.midleft,
                   obs.rect.bottomright, obs.rect.midright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.flip_direction()
                    return
        for rect in self.floor:
            pts = [rect.midleft, rect.midright, rect.bottomleft, rect.bottomright]
            y_cap = rect.top
            for pt in pts:
                if self.rect.collidepoint(pt) or \
                        ((self.rect.left == rect.right or self.rect.right == rect.left) and self.rect.top > y_cap):
                    self.flip_direction()
                    return

    def fall(self):
        # makes the item fall through gaps in the ground
        falling = True
        for rect in self.floor:
            # check if bottom is at the top of the floor rect and that the x pos is within floor area
            if self.rect.bottom == rect.top and (rect.left < self.rect.center[0] < rect.right):
                self.rect.bottom = rect.top
                falling = False
                break
        if falling:
            for obj in self.obstacles:
                pts = [obj.rect.topleft, obj.rect.midtop, obj.rect.topright]
                for pt in pts:
                    if self.rect.collidepoint(pt):
                        falling = False
                        break
                if not falling:
                    break
        if falling:
            self.rect.bottom += abs(self.speed)

    def update(self):
        # updates item position
        if self.animator:
            self.image = self.animator.get_image()
        if not self.rise_from:
            if abs(self.jump_speed) > 0:
                self.rect.top += self.jump_speed
                self.jump_speed += 1    # simulate gravity reducing speed
            self.rect.left += self.speed
            self.bounce_off_obstacles()
            self.fall()
        else:
            self.rise()


class Mushroom(Item):
    # mushroom powerup
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        image = pygimg.load('images/mushroom.png')
        speed = 2
        super(Mushroom, self).__init__(x, y, image, speed, obstacles, floor,
                                       Item.MUSHROOM, rise_from, animated=False)


class OneUp(Item):
    # gives mario extra life
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        image = pygimg.load('images/mushroom-1-up.png')
        speed = 2
        super(OneUp, self).__init__(x, y, image, speed, obstacles, floor,
                                    Item.ONE_UP, rise_from, animated=False)


class FireFlower(Item):
    # gives mario fire powers
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('images/fire-flower-1.png'), pygimg.load('images/fire-flower-2.png'),
                  pygimg.load('images/fire-flower-3.png'), pygimg.load('images/fire-flower-4.png')]
        speed = 0
        super(FireFlower, self).__init__(x, y, images, speed, obstacles,
                                         floor, Item.FIRE_FLOWER, rise_from, True)


class StarMan(Item):
    # star item that gives invincibility for a few seconds
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('images/starman-1.png'), pygimg.load('images/starman-2.png'),
                  pygimg.load('images/starman-3.png'), pygimg.load('images/starman-4.png')]
        speed = 2
        self.last_jump = time.get_ticks()
        self.jump_interval = 1000   # jump around every second
        super(StarMan, self).__init__(x, y, images, speed, obstacles, floor, Item.STARMAN, rise_from, True)

    def update(self):
        touch_floor = False
        for rect in self.floor:
            if self.rect.bottom >= rect.top:
                self.rect.bottom = rect.top
                touch_floor = True
                break
        if abs(self.last_jump - time.get_ticks()) > self.jump_interval and touch_floor:
            self.jump()
            self.last_jump = time.get_ticks()
        super(StarMan, self).update()


class FireBall(Sprite):
    # sprite for the fireball
    def __init__(self, x, y, norm_images, explode_images, obstacles, floor, goomba, koopa, speed=5):
        self.norm_animator = Animate(norm_images)
        self.explode_animator = Animate(explode_images, repeat=False)
        self.image = self.norm_animator.get_image()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.obstacles = obstacles
        self.floor = floor
        self.goomba, self.koopa = goomba, koopa
        self.speed_x = speed
        self.speed_y = speed
        self.active = True
        super(FireBall, self).__init__()

    def check_hit_wall(self):
        # checks if fireball hits wall
        for obs in self.obstacles:
            pts = [obs.rect.midleft, obs.rect.midright, obs.rect.bottomleft, obs.rect.bottomright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.active = False
                    return
        for flr_rect in self.floor:
            pts = [flr_rect.midleft, flr_rect.midright, flr_rect.bottomleft, flr_rect.bottomright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.active = False
                    return

    def check_hit_enemies(self):
        # checks if fireball hits enemy
        for g_enemy in self.goomba:
            if collide_rect(self, g_enemy):
                g_enemy.kill()
                self.active = False
                return
        for k_enemy in self.koopa:
            if collide_rect(self, k_enemy):
                k_enemy.kill()
                self.active = False
                return

    def apply_gravity(self):
        # gravity to the fireball
        bounce = False
        for obs in self.obstacles:
            pts = [obs.rect.topleft, obs.rect.midtop, obs.rect.topright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    bounce = True
                    break
            if bounce:
                break
        if not bounce:
            for flr_rect in self.floor:
                # check if bottom is at the top of the floor rect and that the x pos is within floor area
                if self.rect.bottom >= flr_rect.top and (flr_rect.left < self.rect.center[0] < flr_rect.right):
                    bounce = True
                    break
        if bounce:
            self.speed_y = -abs(self.speed_y)   # ensure speed in y-direction is negative
        else:
            self.speed_y += 2   # apply gravity
        self.rect.y += self.speed_y

    def update(self):
        # updates position of fireball
        if self.active:
            self.rect.x += self.speed_x
            self.apply_gravity()
            self.image = self.norm_animator.get_image()
            self.check_hit_wall()
            self.check_hit_enemies()
        elif self.explode_animator.is_animation_done():
            self.kill()
        else:
            self.image = self.explode_animator.get_image()


class FireBallController:
    # controls fireballs
    def __init__(self, screen, map_group, obstacles, floor, origin, goomba, koopa):
        self.screen = screen
        self.origin = origin
        self.map_group = map_group
        self.obstacles = obstacles
        self.floor = floor
        self.goomba, self.koopa = goomba, koopa
        self.fireballs = Group()
        self.fb_images = [pygimg.load('images/super_mario_fireball_1.png'), pygimg.load('images/super_mario_fireball_2.png'),
                          pygimg.load('images/super_mario_fireball_3.png'), pygimg.load('images/super_mario_fireball_4.png')]
        self.exp_images = [pygimg.load('images/super_mario_fireball_explode_1.png'),
                           pygimg.load('images/super_mario_fireball_explode_2.png'),
                           pygimg.load('images/super_mario_fireball_explode_3.png')]
        self.fb_images = [transform.scale(img, (16, 16)) for img in self.fb_images]
        self.exp_images = [transform.scale(img, (16, 16)) for img in self.exp_images]

    def throw_fireball(self):
        # throws fireball if there are less than 2
        if len(self.fireballs) < 2:
            if self.origin.state_info['facing_right']:
                n_fireball = FireBall(self.origin.rect.topright[0], self.origin.rect.topright[1], self.fb_images,
                                      self.exp_images, self.obstacles, self.floor, self.goomba, self.koopa)
            else:
                n_fireball = FireBall(self.origin.rect.topleft[0], self.origin.rect.topleft[1], self.fb_images,
                                      self.exp_images, self.obstacles, self.floor, self.goomba, self.koopa, speed=-5)
            self.fireballs.add(n_fireball)
            self.map_group.add(n_fireball)
            return True
        return False

    def update_fireballs(self):
        # updates all fireballs
        self.fireballs.update()
        for fb in self.fireballs:
            if fb.rect.x < (self.origin.rect.x - self.screen.get_width()) or \
                fb.rect.x > (self.origin.rect.x + self.screen.get_width()) or \
                    (fb.rect.y < (self.origin.rect.y - self.screen.get_height()) or
                     fb.rect.y > (self.origin.rect.y + self.screen.get_height())):
                fb.kill()
