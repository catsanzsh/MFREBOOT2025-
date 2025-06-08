# test_smb3.py
#
# A complete, runnable Pygame file demonstrating a player controller
# with physics and mechanics inspired by Super Mario Bros. 3.
#
# To run this, you need pygame: pip install pygame

import pygame

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SKY_BLUE = (105, 185, 255)

# --- SMB3-Inspired Player Physics Constants ---
GRAVITY = 0.5
MAX_FALL_SPEED = 10

# Horizontal Movement
ACCELERATION = 0.3
RUN_ACCELERATION = 0.5
FRICTION = 0.25

# Speeds
MAX_WALK_SPEED = 4
MAX_RUN_SPEED = 7

# Jumping
JUMP_FORCE = 11
RUNNING_JUMP_BOOST = 2  # Extra jump power when running
VARIABLE_JUMP_BOOST = 0.4 # Upward force applied when jump key is held
JUMP_TIMER_DURATION = 18 # How long the jump key can be held for extra height

# --- Stub Classes for Demonstration ---

class MockSprite(pygame.sprite.Sprite):
    """A base class for our visible game objects."""
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Solid(MockSprite):
    """Represents a simple, non-interactive solid platform."""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "darkgreen")

class QuestionBlock(MockSprite):
    """Represents an interactive block that can be hit from below, SMB3 style."""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "brown")
        self.original_y = y
        self.hit_timer = 0
        self.is_hit = False
        self._draw_initial_state()

    def _draw_initial_state(self):
        self.image.fill("orange")
        font = pygame.font.SysFont("Consolas", 30, bold=True)
        text = font.render("?", True, "black")
        text_rect = text.get_rect(center=self.image.get_rect().center)
        self.image.blit(text, text_rect)

    def hit(self, player):
        """Called when the player hits this block from below."""
        if self.is_hit:
            return # Can't hit an already empty block

        print("Player hit a Question Block! Coin!")
        self.image.fill("saddlebrown") # Change to "empty" block color
        self.hit_timer = 10 # Timer to animate a small bounce
        self.is_hit = True

    def update(self):
        """Update block's state, like a small bounce animation."""
        if self.hit_timer > 0:
            if self.hit_timer > 5:
                self.rect.y -= 2
            else:
                self.rect.y += 2
            self.hit_timer -= 1
        elif self.rect.y != self.original_y:
            self.rect.y = self.original_y

class Player(MockSprite):
    """The player character, with SMB3-inspired movement logic."""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 50, "cyan")

        # Physics attributes
        self.velocity_x = 0
        self.velocity_y = 0

        # State attributes
        self.on_ground = False
        self.running = False
        self.jump_held = False
        self.jump_timer = 0

    def update(self, keys, solids, blocks):
        """Main update method to handle all movement and state changes."""
        self._update_horizontal_movement(keys)
        self._update_vertical_movement(solids, blocks)

        # Visual feedback for running
        if self.running:
            self.image.fill("red")
        else:
            self.image.fill("cyan")

    def _update_horizontal_movement(self, keys):
        """Handles acceleration, friction, and running."""
        # Check for running state
        self.running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Determine current acceleration and max speed based on state
        accel = RUN_ACCELERATION if self.running else ACCELERATION
        max_speed = MAX_RUN_SPEED if self.running else MAX_WALK_SPEED

        # Apply acceleration based on key presses
        if keys[pygame.K_LEFT]:
            self.velocity_x -= accel
        if keys[pygame.K_RIGHT]:
            self.velocity_x += accel

        # Apply friction if no direction is held
        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            if self.velocity_x > FRICTION:
                self.velocity_x -= FRICTION
            elif self.velocity_x < -FRICTION:
                self.velocity_x += FRICTION
            else:
                self.velocity_x = 0

        # Cap speed
        if self.velocity_x > max_speed:
            self.velocity_x = max_speed
        if self.velocity_x < -max_speed:
            self.velocity_x = -max_speed

        # Apply horizontal movement
        self.rect.x += int(self.velocity_x)

    def _update_vertical_movement(self, solids, blocks):
        """Handles all vertical movement, gravity, and collision."""
        # --- 1. Update Velocity ---
        # Apply normal gravity
        self.velocity_y += GRAVITY
        # Cap fall speed
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED

        # SMB3-style variable jump height
        if self.jump_held and self.jump_timer > 0:
            self.velocity_y -= VARIABLE_JUMP_BOOST
            self.jump_timer -= 1

        # --- 2. Apply Vertical Movement & Check for Collisions ---
        self.rect.y += int(self.velocity_y)
        self.on_ground = False

        all_platforms = solids.sprites() + blocks.sprites()
        collided_platforms = [p for p in all_platforms if self.rect.colliderect(p.rect)]

        # --- 3. Resolve Collisions ---
        if collided_platforms:
            # Sort platforms based on player direction to handle the correct one first
            if self.velocity_y > 0:  # Moving DOWN
                collided_platforms.sort(key=lambda p: p.rect.top)
                landing_platform = collided_platforms[0]

                if self.rect.bottom > landing_platform.rect.top:
                    self.rect.bottom = landing_platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                    self.jump_timer = 0
            
            elif self.velocity_y < 0:  # Moving UP
                collided_platforms.sort(key=lambda p: p.rect.bottom, reverse=True)
                ceiling_platform = collided_platforms[0]

                if self.rect.top < ceiling_platform.rect.bottom:
                    self.rect.top = ceiling_platform.rect.bottom
                    self.velocity_y = 0
                    self.jump_timer = 0

                    # Check if the platform is interactive (has a 'hit' method)
                    if hasattr(ceiling_platform, 'hit'):
                        ceiling_platform.hit(self)

    def jump(self):
        """Initiates a jump."""
        if self.on_ground:
            self.velocity_y = -JUMP_FORCE
            # SMB3: Running jumps are higher!
            if self.running:
                self.velocity_y -= RUNNING_JUMP_BOOST
            
            self.jump_timer = JUMP_TIMER_DURATION
            self.on_ground = False

# --- Main Game Setup ---
def main():
    """Main game loop for demonstration."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SMB3 Physics - Arrows to Move, Space to Jump, L-Shift to Run")
    clock = pygame.time.Clock()

    # Create game objects
    player = Player(100, 500)
    
    solids = pygame.sprite.Group()
    solids.add(Solid(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
    solids.add(Solid(200, 450, 150, 20))
    solids.add(Solid(400, 350, 150, 20))
    solids.add(Solid(0, 200, 300, 20))

    blocks = pygame.sprite.Group()
    blocks.add(QuestionBlock(455, 250))
    blocks.add(QuestionBlock(495, 250))

    all_sprites = pygame.sprite.Group(player, solids, blocks)

    running = True
    while running:
        keys = pygame.key.get_pressed()
        
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                    player.jump_held = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.jump_held = False

        # --- Update ---
        player.update(keys, solids, blocks)
        blocks.update()

        # --- Drawing ---
        screen.fill(SKY_BLUE)
        all_sprites.draw(screen)
        pygame.display.flip()

        # --- Frame Rate ---
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
