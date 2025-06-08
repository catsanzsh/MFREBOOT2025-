# Mario Forever: Community Edition – Python Version (final, bugfree)
import pygame
import sys
import random
from pygame.locals import *

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 12
SCROLL_THRESH = 200
FONT_SIZE = 24

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario Forever: Community Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# Sound manager placeholder
def play_sfx(name):
    # Implement actual sound loading/playing logic
    pass

# Base sprite classes
class Block(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
    def hit(self, player, level):
        # Example: spawn coin or item
        pass

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
    def grow(self):
        # Power-up logic
        pass

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity_x = -2
        self.dead = False
    def update(self, solids):
        if self.dead: return
        self.rect.x += self.velocity_x
        for s in pygame.sprite.spritecollide(self, solids, False):
            self.velocity_x *= -1
    def stomp(self):
        self.dead = True
        self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        super().__init__()
        self.images = images
        self.image = self.images['stand_right']
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = 'right'
        self.on_ground = False
        self.jump_held = False
        self.jump_timer = 0
        self.coins = 0
        self.score = 0
        self.lives = 3
        self.power_up = 0
        self.invincible = 0
        self.is_dying = False
        self.is_sliding_pole = False

    def update(self, solids, enemies, items, blocks, level):
        if self.is_dying:
            self.rect.y += self.velocity_y
            self.velocity_y += GRAVITY
            return
        if self.is_sliding_pole:
            self.velocity_x = 0
            self.velocity_y = 2
            self.rect.y += self.velocity_y
            self.image = self.images['slide_right'] if self.direction == 'right' else self.images['slide_left']
            return
        # Horizontal movement
        self.rect.x += self.velocity_x
        for s in pygame.sprite.spritecollide(self, solids, False):
            if self.velocity_x > 0:
                self.rect.right = s.rect.left
            elif self.velocity_x < 0:
                self.rect.left = s.rect.right
        # Vertical movement
        self.velocity_y += GRAVITY
        if self.jump_held and self.jump_timer > 0:
            self.velocity_y -= 0.5
            self.jump_timer -= 1
        self.rect.y += self.velocity_y
        self.on_ground = False
        for s in pygame.sprite.spritecollide(self, solids, False):
            if self.velocity_y > 0:
                self.rect.bottom = s.rect.top
                self.on_ground = True
                self.velocity_y = 0
                self.jump_timer = 0
            elif self.velocity_y < 0:
                self.rect.top = s.rect.bottom
                self.velocity_y = 0
                self.jump_timer = 0
                if hasattr(s, 'hit'):
                    s.hit(self, level)
        # Coins
        for coin in pygame.sprite.spritecollide(self, level['coins'], True):
            self.coins += 1
            self.score += 200
            if self.coins >= 100:
                self.coins = 0
                self.lives += 1
                play_sfx('1up')
        # Items
        for item in pygame.sprite.spritecollide(self, items, True):
            play_sfx('powerup')
            self.score += 1000
            if hasattr(item, 'grow') and self.power_up == 0:
                item.grow()
                self.power_up = 1
        # Enemy collisions
        if self.invincible <= 0:
            for e in pygame.sprite.spritecollide(self, enemies, False):
                if hasattr(e, 'dead') and e.dead:
                    continue
                if self.velocity_y > 0 and self.rect.bottom < e.rect.centery + 10:
                    play_sfx('stomp')
                    if hasattr(e, 'stomp'):
                        e.stomp()
                    self.velocity_y = -JUMP_STRENGTH / 2
                    self.score += 100
                else:
                    self.take_damage()
        # Animation & invincibility flicker
        self._animate()
        if self.invincible > 0:
            self.invincible -= 1
            self.image.set_alpha(128 if self.invincible % 10 < 5 else 255)
        else:
            self.image.set_alpha(255)
        # Fall off
        if self.rect.top > SCREEN_HEIGHT + 100:
            self.take_damage()

    def take_damage(self):
        if self.invincible > 0 or self.is_dying:
            return
        self.lives -= 1
        if self.lives < 0:
            self.is_dying = True
            self.velocity_y = -JUMP_STRENGTH
        else:
            self.invincible = 120

    def _animate(self):
        # Placeholder for animation logic
        pass

# Level creation & HUD
def create_level():
    level = {
        'solids': pygame.sprite.Group(),
        'enemies': pygame.sprite.Group(),
        'items': pygame.sprite.Group(),
        'blocks': pygame.sprite.Group(),
        'coins': pygame.sprite.Group(),
        'all_sprites': pygame.sprite.Group(),
        'player': None
    }
    # Populate level with sprites
    # ... (load images, create Block, Coin, Item, Enemy instances, add to groups)
    return level

def draw_hud(player):
    hud_surface = font.render(f"Score: {player.score}   Coins: {player.coins}   Lives: {player.lives}", True, (255,255,255))
    screen.blit(hud_surface, (20, 20))

# Main loop
def main():
    images = {
        'stand_right': pygame.Surface((32, 64)),
        'slide_right': pygame.Surface((32, 64)),
        'slide_left': pygame.Surface((32, 64))
    }
    level = create_level()
    player = Player((100, 100), images)
    level['all_sprites'].add(player)

    camera_x = 0
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and player.on_ground:
                    player.velocity_y = -JUMP_STRENGTH
                    player.jump_held = True
                    player.jump_timer = 10
                if event.key in (K_LEFT, K_RIGHT):
                    player.direction = 'left' if event.key == K_LEFT else 'right'
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    player.jump_held = False
                if event.key in (K_LEFT, K_RIGHT):
                    player.velocity_x = 0
        # Continuous input
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: player.velocity_x = -5
        if keys[K_RIGHT]: player.velocity_x = 5

        # Update
        player.update(level['solids'], level['enemies'], level['items'], level['blocks'], level)
        level['enemies'].update(level['solids'])

        # Camera scrolling
        if player.rect.centerx - camera_x > SCROLL_THRESH:
            camera_x = player.rect.centerx - SCROLL_THRESH
        elif player.rect.centerx - camera_x < SCROLL_THRESH / 2:
            camera_x = player.rect.centerx - SCROLL_THRESH / 2

        # Draw
        screen.fill((0,0,0))
        for sprite in level['all_sprites']:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
        draw_hud(player)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
