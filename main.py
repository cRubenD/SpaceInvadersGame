import pygame
import sys
from player import Player
from pygame.sprite import GroupSingle
import obstacle
from alien import Alien
from random import choice, randint
from laser import Laser
from alien import Extra


class Game:
    def __init__(self):
        player_sprite = Player((screen_width / 2, screen_height - 20), screen_width, 5)
        self.player = GroupSingle(player_sprite)

        # health and score setup
        self.lives = 3
        self.lives_surf = pygame.image.load("Sprites/space-invaders.png").convert_alpha()
        self.live_x_start_position = screen_width - (self.lives_surf.get_size()[0] * 3 + 20) - 25

        self.score = 0
        self.font = pygame.font.Font("freesansbold.ttf", 20)

        # obstacle setup
        self.shape = obstacle.shape
        self.blck_size = 6
        self.obstacle_amount = 4
        self.obstacle_x_position = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.blocks = pygame.sprite.Group()
        self.create_multiple_obstacles(*self.obstacle_x_position, x_start=screen_width / 15, y_start=480)

        # alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=6, cols=8)
        self.alien_direction = 1

        # extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        # Audio setup
        music = pygame.mixer.Sound("Audio/music.wav")
        music.set_volume(0.2)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound("Audio/laser.wav")
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound("Audio/explosion.wav")
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.blck_size + offset_x
                    y = y_start + row_index * self.blck_size
                    block = obstacle.Block(self.blck_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance=60, y_distance=48, x_offset=70, y_offset=100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('purple', x, y)
                else:
                    alien_sprite = Alien('green', x, y)
                self.aliens.add(alien_sprite)

    def alien_position_check(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            if alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), screen_width))
            self.extra_spawn_time = randint(400, 800)

    def collisions_checks(self):
        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()
                # extra collision
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 500
        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # player collision
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, True):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives):
            x = self.live_x_start_position + (live * self.lives_surf.get_size()[0] + 1)
            screen.blit(self.lives_surf, (x, 35))

    def display_score(self):
         score_surf = self.font.render(f"Score: {self.score}", False, 'white')
         score_rect = score_surf.get_rect(topleft = (35,35))
         screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render("You won", False, "white")
            victory_rect = victory_surf.get_rect(center  =(screen_width/2, screen_height/ 2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        # update all sprite groups
        # draw all sprite
        self.player.update()
        self.player.draw(screen)
        self.player.sprite.lasers.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.aliens.update(self.alien_direction)
        self.alien_position_check()
        self.alien_lasers.update()
        self.alien_lasers.draw(screen)
        self.extra_alien_timer()
        self.extra.draw(screen)
        self.extra.update()
        self.collisions_checks()
        self.display_lives()
        self.display_score()
        self.victory_message()

class CRT:
    def __init__(self):
        self.tv = pygame.image.load("Sprites/tv.png").convert_alpha()

    def draw(self):
        screen.blit(self.tv, (0, 0))

if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()

        screen.fill((30, 30, 30))
        game.run()
        crt.draw()
        pygame.display.flip()
        clock.tick(60)
