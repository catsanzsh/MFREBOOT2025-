# test.py
#
# A complete, runnable Pygame file demonstrating the fixed and improved
# vertical movement logic.
#
# To run this, you need pygame: pip install pygame

import pygame

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Player Physics Constants ---
GRAVITY = 0.35
MAX_FALL_SPEED = 10
GROUND_POUND_SPEED = 12

# --- Stub Classes and Functions for Demonstration ---

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

class Block(MockSprite):
    """Represents an interactive block that can be hit from below."""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "brown")
        self.original_y = y
        self.hit_timer = 0

    def hit(self, player):
        """Called when the player hits this block from below."""
        print("Player hit a Block!")
        self.image.fill("orange") # Change color to show it was hit
        self.hit_timer = 10 # Timer to animate a small bounce

    def update(self):
        """Update block's state, like a small bounce animation."""
        if self.hit_timer > 0:
            # Animate a simple bounce up and down
            if self.hit_timer > 5:
                self.rect.y -= 1
            else:
                self.rect.y += 1
            self.hit_timer -= 1
        elif self.rect.y != self.original_y:
            self.rect.y = self.original_y # Return to original position
            self.image.fill("brown") # Reset color


class Player(MockSprite):
    """The player character, containing the new movement logic."""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 50, "cyan")

        # Movement attributes
        self.velocity_y = 0
        self.on_ground = False
        self.jump_held = False
        self.jump_timer = 0  # For variable jump height
        self.ground_pounding = False
        self.spin_jumping = False

    ### --- THE REFACTORED AND FIXED FUNCTION --- ###
    def _update_vertical_movement(self, solids, blocks):
        """
        Handles all vertical movement, gravity, and collision.

        This improved version unifies collision handling, resolves collisions
        more robustly, and decouples interactions for more flexible design.
        """
        # --- 1. Update Velocity ---
        # Handle ground pound state first (overrides normal gravity)
        if self.ground_pounding and not self.on_ground:
            self.velocity_y = GROUND_POUND_SPEED
            self._create_ground_pound_particles()
        else:
            # Apply normal gravity
            self.velocity_y += GRAVITY
            # Cap fall speed to a maximum
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED

            # Allow for variable jump height by reducing velocity while jump is held
            if self.jump_held and self.jump_timer > 0:
                self.velocity_y -= 0.6  # This creates an upward boost
                self.jump_timer -= 1

        # --- 2. Apply Vertical Movement & Check for Collisions ---
        # Move the rect based on the new velocity. Using int() is good practice.
        self.rect.y += int(self.velocity_y)

        # Assume we are in the air until a collision proves otherwise
        self.on_ground = False

        # Combine all collidable platforms into a single list for one check
        all_platforms = solids.sprites() + blocks.sprites()
        collided_platforms = [p for p in all_platforms if self.rect.colliderect(p.rect)]

        # --- 3. Resolve Collisions ---
        if collided_platforms:
            if self.velocity_y > 0:  # Player is moving DOWN
                # Sort platforms by their top edge to find the highest one we're landing on
                collided_platforms.sort(key=lambda p: p.rect.top)
                landing_platform = collided_platforms[0]

                # Resolve the collision by placing the player on top
                self.rect.bottom = landing_platform.rect.top
                self.on_ground = True

                # Handle landing effects (e.g., ground pound impact)
                if self.ground_pounding:
                    self._create_ground_pound_impact()
                    self.ground_pounding = False

                # Reset all vertical motion states upon landing
                self.velocity_y = 0
                self.jump_timer = 0
                self.spin_jumping = False

            elif self.velocity_y < 0:  # Player is moving UP
                # Sort platforms by their bottom edge to find the lowest one we're hitting
                collided_platforms.sort(key=lambda p: p.rect.bottom, reverse=True)
                ceiling_platform = collided_platforms[0]

                # Resolve collision by placing player below
                self.rect.top = ceiling_platform.rect.bottom
                self.velocity_y = 0  # Stop upward movement
                self.jump_timer = 0  # Cancel variable jump boost

                # NEW: Check if this platform is interactive (has a 'hit' method)
                # This is a flexible way to handle interactions without caring about the object's class
                if hasattr(ceiling_platform, 'hit'):
                    ceiling_platform.hit(self)

    # --- Player action methods (for demonstration) ---
    def jump(self):
        if self.on_ground:
            self.velocity_y = -10  # Apply initial jump speed
            self.jump_timer = 20   # Set timer for how long the jump button can be held for a boost
            self.on_ground = False

    def ground_pound(self):
        if not self.on_ground and not self.ground_pounding:
            self.ground_pounding = True
            self.velocity_y = 0 # Reset velocity before pound

    def _create_ground_pound_particles(self):
        """Stub method for particle effects."""
        # print("Creating ground pound particles...")
        pass

    def _create_ground_pound_impact(self):
        """Stub method for impact effects on landing."""
        print("GROUND POUND IMPACT!")


# --- Main Game Setup ---
def main():
    """Main game loop for demonstration."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Physics Test - Use Arrows, Space to Jump, Down Arrow in air to Ground Pound")
    clock = pygame.time.Clock()

    # Create game objects
    player = Player(100, 500)
    
    solids = pygame.sprite.Group()
    solids.add(Solid(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)) # Floor
    solids.add(Solid(200, 450, 150, 20))
    solids.add(Solid(400, 350, 150, 20))

    blocks = pygame.sprite.Group()
    blocks.add(Block(455, 250)) # An interactive block

    all_sprites = pygame.sprite.Group(player, solids, blocks)

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                    player.jump_held = True
                if event.key == pygame.K_DOWN:
                    player.ground_pound()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.jump_held = False

        # --- Horizontal Movement (simple) ---
        keys = pygame.key.get_pressed()
        player.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5

        # --- Update ---
        player._update_vertical_movement(solids, blocks)
        blocks.update() # Update the blocks for their animations

        # --- Drawing ---
        screen.fill("black")
        all_sprites.draw(screen)
        pygame.display.flip()

        # --- Frame Rate ---
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
