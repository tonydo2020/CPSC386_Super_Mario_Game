from configparser import ConfigParser
from eventLoop import EventLoop
from block import Block, CoinBlock, QuestionBlock
from pipe import Pipe
from coin import Coin
from decoration import Decoration
from maps import load_world_map
from mario import Mario
from enemy import Goomba, Koopa
from title import Menu
from items import Item
from gameStats import GameStats
import pygame


class Game:
    """Represents the game and its related methods for running"""
    def __init__(self):
        pygame.init()
        config = ConfigParser()     # parse settings file
        config.read('settings.ini')
        screen_size = (int(config['screen_settings']['width']),
                       int(config['screen_settings']['height']))
        self.screen = pygame.display.set_mode(screen_size)
        self.stats = GameStats(self.screen)
        pygame.display.set_caption(config['game_settings']['title'])
        self.clock = pygame.time.Clock()    # clock for limiting fps
        self.game_objects = None
        self.tmx_data = None
        self.map_layer = None
        self.map_group = None
        self.player_spawn = None
        self.mario = None
        self.timer = None
        self.time_warn = None
        self.last_tick = 0
        self.score = 0
        self.lives = 3
        self.coins = 0
        self.SFX = {
            '1-up': pygame.mixer.Sound('audio/1-Up.wav'),
            'warning': pygame.mixer.Sound('audio/Time-Warning.wav')
        }
        self.init_world()
        self.mario = Mario(self.game_objects, self.map_layer, self.map_group, self.screen)
        self.prep_enemies()
        self.mario.rect.x, self.mario.rect.y = self.player_spawn.x, self.player_spawn.y
        self.map_layer.center((self.mario.rect.x, self.mario.rect.y))   # center camera
        self.map_layer.zoom = 0.725     # camera zoom
        self.map_group.add(self.mario)   # add test sprite to map group
        self.paused = False
        # print(self.map_layer.view_rect.center)
        # action map for event loop
        self.paused = False
        self.game_active = False
        self.game_won = False
        self.menu = Menu(self.screen)
        self.action_map = {pygame.KEYDOWN: self.set_paused}
        print(self.map_layer.view_rect.center)

    def retrieve_map_data(self, data_layer_name):
        """Retrieve map data if it exists in the game's current map, otherwise return an empty list"""
        try:
            data = self.tmx_data.get_layer_by_name(data_layer_name)
        except ValueError:
            data = []
        return data

    def init_world(self, map_name='world1', spawn='player', reset=True):
        """Load the initial world for the game"""
        self.tmx_data, self.map_layer, self.map_group = load_world_map('map/' + map_name + '.tmx', self.screen)
        self.player_spawn = self.tmx_data.get_object_by_name(spawn)  # get player spawn object from map data
        self.init_game_objects()
        self.map_layer.center((self.player_spawn.x, self.player_spawn.y))
        self.map_layer.zoom = 0.725  # camera zoom
        if self.mario:
            self.map_group.add(self.mario)
            self.prep_enemies()
            self.mario.reset(self.map_layer, self.game_objects, reset)
            self.mario.rect.x, self.mario.rect.y = self.player_spawn.x, self.player_spawn.y

    def handle_pipe(self):
        """Handle Mario traveling through a pipe"""
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_DOWN] is 1:
            for pipe in self.game_objects['pipes']:
                if (pipe.destination and
                        self.mario.rect.left >= pipe.rect.left and self.mario.rect.right <= pipe.rect.right):
                    self.init_world(map_name=pipe.destination, spawn=pipe.spawn, reset=False)
                    self.mario.x, self.mario.y = self.player_spawn.x, self.player_spawn.y
                    pygame.mixer.music.load('audio/' + str(pipe.music))
                    pygame.mixer.music.play(-1)
        elif keys_pressed[pygame.K_RIGHT] is 1:
            for pipe in self.game_objects['pipes']:
                if (pipe.destination and pipe.horiz and self.mario.rect.right >= pipe.rect.left and
                        self.mario.rect.bottom <= pipe.rect.bottom):
                    self.init_world(map_name=pipe.destination, spawn=pipe.spawn, reset=False)
                    self.mario.x, self.mario.y = self.player_spawn.x, self.player_spawn.y
                    pygame.mixer.music.load('audio/' + str(pipe.music))
                    pygame.mixer.music.play(-1)

    def check_stage_clear(self):
        """Check if Mario has cleared the stage"""
        for rect in self.game_objects['win-zone']:
            if rect.colliderect(self.mario.rect):
                pygame.mixer.music.load('audio/End-Clear-Stage.wav')
                pygame.mixer.music.play()
                self.mario.flag_pole_sliding()
                self.game_won = True

    def init_game_objects(self):
        """Create all game objects in memory by extracting them from the map file"""
        self.game_objects = {
            'floors': [],
            'blocks': pygame.sprite.Group(),
            'q_blocks': pygame.sprite.Group(),
            'rubble': pygame.sprite.Group(),
            'coins': pygame.sprite.Group(),
            'pipes': pygame.sprite.Group(),
            'collide_objs': pygame.sprite.Group(),  # for checking collisions with all collide-able objects
            'flag': pygame.sprite.Group(),
            'items': pygame.sprite.Group(),
            'koopa': pygame.sprite.Group(),
            'goomba': pygame.sprite.Group(),
            'win-zone': []
        }
        floor_data = self.retrieve_map_data('walls')
        block_data = self.retrieve_map_data('blocks')
        q_block_data = self.retrieve_map_data('q-blocks')
        pipe_data = self.retrieve_map_data('pipes')
        coin_data = self.retrieve_map_data('coins')
        flag_data = self.retrieve_map_data('flag')
        background = self.retrieve_map_data('decorations')
        for obj in floor_data:  # walls represented as pygame Rects
            self.game_objects['floors'].append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        for block in block_data:
            if not block.properties.get('pipe', False):
                b_sprite = CoinBlock.coin_block_from_tmx_obj(block, self.screen, self.map_group, self.game_objects)
            else:
                b_sprite = Block(block.x, block.y, block.image, self.screen)
            self.map_group.add(b_sprite)    # draw using this group
            self.game_objects['blocks'].add(b_sprite)       # check collisions using this group
            self.game_objects['collide_objs'].add(b_sprite)
        for q_block in q_block_data:
            q_sprite = QuestionBlock.q_block_from_tmx_obj(q_block, self.screen, self.map_group, self.game_objects)
            self.map_group.add(q_sprite)    # draw using this group
            self.game_objects['q_blocks'].add(q_sprite)     # check collisions using this group
            self.game_objects['collide_objs'].add(q_sprite)
        for coin in coin_data:
            c_sprite = Coin(coin.x, coin.y, self.screen)
            self.map_group.add(c_sprite)
            self.game_objects['coins'].add(c_sprite)
        for pipe in pipe_data:
            p_sprite = Pipe.pipe_from_tmx_obj(pipe, self.screen)
            self.map_group.add(p_sprite)    # draw using this group
            self.game_objects['pipes'].add(p_sprite)        # check collisions using this group
            self.game_objects['collide_objs'].add(p_sprite)
        for flag_part in flag_data:
            if flag_part.image:
                f_sprite = Block(flag_part.x, flag_part.y, flag_part.image, self.screen)
                self.map_group.add(f_sprite)    # draw using this group
                self.game_objects['flag'].add(f_sprite)        # check collisions using this group
            else:
                self.game_objects['win-zone'].append(pygame.Rect(flag_part.x, flag_part.y,
                                                                 flag_part.width, flag_part.height))
        for bg in background:
            self.map_group.add(Decoration(bg.x, bg.y, bg.image))

    def prep_enemies(self):
        """Prepare the enemy sprites"""
        # may not be necessary if passing game_objects dictionary as a whole
        #  to Mario instead of passing individual groups
        enemy_spawn_data = self.retrieve_map_data('enemy-spawns')
        for spawn in enemy_spawn_data:
            if spawn.properties.get('e_type', 'goomba') == 'goomba':
                enemy = Goomba(self.screen, spawn.x, spawn.y, self.mario,
                               self.game_objects['floors'], self.game_objects['collide_objs'],
                               self.game_objects['goomba'], self.game_objects['koopa'])
                enemy.rect.y += 65 - enemy.rect.height
                self.game_objects['goomba'].add(enemy)
            else:
                enemy = Koopa(self.screen, spawn.x, spawn.y, self.mario,
                              self.game_objects['floors'], self.game_objects['collide_objs'],
                              self.game_objects['goomba'], self.game_objects['koopa'])
                enemy.rect.y += (65 - enemy.rect.height)
                print('Enemy rect begin:' + str(enemy.rect.y))
                self.game_objects['koopa'].add(enemy)
            self.map_group.add(enemy)

    def set_paused(self, event):
        """Set the game state to paused based on key press"""
        key = event.key
        if key == pygame.K_p:
            self.paused = not self.paused
            pygame.mixer.music.load('audio/Pause-Screen.wav')
            pygame.mixer.music.play()

    def update(self):
        """Update the screen and any objects that require individual updates"""
        if not self.paused and self.game_active:
            for block in self.game_objects['blocks']:
                points = block.check_hit(other=self.mario)
                if points:
                    self.score += points
                    self.coins += 1
            for q_block in self.game_objects['q_blocks']:
                points = q_block.check_hit(other=self.mario)
                if points:
                    self.score += points
                    self.coins += 1
            for coin in self.game_objects['coins']:
                if pygame.sprite.collide_rect(coin, self.mario):
                    self.score += coin.points
                    self.coins += 1
                    self.mario.SFX['coin'].play()
                    coin.kill()
            self.game_objects['blocks'].update()
            self.game_objects['rubble'].update()
            one_up_check = pygame.sprite.spritecollideany(self.mario, self.game_objects['items'])
            if one_up_check and one_up_check.item_type == Item.ONE_UP:
                self.lives += 1
                self.SFX['1-up'].play()
                one_up_check.kill()
            self.mario.update(pygame.key.get_pressed())  # update and check if not touching any walls
            self.handle_pipe()
            self.check_stage_clear()
            # print(self.mario.rect.x, self.mario.rect.y)
            self.game_objects['q_blocks'].update()
            self.game_objects['items'].update()
            self.game_objects['coins'].update()
            for goomba in self.game_objects['goomba']:
                goomba.update()
            for koopa in self.game_objects['koopa']:
                koopa.update()
        self.map_group.draw(self.screen)
        if not self.game_active:
            self.menu.blit()
        if self.game_active:
            self.stats.blit()
            self.check_timer()
        pygame.display.flip()

    def check_timer(self):
        """Check the game timer and update it if necessary"""
        if not self.paused:
            time = pygame.time.get_ticks()
            if time - self.last_tick > 600 and self.timer > 0:
                self.last_tick = time
                self.timer -= 1
            elif self.timer <= 100 and not self.time_warn:
                self.time_warn = True
                self.SFX['warning'].play()
            elif self.timer <= 0 and not self.mario.state_info['dead']:
                self.mario.start_death_jump()
        score = self.score + self.mario.score
        self.stats.update(str(score), str(self.coins), str('1-1'), str(self.timer), str(self.lives))

    def handle_player_killed(self):
        """Handle the player being killed in game"""
        self.lives -= 1
        if self.lives > 0:
            self.init_world()
            self.timer = 400
        else:
            self.game_active = False

    def run(self):
        """Run the application loop so that the menu can be displayed and the game started"""
        loop = EventLoop(loop_running=True, actions=self.menu.action_map)

        while True:
            loop.check_events()
            self.update()
            if self.menu.start:
                self.game_active = True
                self.timer = 400
                self.time_warn = False
                self.start_game()
                self.menu.start = False
                self.game_active = False
                self.game_won = False
                self.init_world()

    def start_game(self):
        """Launch the game and begin checking for events"""
        loop = EventLoop(loop_running=True, actions=self.action_map)
        self.score = 0
        self.lives = 3
        self.coins = 0

        while loop.loop_running and self.game_active:
            self.clock.tick(60)     # 60 fps cap
            loop.check_events()
            self.update()
            if self.mario.state_info['death_finish']:
                self.handle_player_killed()
            elif not pygame.mixer.music.get_busy() and self.game_won:
                self.menu.high_score.save(self.score)
                self.game_active = False
            elif not pygame.mixer.music.get_busy() and self.mario.state_info['dead']:
                pygame.mixer.music.load('audio/Mario-Die.wav')
                pygame.mixer.music.play()
            elif not pygame.mixer.music.get_busy() and not self.paused:
                pygame.mixer.music.load('audio/BG-Main.wav')
                pygame.mixer.music.play(-1)


if __name__ == '__main__':
    game = Game()
    game.run()