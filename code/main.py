import pygame
import sys
from support import import_folder, enemy_import_folder


# PLAYER CONTROLS
# Movement = A, D
# Jump = W
# Attack = Q

# ENEMY CONTROLS
# Movement = Left, Right
# Jump = Up
# Attack = RTCTRL


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.import_character_assets()
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100
        self.alive = True
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [pos_x, pos_y]

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        # player status
        self.status = 'idle'
        self.facing_right = True

    def import_character_assets(self):
        character_path = '../character/'
        self.animations = {'idle': [], 'attack': [], 'jump': [], 'run': [], 'hurt': [], 'death': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flip_img = pygame.transform.flip(image, True, False)
            self.image = flip_img

    def move(self, screen_width, screen_height, surface, target):
        GRAVITY = 0.2
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()

        # player movement
        if keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        else:
            self.direction.x = 0

        # player jump
        if keys[pygame.K_w]:
            self.player_jump()

        # player attack
        if keys[pygame.K_q]:
            self.player_attack(surface, target)

        # apply player gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width - 75:
            self.vel_y = 0
            dy = screen_height

        # ensure player doesn't fall through the screen
        if self.rect.bottom + dy > screen_height - 75:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 75 - self.rect.bottom

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    def player_attack(self, surface, target):
        self.attacking = True
        attacking_rect = pygame.Rect(self.rect.centerx - 235, self.rect.y, self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.health -= 0.1
            target.status = 'hurt'

    def player_gravity(self):
        dy = 0
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def player_jump(self):
        self.direction.y = self.jump_speed

    def player_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

            # player death animation
            if self.animations['death'] and self.health <= 0:
                self.frame_index = len(self.animations['death']) - 1
                self.status = 'death'
                enemy_win()

        # attack animation
        key = pygame.key.get_pressed()
        if key[pygame.K_q]:
            self.status = 'attack'

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.animate()
        self.move(screen_width, screen_height, screen, enemy)
        self.player_gravity()
        self.player_status()
        self.rect.x += self.direction.x * self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.import_enemy_assets()
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.health = 100
        self.alive = True
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomright = [pos_x, pos_y]

        # enemy movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        # enemy status
        self.status = 'idle'
        self.facing_right = True

    def import_enemy_assets(self):
        character_path = '../enemy/'
        self.animations = {'idle': [], 'attack': [], 'cast': [], 'walk': [], 'hurt': [], 'death': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = enemy_import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flip_img = pygame.transform.flip(image, True, False)
            self.image = flip_img

    def move(self, screen_width, screen_height, surface, target):
        GRAVITY = 0.2
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()

        # player movement
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = True
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = False
        else:
            self.direction.x = 0

            # enemy jump
            if keys[pygame.K_UP]:
                self.enemy_jump()

            # enemy attack
            if keys[pygame.K_RCTRL]:
                self.enemy_attack(surface, target)

        # apply enemy gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure enemy stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width - 75:
            self.vel_y = 0
            dy = screen_height

        # ensure enemy doesn't fall through the screen
        if self.rect.bottom + dy > screen_height - 75:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 75 - self.rect.bottom

        # update enemy position
        self.rect.x += dx
        self.rect.y += dy

    def enemy_attack(self, surface, target):
        self.attacking = True
        attacking_rect = pygame.Rect(self.rect.centerx - 235, self.rect.y, self.rect.width, self.rect.height)
        if attacking_rect.colliderect(target.rect):
            target.health -= 0.1
            target.status = 'hurt'

    def enemy_gravity(self):
        dy = 0
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def enemy_jump(self):
        self.direction.y = self.jump_speed

    def enemy_status(self):
        if self.direction.y < 0:
            self.status = 'cast'
        else:
            if self.direction.x != 0:
                self.status = 'walk'
            else:
                self.status = 'idle'

            # enemy death animation
            if self.animations['death'] and self.health <= 0:
                self.frame_index = len(self.animations['death']) - 1
                self.status = 'death'
                player_win()

        # attack animation
        key = pygame.key.get_pressed()
        if key[pygame.K_RCTRL]:
            self.status = 'attack'

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.animate()
        self.move(screen_width, screen_height, screen, player)
        self.enemy_gravity()
        self.enemy_status()
        self.rect.x += self.direction.x * self.speed


# initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# create screen dimensions
screen_width = 1280
screen_height = 700

# create display screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('1st Game :)')

# create frame rate
clock = pygame.time.Clock()
FPS = 60

# define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# define font
font = pygame.font.Font('../Font/PoetsenOne-Regular.ttf', 100)

# load images
bg = pygame.image.load('../PNG/cyberpunk-street.png')
bg_scale = pygame.transform.scale(bg, (1280, 700))

# load music
main_fx = pygame.mixer.Sound('../music/cyberpunk-street.wav')
main_fx.set_volume(0.5)


# function for health bars
def health_bars(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 5, y - 5, 410, 40))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 400 * ratio, 30))


# function for enemy win
def enemy_win():
    game_over_text = font.render("Game Over! You Lose :(", True, (200, 200, 200))
    screen.blit(game_over_text, (100, 250))


# function for player win
def player_win():
    game_over_text = font.render("Game Over! You Win :)", True, (200, 200, 200))
    screen.blit(game_over_text, (100, 250))


# create player and enemy instances
player = Player(0, 650)
enemy = Enemy(1280, 650)

# game loop
run = True
while run:

    # locks frame rate
    clock.tick(FPS)
    main_fx.play()

    # draws bg
    screen.blit(bg_scale, (0, 0))

    # draw player and enemy stats
    health_bars(player.health, 20, 20)
    health_bars(enemy.health, 860, 20)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # updates display window and sprites
    player.move(screen_width, screen_height, screen, enemy)
    enemy.move(screen_width, screen_height, screen, player)

    # draw player and enemy
    player.draw()
    enemy.draw()

    # update player and enemy
    player.update()
    enemy.update()

    # updates display
    pygame.display.update()

pygame.quit()
sys.exit()
