#!/usr/bin/env python3
"""
2D Arcade-Style Space Shooter Game
A survival-based space shooter where players destroy meteors for points within a 60-second time limit.
Features power-ups, lives system, and real-time scoring.
"""

import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION = 60  # seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

class Player:
    """Player spaceship class handling movement, shooting, and collision detection"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.double_score = False
        self.double_score_timer = 0
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.laser_beam = False
        self.laser_beam_timer = 0
        self.time_slow = False
        self.time_slow_timer = 0
        self.mega_bullets = False
        self.mega_bullets_timer = 0
        self.last_shot = 0
        self.shot_cooldown = 250  # milliseconds
        
    def update(self):
        """Update player state including power-up timers"""
        current_time = pygame.time.get_ticks()
        
        # Update power-up timers
        if self.invincible and current_time - self.invincible_timer > 5000:
            self.invincible = False
            
        if self.rapid_fire and current_time - self.rapid_fire_timer > 5000:
            self.rapid_fire = False
            
        if self.double_score and current_time - self.double_score_timer > 5000:
            self.double_score = False
            
        if self.triple_shot and current_time - self.triple_shot_timer > 7000:
            self.triple_shot = False
            
        if self.laser_beam and current_time - self.laser_beam_timer > 4000:
            self.laser_beam = False
            
        if self.time_slow and current_time - self.time_slow_timer > 6000:
            self.time_slow = False
            
        if self.mega_bullets and current_time - self.mega_bullets_timer > 5000:
            self.mega_bullets = False
    
    def move(self, direction):
        """Move player left or right within screen bounds"""
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def shoot(self):
        """Create bullets based on current power-ups"""
        current_time = pygame.time.get_ticks()
        cooldown = 100 if self.rapid_fire else self.shot_cooldown
        
        if current_time - self.last_shot > cooldown:
            self.last_shot = current_time
            bullets = []
            
            if self.laser_beam:
                # Create laser beam (continuous beam)
                bullets.append(LaserBeam(self.x + self.width // 2, self.y))
            elif self.triple_shot:
                # Create three bullets
                bullets.append(Bullet(self.x + self.width // 2, self.y, angle=0, mega=self.mega_bullets))
                bullets.append(Bullet(self.x + self.width // 2 - 10, self.y, angle=-15, mega=self.mega_bullets))
                bullets.append(Bullet(self.x + self.width // 2 + 10, self.y, angle=15, mega=self.mega_bullets))
            else:
                # Single bullet
                bullets.append(Bullet(self.x + self.width // 2, self.y, mega=self.mega_bullets))
            
            return bullets
        return []
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Draw the player spaceship"""
        # Main body (blue triangle)
        points = [
            (self.x + self.width // 2, self.y),  # Top point
            (self.x, self.y + self.height),      # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        pygame.draw.polygon(screen, BLUE, points)
        
        # Engine glow (orange rectangle at bottom)
        engine_rect = pygame.Rect(self.x + 10, self.y + self.height - 5, self.width - 20, 8)
        pygame.draw.rect(screen, ORANGE, engine_rect)
        
        # Shield effect if invincible
        if self.invincible:
            pygame.draw.circle(screen, CYAN, 
                             (self.x + self.width // 2, self.y + self.height // 2), 
                             30, 3)

class Meteor:
    """Meteor class for falling obstacles"""
    
    def __init__(self, x, y, size_type="large"):
        self.x = x
        self.y = y
        self.size_type = size_type
        
        if size_type == "large":
            self.width = 40
            self.height = 40
            self.speed = random.uniform(1, 3)
            self.points = 10
        else:  # small
            self.width = 20
            self.height = 20
            self.speed = random.uniform(2, 4)
            self.points = 10
            
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self, time_slow=False):
        """Update meteor position and rotation"""
        speed_multiplier = 0.3 if time_slow else 1.0
        self.y += self.speed * speed_multiplier
        self.rotation += self.rotation_speed * speed_multiplier
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """Check if meteor has fallen off screen"""
        return self.y > SCREEN_HEIGHT
    
    def draw(self, screen):
        """Draw the meteor with rotation effect"""
        # Create a surface for the meteor
        meteor_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw meteor shape (irregular polygon)
        if self.size_type == "large":
            color = GRAY
            # Large meteor - more irregular shape
            points = [
                (self.width * 0.5, 0),
                (self.width * 0.8, self.height * 0.3),
                (self.width, self.height * 0.7),
                (self.width * 0.6, self.height),
                (self.width * 0.2, self.height * 0.8),
                (0, self.height * 0.4)
            ]
        else:
            color = (160, 160, 160)
            # Small meteor - simpler shape
            points = [
                (self.width * 0.5, 0),
                (self.width, self.height * 0.4),
                (self.width * 0.7, self.height),
                (self.width * 0.3, self.height),
                (0, self.height * 0.6)
            ]
        
        pygame.draw.polygon(meteor_surface, color, points)
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(meteor_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        screen.blit(rotated_surface, rotated_rect)

class Bullet:
    """Bullet class for player projectiles"""
    
    def __init__(self, x, y, angle=0, mega=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.mega = mega
        
        if mega:
            self.width = 8
            self.height = 16
            self.speed = 10
            self.damage = 2
        else:
            self.width = 4
            self.height = 10
            self.speed = 8
            self.damage = 1
            
        # Calculate velocity based on angle
        self.vx = math.sin(math.radians(angle)) * self.speed
        self.vy = -math.cos(math.radians(angle)) * self.speed
    
    def update(self, time_slow=False):
        """Update bullet position"""
        speed_multiplier = 0.3 if time_slow else 1.0
        self.x += self.vx * speed_multiplier
        self.y += self.vy * speed_multiplier
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """Check if bullet has left screen"""
        return self.y < 0 or self.x < 0 or self.x > SCREEN_WIDTH
    
    def draw(self, screen):
        """Draw the bullet"""
        if self.mega:
            # Mega bullet - larger with glow effect
            pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, YELLOW, (self.x + 1, self.y + 1, self.width - 2, self.height - 2))
        else:
            # Normal bullet
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))

class LaserBeam:
    """Laser beam class for continuous damage"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 6
        self.height = SCREEN_HEIGHT
        self.speed = 0  # Laser doesn't move
        self.damage = 5
        self.lifetime = 200  # milliseconds
        self.created_time = pygame.time.get_ticks()
        
    def update(self, time_slow=False):
        """Laser beam doesn't move, just tracks lifetime"""
        pass
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x - self.width // 2, 0, self.width, self.y)
    
    def is_off_screen(self):
        """Check if laser beam should be removed"""
        return pygame.time.get_ticks() - self.created_time > self.lifetime
    
    def draw(self, screen):
        """Draw the laser beam"""
        # Main laser beam
        pygame.draw.rect(screen, RED, (self.x - self.width // 2, 0, self.width, self.y))
        # Inner bright core
        pygame.draw.rect(screen, WHITE, (self.x - 2, 0, 4, self.y))
        # Outer glow effect
        for i in range(3):
            alpha = 50 - i * 15
            glow_surface = pygame.Surface((self.width + i * 4, self.y))
            glow_surface.set_alpha(alpha)
            glow_surface.fill(RED)
            screen.blit(glow_surface, (self.x - (self.width + i * 4) // 2, 0))

class PowerUp:
    """Power-up class for special abilities"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed = 2
        self.type = random.choice([
            "rapid_fire", "shield", "double_score", 
            "triple_shot", "laser_beam", "time_slow", "mega_bullets"
        ])
        self.glow_timer = 0
        
        # Set color based on type
        color_map = {
            "rapid_fire": RED,
            "shield": CYAN,
            "double_score": GREEN,
            "triple_shot": PURPLE,
            "laser_beam": (255, 0, 255),  # Magenta
            "time_slow": (0, 255, 255),   # Bright cyan
            "mega_bullets": ORANGE
        }
        self.color = color_map.get(self.type, WHITE)
    
    def update(self):
        """Update power-up position and glow effect"""
        self.y += self.speed
        self.glow_timer += 1
    
    def get_rect(self):
        """Return collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """Check if power-up has fallen off screen"""
        return self.y > SCREEN_HEIGHT
    
    def draw(self, screen):
        """Draw the power-up with glowing effect"""
        # Pulsing glow effect
        glow_intensity = abs(math.sin(self.glow_timer * 0.2)) * 10 + 5
        
        # Draw outer glow
        pygame.draw.circle(screen, self.color, 
                         (self.x + self.width // 2, self.y + self.height // 2), 
                         self.width // 2 + int(glow_intensity), 0)
        
        # Draw main capsule
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))
        
        # Draw type indicator
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.type == "rapid_fire":
            # Draw bullets symbol
            pygame.draw.circle(screen, RED, (center_x, center_y - 3), 2)
            pygame.draw.circle(screen, RED, (center_x, center_y + 3), 2)
        elif self.type == "shield":
            # Draw shield symbol
            pygame.draw.circle(screen, CYAN, (center_x, center_y), 6, 2)
        elif self.type == "double_score":
            # Draw "2X" symbol
            font = pygame.font.Font(None, 16)
            text = font.render("2X", True, GREEN)
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)
        elif self.type == "triple_shot":
            # Draw three lines for triple shot
            pygame.draw.line(screen, PURPLE, (center_x - 6, center_y - 6), (center_x - 6, center_y + 6), 2)
            pygame.draw.line(screen, PURPLE, (center_x, center_y - 6), (center_x, center_y + 6), 2)
            pygame.draw.line(screen, PURPLE, (center_x + 6, center_y - 6), (center_x + 6, center_y + 6), 2)
        elif self.type == "laser_beam":
            # Draw laser symbol
            pygame.draw.line(screen, (255, 0, 255), (center_x, center_y - 8), (center_x, center_y + 8), 3)
        elif self.type == "time_slow":
            # Draw clock symbol
            pygame.draw.circle(screen, (0, 255, 255), (center_x, center_y), 6, 2)
            pygame.draw.line(screen, (0, 255, 255), (center_x, center_y), (center_x, center_y - 4), 2)
            pygame.draw.line(screen, (0, 255, 255), (center_x, center_y), (center_x + 3, center_y), 2)
        elif self.type == "mega_bullets":
            # Draw large bullet symbol
            pygame.draw.rect(screen, ORANGE, (center_x - 3, center_y - 6, 6, 12))

class Explosion:
    """Simple explosion effect for collisions"""
    
    def __init__(self, x, y, size="small"):
        self.x = x
        self.y = y
        self.size = size
        self.timer = 0
        self.max_timer = 20
        self.particles = []
        
        # Create explosion particles
        particle_count = 15 if size == "large" else 8
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(10, 20)
            })
    
    def update(self):
        """Update explosion animation"""
        self.timer += 1
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def is_finished(self):
        """Check if explosion animation is complete"""
        return self.timer > self.max_timer and len(self.particles) == 0
    
    def draw(self, screen):
        """Draw explosion particles"""
        for particle in self.particles:
            alpha = max(0, particle['life'] * 12)
            color = (255, min(255, alpha), 0)  # Orange to red fade
            size = max(1, particle['life'] // 3)
            pygame.draw.circle(screen, color, 
                             (int(particle['x']), int(particle['y'])), size)

class GameManager:
    """Main game manager handling game state, spawning, and collision detection"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Arcade Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.start_time = time.time()
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        self.meteors = []
        self.bullets = []
        self.power_ups = []
        self.explosions = []
        
        # Spawn timers
        self.last_meteor_spawn = 0
        self.last_power_up_spawn = 0
        self.meteor_spawn_rate = 1000  # milliseconds
        self.power_up_spawn_rate = random.randint(8000, 12000)  # 8-12 seconds
    
    def draw_heart(self, screen, x, y, size=20, filled=True):
        """Draw a heart shape"""
        color = RED if filled else GRAY
        
        # Heart shape using circles and triangle
        # Two circles for the top
        circle_radius = size // 4
        pygame.draw.circle(screen, color, (x + circle_radius, y + circle_radius), circle_radius)
        pygame.draw.circle(screen, color, (x + size - circle_radius, y + circle_radius), circle_radius)
        
        # Triangle for the bottom
        points = [
            (x, y + circle_radius),
            (x + size, y + circle_radius),
            (x + size // 2, y + size)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
    
    def handle_input(self):
        """Handle continuous keyboard input"""
        if not self.game_over:
            keys = pygame.key.get_pressed()
            
            # Player movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move("left")
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move("right")
            
            # Shooting
            if keys[pygame.K_SPACE]:
                bullets = self.player.shoot()
                if bullets:
                    self.bullets.extend(bullets)
    
    def spawn_meteors(self):
        """Spawn meteors at regular intervals"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_meteor_spawn > self.meteor_spawn_rate:
            self.last_meteor_spawn = current_time
            
            # Spawn 1-2 meteors
            for _ in range(random.randint(1, 2)):
                x = random.randint(0, SCREEN_WIDTH - 40)
                size_type = random.choice(["large", "large", "small"])  # 2:1 ratio
                self.meteors.append(Meteor(x, -50, size_type))
            
            # Gradually increase spawn rate (decrease interval)
            if self.meteor_spawn_rate > 400:
                self.meteor_spawn_rate -= 10
    
    def spawn_power_ups(self):
        """Spawn power-ups occasionally"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_power_up_spawn > self.power_up_spawn_rate:
            self.last_power_up_spawn = current_time
            self.power_up_spawn_rate = random.randint(8000, 12000)  # Reset timer
            
            x = random.randint(0, SCREEN_WIDTH - 25)
            self.power_ups.append(PowerUp(x, -30))
    
    def update_game_objects(self):
        """Update all game objects"""
        if not self.game_over:
            # Update player
            self.player.update()
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update(self.player.time_slow)
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)
            
            # Update meteors
            for meteor in self.meteors[:]:
                meteor.update(self.player.time_slow)
                if meteor.is_off_screen():
                    self.meteors.remove(meteor)
            
            # Update power-ups
            for power_up in self.power_ups[:]:
                power_up.update()
                if power_up.is_off_screen():
                    self.power_ups.remove(power_up)
        
        # Update explosions (always)
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
    
    def check_collisions(self):
        """Check all collision detection"""
        if self.game_over:
            return
        
        # Bullet-meteor collisions
        for bullet in self.bullets[:]:
            for meteor in self.meteors[:]:
                if bullet.get_rect().colliderect(meteor.get_rect()):
                    # Create explosion
                    self.explosions.append(Explosion(meteor.x + meteor.width // 2, 
                                                   meteor.y + meteor.height // 2, 
                                                   meteor.size_type))
                    
                    # Award points
                    points = meteor.points
                    if self.player.double_score:
                        points *= 2
                    self.score += points
                    
                    # Remove objects
                    self.bullets.remove(bullet)
                    self.meteors.remove(meteor)
                    break
        
        # Player-meteor collisions
        if not self.player.invincible:
            for meteor in self.meteors[:]:
                if self.player.get_rect().colliderect(meteor.get_rect()):
                    # Create explosion
                    self.explosions.append(Explosion(self.player.x + self.player.width // 2,
                                                   self.player.y + self.player.height // 2,
                                                   "large"))
                    
                    # Remove meteor and reduce life
                    self.meteors.remove(meteor)
                    self.player.lives -= 1
                    
                    # Brief invincibility after hit
                    self.player.invincible = True
                    self.player.invincible_timer = pygame.time.get_ticks()
                    
                    if self.player.lives <= 0:
                        self.game_over = True
                    break
        
        # Player-power-up collisions
        for power_up in self.power_ups[:]:
            if self.player.get_rect().colliderect(power_up.get_rect()):
                # Apply power-up effect
                current_time = pygame.time.get_ticks()
                
                if power_up.type == "rapid_fire":
                    self.player.rapid_fire = True
                    self.player.rapid_fire_timer = current_time
                elif power_up.type == "shield":
                    self.player.invincible = True
                    self.player.invincible_timer = current_time
                elif power_up.type == "double_score":
                    self.player.double_score = True
                    self.player.double_score_timer = current_time
                elif power_up.type == "triple_shot":
                    self.player.triple_shot = True
                    self.player.triple_shot_timer = current_time
                elif power_up.type == "laser_beam":
                    self.player.laser_beam = True
                    self.player.laser_beam_timer = current_time
                elif power_up.type == "time_slow":
                    self.player.time_slow = True
                    self.player.time_slow_timer = current_time
                elif power_up.type == "mega_bullets":
                    self.player.mega_bullets = True
                    self.player.mega_bullets_timer = current_time
                
                # Remove power-up
                self.power_ups.remove(power_up)
                break
    
    def get_remaining_time(self):
        """Calculate remaining game time"""
        elapsed = time.time() - self.start_time
        remaining = max(0, GAME_DURATION - elapsed)
        return remaining
    
    def check_game_over(self):
        """Check if game should end"""
        if not self.game_over and self.get_remaining_time() <= 0:
            self.game_over = True
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives as hearts
        lives_label = self.font.render("Lives:", True, WHITE)
        self.screen.blit(lives_label, (10, 50))
        
        # Draw hearts
        heart_x = 90
        for i in range(3):
            filled = i < self.player.lives
            self.draw_heart(self.screen, heart_x + i * 30, 55, 20, filled)
        
        # Timer
        remaining_time = self.get_remaining_time()
        time_text = self.font.render(f"Time: {int(remaining_time)}s", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        
        # Power-up indicators
        y_offset = 90
        active_powers = []
        
        if self.player.rapid_fire:
            active_powers.append(("RAPID FIRE", RED))
        if self.player.invincible:
            active_powers.append(("SHIELD", CYAN))
        if self.player.double_score:
            active_powers.append(("DOUBLE SCORE", GREEN))
        if self.player.triple_shot:
            active_powers.append(("TRIPLE SHOT", PURPLE))
        if self.player.laser_beam:
            active_powers.append(("LASER BEAM", (255, 0, 255)))
        if self.player.time_slow:
            active_powers.append(("TIME SLOW", (0, 255, 255)))
        if self.player.mega_bullets:
            active_powers.append(("MEGA BULLETS", ORANGE))
        
        for power_name, color in active_powers:
            power_text = self.small_font.render(power_name, True, color)
            self.screen.blit(power_text, (10, y_offset))
            y_offset += 25
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        """Restart the game"""
        self.game_over = False
        self.score = 0
        self.start_time = time.time()
        
        # Reset player
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        
        # Clear all objects
        self.meteors.clear()
        self.bullets.clear()
        self.power_ups.clear()
        self.explosions.clear()
        
        # Reset spawn timers
        self.last_meteor_spawn = 0
        self.last_power_up_spawn = 0
        self.meteor_spawn_rate = 1000
        self.power_up_spawn_rate = random.randint(8000, 12000)
    
    def draw(self):
        """Draw all game objects"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw stars background
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for meteor in self.meteors:
            meteor.draw(self.screen)
        
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.handle_input()
            
            if not self.game_over:
                self.spawn_meteors()
                self.spawn_power_ups()
            
            self.update_game_objects()
            self.check_collisions()
            self.check_game_over()
            self.draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Main function to start the game"""
    game = GameManager()
    game.run()

if __name__ == "__main__":
    main()
