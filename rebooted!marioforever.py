import pygame
import sys
import random
import os
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = 14
FPS = 60

# Colors
SKY_BLUE = (107, 140, 255)
GROUND_BROWN = (180, 122, 48)
BRICK_RED = (200, 76, 12)
BLOCK_YELLOW = (252, 188, 24)
PIPE_GREEN = (0, 168, 0)
COIN_YELLOW = (252, 216, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Create the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario Forever: Community Edition - Python Version")
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = {
            "stand_right": self.create_player_surface(True),
            "stand_left": self.create_player_surface(False),
            "walk_right": [self.create_player_surface(True, frame) for frame in range(1, 4)],
            "walk_left": [self.create_player_surface(False, frame) for frame in range(1, 4)],
            "jump_right": self.create_player_surface(True, jump=True),
            "jump_left": self.create_player_surface(False, jump=True)
        }
        
        self.image = self.images["stand_right"]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.direction = "right"
        self.walk_frame = 0
        self.walk_timer = 0
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.invincible = 0
        self.power_up = 0  # 0=small, 1=big, 2=fire
        
    def create_player_surface(self, facing_right=True, frame=0, jump=False):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Body color
        red = (228, 0, 0)
        blue = (0, 92, 196)
        skin = (252, 188, 176)
        brown = (140, 76, 0)
        
        # Draw Mario
        # Hat
        pygame.draw.rect(surface, red, (4, 2, 24, 8))
        pygame.draw.rect(surface, red, (2, 6, 28, 4))
        
        # Face
        pygame.draw.rect(surface, skin, (8, 10, 16, 14))
        
        # Eyes
        if facing_right:
            pygame.draw.rect(surface, WHITE, (16, 12, 4, 2))
            pygame.draw.rect(surface, WHITE, (16, 16, 4, 2))
            pygame.draw.rect(surface, BLACK, (17, 13, 2, 1))
            pygame.draw.rect(surface, BLACK, (17, 17, 2, 1))
        else:
            pygame.draw.rect(surface, WHITE, (8, 12, 4, 2))
            pygame.draw.rect(surface, WHITE, (8, 16, 4, 2))
            pygame.draw.rect(surface, BLACK, (9, 13, 2, 1))
            pygame.draw.rect(surface, BLACK, (9, 17, 2, 1))
        
        # Mustache
        pygame.draw.rect(surface, brown, (8, 18, 16, 2))
        
        # Overalls
        pygame.draw.rect(surface, blue, (4, 24, 24, 8))
        pygame.draw.rect(surface, blue, (8, 20, 16, 4))
        
        # Buttons
        pygame.draw.rect(surface, (252, 216, 0), (16, 22, 4, 4))
        
        # Arms
        pygame.draw.rect(surface, skin, (4, 24, 4, 4))
        pygame.draw.rect(surface, skin, (24, 24, 4, 4))
        
        # Legs
        if jump:
            # Jumping pose
            pygame.draw.rect(surface, red, (8, 32, 8, 4))
            pygame.draw.rect(surface, red, (16, 32, 8, 4))
        else:
            # Walking animation frames
            if frame == 0:  # Standing
                pygame.draw.rect(surface, red, (8, 32, 8, 4))
                pygame.draw.rect(surface, red, (16, 32, 8, 4))
            elif frame == 1:  # Mid step
                pygame.draw.rect(surface, red, (10, 32, 6, 4))
                pygame.draw.rect(surface, red, (16, 32, 8, 4))
            elif frame == 2:  # Other step
                pygame.draw.rect(surface, red, (8, 32, 8, 4))
                pygame.draw.rect(surface, red, (18, 32, 6, 4))
        
        if not facing_right:
            surface = pygame.transform.flip(surface, True, False)
            
        return surface
        
    def update(self, platforms, enemies, blocks, pipes, coins):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x
        
        # Keep player on screen horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Reset ground status
        self.on_ground = False
        
        # Check collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        
        # Check collisions with pipes
        for pipe in pipes:
            if self.rect.colliderect(pipe.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = pipe.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Jumping
                    self.rect.top = pipe.rect.bottom
                    self.velocity_y = 0
        # Check collisions with blocks
        block_hit = None
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.velocity_y < 0:  # Hitting from below
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0
                    block_hit = block
                elif self.velocity_y > 0:  # Landing on top
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
        
        # Handle block hit
        if block_hit:
            if block_hit.type == "brick" and self.power_up > 0:
                block_hit.break_block()
                self.score += 50
            elif block_hit.type == "question":
                block_hit.hit_block()
                if block_hit.content == "coin":
                    self.coins += 1
                    self.score += 200
                elif block_hit.content == "mushroom":
                    if self.power_up == 0:
                        self.power_up = 1
                    self.score += 1000
        
        # Check collisions with coins
        for coin in coins:
            if self.rect.colliderect(coin.rect):
                coin.collect()
                self.coins += 1
                self.score += 200
        
        # Check collisions with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.velocity_y > 0 and self.rect.bottom < enemy.rect.centery:  # Jumping on enemy
                    enemy.stomp()
                    self.velocity_y = -JUMP_STRENGTH / 1.5
                    self.score += 100
                else:  # Hit by enemy
                    if self.invincible <= 0:
                        if self.power_up > 0:
                            self.power_up -= 1
                            self.invincible = 60  # 1 second invincibility
                        else:
                            self.die()
        
        # Update animation
        self.walk_timer += 1
        if self.walk_timer > 5:
            self.walk_timer = 0
            self.walk_frame = (self.walk_frame + 1) % 3
        
        # Update sprite based on state
        if not self.on_ground:
            if self.direction == "right":
                self.image = self.images["jump_right"]
            else:
                self.image = self.images["jump_left"]
        else:
            if self.velocity_x == 0:
                if self.direction == "right":
                    self.image = self.images["stand_right"]
                else:
                    self.image = self.images["stand_left"]
            else:
                if self.direction == "right":
                    self.image = self.images["walk_right"][self.walk_frame]
                else:
                    self.image = self.images["walk_left"][self.walk_frame]
        
        # Update invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
            if self.invincible % 4 < 2:  # Flash effect
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
        
        # Game over if player falls off the bottom
        if self.rect.top > SCREEN_HEIGHT:
            return True  # Player died
        return False
    
    def die(self):
        self.lives -= 1
        self.rect.x = 100
        self.rect.y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.power_up = 0
        self.invincible = 120  # 2 seconds of invincibility after death
        
        # Return True if game over
        return self.lives <= 0
        
    def move_left(self):
        self.velocity_x = -PLAYER_SPEED
        self.direction = "left"
    
    def move_right(self):
        self.velocity_x = PLAYER_SPEED
        self.direction = "right"
    
    def stop(self):
        self.velocity_x = 0
    
    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH

# Block class
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type="brick", content="none"):
        super().__init__()
        self.type = block_type
        self.content = content
        self.hit_count = 0
        
        if block_type == "brick":
            self.image = self.create_brick()
        elif block_type == "question":
            self.image = self.create_question_block()
        elif block_type == "ground":
            self.image = self.create_ground_block()
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def create_brick(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(BRICK_RED)
        
        # Brick pattern
        pygame.draw.line(surface, (160, 60, 0), (0, 0), (TILE_SIZE, 0), 2)
        pygame.draw.line(surface, (160, 60, 0), (0, 0), (0, TILE_SIZE), 2)
        pygame.draw.line(surface, (240, 120, 60), (0, TILE_SIZE-1), (TILE_SIZE, TILE_SIZE-1), 2)
        pygame.draw.line(surface, (240, 120, 60), (TILE_SIZE-1, 0), (TILE_SIZE-1, TILE_SIZE), 2)
        
        # Brick texture
        for i in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (160, 60, 0), (i, 4), (i, TILE_SIZE-4), 1)
        
        return surface
    
    def create_question_block(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(BLOCK_YELLOW)
        
        # Block border
        pygame.draw.rect(surface, (200, 160, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        
        # Question mark
        pygame.draw.rect(surface, (180, 140, 0), (10, 8, 12, 4))
        pygame.draw.rect(surface, (180, 140, 0), (12, 12, 8, 4))
        pygame.draw.rect(surface, (180, 140, 0), (12, 20, 8, 4))
        pygame.draw.rect(surface, (180, 140, 0), (16, 16, 4, 4))
        
        return surface
    
    def create_ground_block(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(GROUND_BROWN)
        
        # Ground pattern
        pygame.draw.line(surface, (140, 92, 20), (0, 0), (TILE_SIZE, 0), 3)
        pygame.draw.line(surface, (140, 92, 20), (0, 0), (0, TILE_SIZE), 3)
        pygame.draw.line(surface, (220, 152, 76), (0, TILE_SIZE-1), (TILE_SIZE, TILE_SIZE-1), 3)
        pygame.draw.line(surface, (220, 152, 76), (TILE_SIZE-1, 0), (TILE_SIZE-1, TILE_SIZE), 3)
        
        # Ground texture
        for i in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (140, 92, 20), (i, 4), (i, TILE_SIZE-4), 1)
        
        return surface
    
    def hit_block(self):
        if self.type == "question" and self.hit_count == 0:
            self.hit_count += 1
            # Change to hit question block
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((180, 140, 0))
            pygame.draw.rect(self.image, (160, 120, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
            return True
        return False
    
    def break_block(self):
        if self.type == "brick":
            self.kill()
            return True
        return False

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, height=2):
        super().__init__()
        self.height = height  # Height in tiles
        self.image = pygame.Surface((TILE_SIZE * 1.5, TILE_SIZE * height))
        self.image.fill(PIPE_GREEN)
        
        # Pipe details
        pygame.draw.rect(self.image, (0, 140, 0), (0, 0, TILE_SIZE * 1.5, TILE_SIZE * height), 3)
        
        # Pipe rim
        pygame.draw.rect(self.image, (0, 200, 0), (0, 0, TILE_SIZE * 1.5, 8))
        pygame.draw.rect(self.image, (0, 120, 0), (0, 4, TILE_SIZE * 1.5, 4))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - (height - 1) * TILE_SIZE  # Adjust y position based on height

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
        
        # Draw coin
        pygame.draw.circle(self.image, COIN_YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4)
        pygame.draw.circle(self.image, (220, 180, 0), (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4 - 2)
        pygame.draw.circle(self.image, COIN_YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4 - 4)
        
        self.rect = self.image.get_rect()
        self.rect.x = x + TILE_SIZE//4
        self.rect.y = y + TILE_SIZE//4
        self.collected = False
        
    def collect(self):
        if not self.collected:
            self.collected = True
            self.kill()
            return True
        return False

# Goomba enemy class
class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walk_images = [
            self.create_goomba_surface(),
            self.create_goomba_surface(True)
        ]
        self.image = self.walk_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -1.5
        self.velocity_y = 0
        self.walk_timer = 0
        self.walk_frame = 0
        self.dead = False
        self.death_timer = 0
        
    def create_goomba_surface(self, frame2=False):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Body color
        brown = (180, 92, 0)
        dark_brown = (140, 60, 0)
        
        # Draw Goomba body
        pygame.draw.ellipse(surface, brown, (4, 8, 24, 20))
        
        # Draw Goomba head
        pygame.draw.ellipse(surface, dark_brown, (6, 4, 20, 12))
        
        # Draw eyes
        if frame2:
            pygame.draw.rect(surface, BLACK, (10, 8, 4, 4))
            pygame.draw.rect(surface, BLACK, (18, 8, 4, 4))
        else:
            pygame.draw.rect(surface, BLACK, (8, 8, 4, 4))
            pygame.draw.rect(surface, BLACK, (20, 8, 4, 4))
        
        # Draw feet
        pygame.draw.rect(surface, dark_brown, (6, 26, 6, 4))
        pygame.draw.rect(surface, dark_brown, (20, 26, 6, 4))
        
        return surface
        
    def update(self, platforms, pipes):
        if self.dead:
            self.death_timer += 1
            if self.death_timer > 30:  # Remove after 0.5 seconds
                self.kill()
            return
            
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x
        
        # Animation
        self.walk_timer += 1
        if self.walk_timer > 10:
            self.walk_timer = 0
            self.walk_frame = (self.walk_frame + 1) % 2
            self.image = self.walk_images[self.walk_frame]
        
        # Check collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
        
        # Check collisions with pipes
        for pipe in pipes:
            if self.rect.colliderect(pipe.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = pipe.rect.top
                    self.velocity_y = 0
        
        # Reverse direction if hitting a wall or edge
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity_x *= -1
        
        # Check if at edge of platform
        if self.velocity_x < 0:  # Moving left
            test_rect = pygame.Rect(self.rect.left - 2, self.rect.bottom, 2, 2)
        else:  # Moving right
            test_rect = pygame.Rect(self.rect.right, self.rect.bottom, 2, 2)
            
        on_ground = False
        for platform in platforms:
            if test_rect.colliderect(platform.rect):
                on_ground = True
                break
                
        for pipe in pipes:
            if test_rect.colliderect(pipe.rect):
                on_ground = True
                break
                
        if not on_ground:
            self.velocity_x *= -1
            
    def stomp(self):
        if not self.dead:
            self.dead = True
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (140, 60, 0), (0, 0, TILE_SIZE, TILE_SIZE // 2))
            self.rect.y += TILE_SIZE // 2

# Create level
def create_level():
    platforms = pygame.sprite.Group()
    pipes = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    
    # Create ground
    for x in range(0, SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
        platforms.add(Block(x, SCREEN_HEIGHT - TILE_SIZE, "ground"))
    
    # Create pipes
    pipes.add(Pipe(500, SCREEN_HEIGHT - TILE_SIZE, 3))
    pipes.add(Pipe(700, SCREEN_HEIGHT - TILE_SIZE, 2))
    
    # Create brick blocks
    for i in range(3):
        blocks.add(Block(200 + i * TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE * 3, "brick"))
    
    # Create question blocks
    blocks.add(Block(300, SCREEN_HEIGHT - TILE_SIZE * 5, "question", "coin"))
    blocks.add(Block(350, SCREEN_HEIGHT - TILE_SIZE * 5, "question", "mushroom"))
    
    # Create floating platforms
    for i in range(5):
        platforms.add(Block(400 + i * TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE * 4, "ground"))
    
    # Create coins
    coins.add(Coin(150, SCREEN_HEIGHT - TILE_SIZE * 4))
    coins.add(Coin(170, SCREEN_HEIGHT - TILE_SIZE * 4))
    coins.add(Coin(190, SCREEN_HEIGHT - TILE_SIZE * 4))
    
    # Create enemies
    enemies.add(Goomba(600, SCREEN_HEIGHT - TILE_SIZE * 2))
    enemies.add(Goomba(650, SCREEN_HEIGHT - TILE_SIZE * 2))
    
    return platforms, pipes, blocks, enemies, coins

# Draw HUD
def draw_hud(player):
    # Draw coins
    coin_surf = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2), pygame.SRCALPHA)
    pygame.draw.circle(coin_surf, COIN_YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4)
    pygame.draw.circle(coin_surf, (220, 180, 0), (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4 - 2)
    pygame.draw.circle(coin_surf, COIN_YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4 - 4)
    screen.blit(coin_surf, (20, 20))
    
    coin_text = font.render(f"× {player.coins}", True, WHITE)
    screen.blit(coin_text, (50, 20))
    
    # Draw score
    score_text = font.render(f"SCORE: {player.score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
    
    # Draw lives
    for i in range(player.lives):
        life_img = Player(0, 0).images["stand_right"]
        screen.blit(life_img, (20 + i * 40, 60))

# Main menu
def show_main_menu():
    screen.fill(SKY_BLUE)
    
    # Draw title
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("MARIO FOREVER", True, RED)
    subtitle = title_font.render("Community Edition", True, WHITE)
    
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 170))
    
    # Draw Mario and Goomba
    mario_img = Player(0, 0).images["stand_right"]
    screen.blit(mario_img, (SCREEN_WIDTH//2 - 100, 300))
    
    # Draw menu options
    menu_font = pygame.font.Font(None, 48)
    start_text = menu_font.render("Press ENTER to Start", True, WHITE)
    quit_text = menu_font.render("Press ESC to Quit", True, WHITE)
    
    screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 400))
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 450))
    
    pygame.display.flip()

# Game over screen
def show_game_over(score, coins):
    screen.fill(BLACK)
    
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("GAME  OVER", True, RED)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    
    score_font = pygame.font.Font(None, 48)
    score_text = score_font.render(f"Final Score: {score}", True, WHITE)
    coin_text = score_font.render(f"Coins Collected: {coins}", True, WHITE)
    
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
    screen.blit(coin_text, (SCREEN_WIDTH//2 - coin_text.get_width()//2, 300))
    
    restart_text = score_font.render("Press R to Restart", True, WHITE)
    menu_text = score_font.render("Press ESC for Menu", True, WHITE)
    
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 400))
    screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 450))
    
    pygame.display.flip()

# Level complete screen
def show_level_complete(score, coins):
    screen.fill(SKY_BLUE)
    
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("LEVEL COMPLETE!", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    
    flag_img = pygame.Surface((TILE_SIZE, TILE_SIZE * 3))
    flag_img.fill(RED)
    pygame.draw.rect(flag_img, WHITE, (0, 0, TILE_SIZE, TILE_SIZE * 3), 2)
    screen.blit(flag_img, (SCREEN_WIDTH//2 - TILE_SIZE//2, 250))
    
    score_font = pygame.font.Font(None, 48)
    score_text = score_font.render(f"Score: {score}", True, BLACK)
    coin_text = score_font.render(f"Coins: {coins}", True, BLACK)
    
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 350))
    screen.blit(coin_text, (SCREEN_WIDTH//2 - coin_text.get_width()//2, 400))
    
    restart_text = score_font.render("Press R to Restart", True, BLACK)
    menu_text = score_font.render("Press ESC for Menu", True, BLACK)
    
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 450))
    screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 500))
    
    pygame.display.flip()

# Main game loop
def main():
    running = True
    game_state = "menu"
    player = Player(100, SCREEN_HEIGHT - TILE_SIZE * 2)
    platforms, pipes, blocks, enemies, coins = create_level()
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if game_state == "menu":
                    if event.key == K_RETURN:
                        game_state = "playing"
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                        
                elif game_state == "playing":
                    if event.key == K_SPACE:
                        player.jump()
                        
                elif game_state == "game_over" or game_state == "level_complete":
                    if event.key == K_r:
                        game_state = "playing"
                        player = Player(100, SCREEN_HEIGHT - TILE_SIZE * 2)
                        platforms, pipes, blocks, enemies, coins = create_level()
                    if event.key == K_ESCAPE:
                        game_state = "menu"
                        
        if game_state == "menu":
            show_main_menu()
            
        elif game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                player.move_left()
            if keys[K_RIGHT]:
                player.move_right()
            if not keys[K_LEFT] and not keys[K_RIGHT]:
                player.stop()
                
            # Update game objects
            platforms.update()
            pipes.update()
            blocks.update()
            enemies.update(platforms, pipes)
            coins.update()
            player_died = player.update(platforms, enemies, blocks, pipes, coins)
            
            # Check for level completion (simplified)
            if player.rect.x > SCREEN_WIDTH:
                platforms, pipes, blocks, enemies, coins = create_level()
                player.rect.x = 100
                player.rect.y = SCREEN_HEIGHT - TILE_SIZE * 2
                player.score += 5000
                game_state = "level_complete"
                
            if player_died:
                if player.die():
                    game_state = "game_over"
                else:
                    platforms, pipes, blocks, enemies, coins = create_level()
            
            # Draw everything
            screen.fill(SKY_BLUE)
            platforms.draw(screen)
            pipes.draw(screen)
            blocks.draw(screen)
            coins.draw(screen)
            enemies.draw(screen)
            
            screen.blit(player.image, player.rect)
            draw_hud(player)
            
            pygame.display.flip()
            
        elif game_state == "game_over":
            show_game_over(player.score, player.coins)
            
        elif game_state == "level_complete":
            show_level_complete(player.score, player.coins)
            
        clock.tick(FPS)

if __name__ == "__main__":
    main()
