import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 25
UI_HEIGHT = 80
GAME_HEIGHT = WINDOW_HEIGHT - UI_HEIGHT

# Speed settings
SPEED_SETTINGS = {
    'Slow': 8,
    'Normal': 12,
    'Fast': 16,
    'Insane': 22
}
SPEED_NAMES = list(SPEED_SETTINGS.keys())

# Snake themes
SNAKE_THEMES = {
    'Classic': {'head': (50, 205, 50), 'body': (34, 139, 34), 'outline': (0, 100, 0)},
    'Fire': {'head': (255, 69, 0), 'body': (220, 20, 60), 'outline': (139, 0, 0)},
    'Ice': {'head': (135, 206, 235), 'body': (70, 130, 180), 'outline': (25, 25, 112)},
    'Gold': {'head': (255, 215, 0), 'body': (218, 165, 32), 'outline': (184, 134, 11)},
    'Neon': {'head': (57, 255, 20), 'body': (0, 255, 127), 'outline': (0, 139, 69)}
}
THEME_NAMES = list(SNAKE_THEMES.keys())

# Colors - Professional palette
BG_COLOR = (15, 15, 35)
UI_BG = (25, 25, 45)
SNAKE_HEAD = (50, 205, 50)
SNAKE_BODY = (34, 139, 34)
SNAKE_OUTLINE = (0, 100, 0)
FOOD_COLOR = (255, 69, 0)
FOOD_GLOW = (255, 140, 0)
TEXT_COLOR = (220, 220, 220)
ACCENT_COLOR = (0, 191, 255)
GRID_COLOR = (30, 30, 50)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pro Snake - Enhanced Edition")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.ui_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.high_score = 0
        self.game_state = "menu"  # menu, settings, playing, game_over
        self.selected_speed = 1  # Normal by default
        self.base_speed = SPEED_SETTINGS[SPEED_NAMES[self.selected_speed]]
        self.current_speed = self.base_speed
        self.show_grid = True
        self.particle_effects = True
        self.particles = []
        
        # New features
        self.lives = 3
        self.max_lives = 3
        self.selected_theme = 0  # Classic by default
        self.smooth_movement = True
        self.snake_pos = []
        self.target_pos = []
        self.move_progress = 0
        self.settings_tab = 0  # 0: Game, 1: Visual, 2: Snake
        
        self.reset_game()

    def reset_game(self):
        start_x = (WINDOW_WIDTH//2 // CELL_SIZE) * CELL_SIZE
        start_y = ((UI_HEIGHT + GAME_HEIGHT//2) // CELL_SIZE) * CELL_SIZE
        self.snake = [start_x, start_y]
        self.snake_pos = [[start_x, start_y]]
        self.target_pos = [[start_x, start_y]]
        self.direction = (CELL_SIZE, 0)
        self.food = self.generate_food()
        self.score = 0
        self.food_eaten = 0
        self.current_speed = self.base_speed
        self.particles = []
        self.move_progress = 0
        if self.game_state != "playing":
            self.lives = self.max_lives
        self.game_state = "playing"

    def generate_food(self):
        while True:
            x = random.randint(0, (WINDOW_WIDTH-CELL_SIZE)//CELL_SIZE) * CELL_SIZE
            y = random.randint(UI_HEIGHT//CELL_SIZE, (WINDOW_HEIGHT-CELL_SIZE)//CELL_SIZE) * CELL_SIZE
            if [x, y] not in self.snake:
                return [x, y]

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_s:
                        self.game_state = "settings"
                elif self.game_state == "settings":
                    if event.key == pygame.K_LEFT:
                        self.settings_tab = (self.settings_tab - 1) % 3
                    elif event.key == pygame.K_RIGHT:
                        self.settings_tab = (self.settings_tab + 1) % 3
                    elif event.key == pygame.K_UP:
                        if self.settings_tab == 0:  # Game settings
                            self.selected_speed = (self.selected_speed - 1) % len(SPEED_NAMES)
                            self.base_speed = SPEED_SETTINGS[SPEED_NAMES[self.selected_speed]]
                        elif self.settings_tab == 2:  # Snake settings
                            self.selected_theme = (self.selected_theme - 1) % len(THEME_NAMES)
                    elif event.key == pygame.K_DOWN:
                        if self.settings_tab == 0:  # Game settings
                            self.selected_speed = (self.selected_speed + 1) % len(SPEED_NAMES)
                            self.base_speed = SPEED_SETTINGS[SPEED_NAMES[self.selected_speed]]
                        elif self.settings_tab == 2:  # Snake settings
                            self.selected_theme = (self.selected_theme + 1) % len(THEME_NAMES)
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_p:
                        self.particle_effects = not self.particle_effects
                    elif event.key == pygame.K_m:
                        self.smooth_movement = not self.smooth_movement
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                elif self.game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                elif self.game_state == "playing":
                    if event.key == pygame.K_UP and self.direction != (0, CELL_SIZE):
                        self.direction = (0, -CELL_SIZE)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -CELL_SIZE):
                        self.direction = (0, CELL_SIZE)
                    elif event.key == pygame.K_LEFT and self.direction != (CELL_SIZE, 0):
                        self.direction = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-CELL_SIZE, 0):
                        self.direction = (CELL_SIZE, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
        return True

    def update_snake(self):
        if self.game_state != "playing":
            return

        if self.smooth_movement:
            self.move_progress += self.current_speed / 60.0
            if self.move_progress >= 1.0:
                self.move_progress = 0
                self.move_snake_step()
        else:
            self.move_snake_step()

    def move_snake_step(self):
        # Move snake head
        head_x, head_y = self.snake[0], self.snake[1]
        new_head_x = head_x + self.direction[0]
        new_head_y = head_y + self.direction[1]

        # Wall wrapping
        if new_head_x < 0:
            new_head_x = WINDOW_WIDTH - CELL_SIZE
        elif new_head_x >= WINDOW_WIDTH:
            new_head_x = 0
        
        if new_head_y < UI_HEIGHT:
            new_head_y = WINDOW_HEIGHT - CELL_SIZE
        elif new_head_y >= WINDOW_HEIGHT:
            new_head_y = UI_HEIGHT

        new_head = [new_head_x, new_head_y]

        # Check self collision
        for i in range(0, len(self.snake), 2):
            if [self.snake[i], self.snake[i+1]] == new_head:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = "game_over"
                    if self.score > self.high_score:
                        self.high_score = self.score
                else:
                    # Reset position but keep score
                    start_x = (WINDOW_WIDTH//2 // CELL_SIZE) * CELL_SIZE
                    start_y = ((UI_HEIGHT + GAME_HEIGHT//2) // CELL_SIZE) * CELL_SIZE
                    self.snake = [start_x, start_y]
                    self.direction = (CELL_SIZE, 0)
                return

        self.snake.insert(0, new_head_x)
        self.snake.insert(1, new_head_y)

        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.food_eaten += 1
            
            # Add particles for food eaten
            if self.particle_effects:
                for _ in range(8):
                    self.particles.append({
                        'x': self.food[0] + CELL_SIZE//2,
                        'y': self.food[1] + CELL_SIZE//2,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-3, 3),
                        'life': 30,
                        'color': FOOD_COLOR
                    })
            
            self.food = self.generate_food()
            # Increase speed slightly
            if self.food_eaten % 5 == 0:
                self.current_speed = min(self.current_speed + 1, self.base_speed + 8)
        else:
            self.snake.pop()
            self.snake.pop()

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vy'] += 0.1  # Gravity
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            color = (*particle['color'][:3], alpha)
            size = max(1, int(particle['life'] / 6))
            pygame.draw.circle(self.screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)

    def draw_grid(self):
        if self.show_grid:
            for x in range(0, WINDOW_WIDTH, CELL_SIZE):
                pygame.draw.line(self.screen, GRID_COLOR, (x, UI_HEIGHT), (x, WINDOW_HEIGHT))
            for y in range(UI_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
                pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self):
        theme = SNAKE_THEMES[THEME_NAMES[self.selected_theme]]
        
        for i in range(0, len(self.snake), 2):
            x, y = self.snake[i], self.snake[i+1]
            
            # Smooth movement interpolation
            if self.smooth_movement and i == 0 and self.move_progress > 0:
                next_x = x + self.direction[0] * self.move_progress
                next_y = y + self.direction[1] * self.move_progress
                x, y = int(next_x), int(next_y)
            
            if i == 0:  # Head
                # Head shape with theme colors
                pygame.draw.rect(self.screen, theme['head'], (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))
                pygame.draw.rect(self.screen, theme['outline'], (x, y, CELL_SIZE, CELL_SIZE), 2)
                
                # Eyes positioned based on direction
                eye_size = 4
                if self.direction == (CELL_SIZE, 0):  # Moving right
                    eye1_pos = (x + 18, y + 6)
                    eye2_pos = (x + 18, y + 18)
                elif self.direction == (-CELL_SIZE, 0):  # Moving left
                    eye1_pos = (x + 6, y + 6)
                    eye2_pos = (x + 6, y + 18)
                elif self.direction == (0, -CELL_SIZE):  # Moving up
                    eye1_pos = (x + 6, y + 6)
                    eye2_pos = (x + 18, y + 6)
                else:  # Moving down
                    eye1_pos = (x + 6, y + 18)
                    eye2_pos = (x + 18, y + 18)
                
                # Draw eyes
                pygame.draw.circle(self.screen, (255, 255, 255), eye1_pos, eye_size)
                pygame.draw.circle(self.screen, (255, 255, 255), eye2_pos, eye_size)
                pygame.draw.circle(self.screen, (0, 0, 0), eye1_pos, 2)
                pygame.draw.circle(self.screen, (0, 0, 0), eye2_pos, 2)
                
                # Draw nose/mouth indicator
                if self.direction == (CELL_SIZE, 0):  # Right
                    pygame.draw.circle(self.screen, (200, 200, 200), (x + 22, y + 12), 2)
                elif self.direction == (-CELL_SIZE, 0):  # Left
                    pygame.draw.circle(self.screen, (200, 200, 200), (x + 2, y + 12), 2)
                elif self.direction == (0, -CELL_SIZE):  # Up
                    pygame.draw.circle(self.screen, (200, 200, 200), (x + 12, y + 2), 2)
                else:  # Down
                    pygame.draw.circle(self.screen, (200, 200, 200), (x + 12, y + 22), 2)
                    
            else:  # Body
                pygame.draw.rect(self.screen, theme['body'], (x+1, y+1, CELL_SIZE-2, CELL_SIZE-2))
                pygame.draw.rect(self.screen, theme['outline'], (x, y, CELL_SIZE, CELL_SIZE), 1)

    def draw_food(self):
        x, y = self.food
        # Glowing effect
        for i in range(3):
            color = [min(255, c + 30*i) for c in FOOD_GLOW]
            size = CELL_SIZE - i*2
            offset = i
            pygame.draw.rect(self.screen, color, (x+offset, y+offset, size, size))
        pygame.draw.rect(self.screen, FOOD_COLOR, (x+3, y+3, CELL_SIZE-6, CELL_SIZE-6))

    def draw_hearts(self):
        heart_size = 15
        for i in range(self.max_lives):
            x = 20 + i * (heart_size + 5)
            y = 50
            if i < self.lives:
                # Full heart
                pygame.draw.polygon(self.screen, (255, 0, 0), [
                    (x + heart_size//2, y + heart_size),
                    (x, y + heart_size//3),
                    (x + heart_size//3, y),
                    (x + 2*heart_size//3, y),
                    (x + heart_size, y + heart_size//3)
                ])
            else:
                # Empty heart
                pygame.draw.polygon(self.screen, (100, 100, 100), [
                    (x + heart_size//2, y + heart_size),
                    (x, y + heart_size//3),
                    (x + heart_size//3, y),
                    (x + 2*heart_size//3, y),
                    (x + heart_size, y + heart_size//3)
                ], 2)

    def draw_ui(self):
        # UI background
        pygame.draw.rect(self.screen, UI_BG, (0, 0, WINDOW_WIDTH, UI_HEIGHT))
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, UI_HEIGHT), (WINDOW_WIDTH, UI_HEIGHT), 2)
        
        # Score
        score_text = self.ui_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (150, 15))
        
        # High Score
        high_score_text = self.ui_font.render(f"Best: {self.high_score}", True, ACCENT_COLOR)
        self.screen.blit(high_score_text, (300, 15))
        
        # Speed and Length
        speed_text = self.small_font.render(f"Speed: {self.current_speed}", True, TEXT_COLOR)
        self.screen.blit(speed_text, (500, 20))
        
        length_text = self.small_font.render(f"Length: {len(self.snake)//2}", True, TEXT_COLOR)
        self.screen.blit(length_text, (600, 20))
        
        # Theme indicator
        theme_text = self.small_font.render(f"Theme: {THEME_NAMES[self.selected_theme]}", True, TEXT_COLOR)
        self.screen.blit(theme_text, (500, 40))
        
        # Hearts
        self.draw_hearts()
        
        # Controls hint
        controls_text = self.small_font.render("ESC: Menu | Arrows: Move", True, (150, 150, 150))
        self.screen.blit(controls_text, (600, 60))

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.title_font.render("PRO SNAKE", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.ui_font.render("Enhanced Edition", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Features:",
            "• Snake wraps around walls",
            "• Professional UI design",
            "• Customizable speed settings",
            "• Particle effects",
            "• Enhanced snake graphics",
            "",
            "Press SPACE to start",
            "Press S for settings"
        ]
        
        y_offset = 280
        for instruction in instructions:
            color = ACCENT_COLOR if "SPACE" in instruction else TEXT_COLOR
            font = self.ui_font if "SPACE" in instruction else self.small_font
            text = font.render(instruction, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # High score display
        if self.high_score > 0:
            high_score_text = self.ui_font.render(f"High Score: {self.high_score}", True, FOOD_COLOR)
            high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH//2, 500))
            self.screen.blit(high_score_text, high_score_rect)

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.title_font.render("GAME OVER", True, FOOD_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score = self.ui_font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        final_score_rect = final_score.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
        self.screen.blit(final_score, final_score_rect)
        
        # New high score
        if self.score == self.high_score and self.score > 0:
            new_high = self.ui_font.render("NEW HIGH SCORE!", True, ACCENT_COLOR)
            new_high_rect = new_high.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            self.screen.blit(new_high, new_high_rect)
        
        # Instructions
        restart_text = self.ui_font.render("SPACE: Play Again", True, ACCENT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 60))
        self.screen.blit(restart_text, restart_rect)
        
        menu_text = self.small_font.render("ESC: Main Menu", True, TEXT_COLOR)
        menu_rect = menu_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
        self.screen.blit(menu_text, menu_rect)

    def draw_settings(self):
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.title_font.render("SETTINGS", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Tab navigation
        tabs = ["Game", "Visual", "Snake"]
        tab_width = 150
        start_x = (WINDOW_WIDTH - len(tabs) * tab_width) // 2
        
        for i, tab in enumerate(tabs):
            x = start_x + i * tab_width
            color = ACCENT_COLOR if i == self.settings_tab else TEXT_COLOR
            bg_color = UI_BG if i == self.settings_tab else BG_COLOR
            
            pygame.draw.rect(self.screen, bg_color, (x, 100, tab_width-10, 40))
            pygame.draw.rect(self.screen, color, (x, 100, tab_width-10, 40), 2)
            
            tab_text = self.ui_font.render(tab, True, color)
            tab_rect = tab_text.get_rect(center=(x + tab_width//2 - 5, 120))
            self.screen.blit(tab_text, tab_rect)
        
        # Tab content
        if self.settings_tab == 0:  # Game settings
            # Speed setting
            speed_label = self.ui_font.render("Game Speed:", True, TEXT_COLOR)
            self.screen.blit(speed_label, (200, 180))
            
            for i, speed_name in enumerate(SPEED_NAMES):
                color = ACCENT_COLOR if i == self.selected_speed else TEXT_COLOR
                speed_text = self.ui_font.render(f"{speed_name} ({SPEED_SETTINGS[speed_name]} FPS)", True, color)
                self.screen.blit(speed_text, (250, 220 + i * 40))
                if i == self.selected_speed:
                    pygame.draw.rect(self.screen, ACCENT_COLOR, (240, 220 + i * 40, 300, 35), 2)
            
            # Lives setting
            lives_text = self.ui_font.render(f"Lives: {self.max_lives}", True, TEXT_COLOR)
            self.screen.blit(lives_text, (200, 400))
            
        elif self.settings_tab == 1:  # Visual settings
            options = [
                (f"Grid: {'ON' if self.show_grid else 'OFF'}", self.show_grid),
                (f"Particles: {'ON' if self.particle_effects else 'OFF'}", self.particle_effects),
                (f"Smooth Movement: {'ON' if self.smooth_movement else 'OFF'}", self.smooth_movement)
            ]
            
            for i, (text, enabled) in enumerate(options):
                color = ACCENT_COLOR if enabled else TEXT_COLOR
                option_text = self.ui_font.render(text, True, color)
                self.screen.blit(option_text, (200, 200 + i * 50))
                
        elif self.settings_tab == 2:  # Snake settings
            # Theme selection
            theme_label = self.ui_font.render("Snake Theme:", True, TEXT_COLOR)
            self.screen.blit(theme_label, (200, 180))
            
            for i, theme_name in enumerate(THEME_NAMES):
                color = ACCENT_COLOR if i == self.selected_theme else TEXT_COLOR
                theme_text = self.ui_font.render(theme_name, True, color)
                self.screen.blit(theme_text, (250, 220 + i * 40))
                
                # Preview snake colors
                theme = SNAKE_THEMES[theme_name]
                preview_x = 450
                preview_y = 220 + i * 40
                pygame.draw.rect(self.screen, theme['head'], (preview_x, preview_y, 20, 20))
                pygame.draw.rect(self.screen, theme['body'], (preview_x + 25, preview_y, 20, 20))
                pygame.draw.rect(self.screen, theme['outline'], (preview_x, preview_y, 20, 20), 2)
                pygame.draw.rect(self.screen, theme['outline'], (preview_x + 25, preview_y, 20, 20), 2)
                
                if i == self.selected_theme:
                    pygame.draw.rect(self.screen, ACCENT_COLOR, (240, 220 + i * 40, 250, 35), 2)
        
        # Controls
        controls = [
            "←→ Switch Tabs",
            "↑↓ Navigate Options",
            "G Toggle Grid | P Toggle Particles | M Toggle Movement",
            "SPACE Start Game | ESC Back to Menu"
        ]
        
        y_offset = 480
        for control in controls:
            text = self.small_font.render(control, True, (150, 150, 150))
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25

    def draw(self):
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "settings":
            self.draw_settings()
        elif self.game_state == "playing":
            self.screen.fill(BG_COLOR)
            self.draw_grid()
            self.draw_food()
            self.draw_snake()
            if self.particle_effects:
                self.draw_particles()
            self.draw_ui()
        elif self.game_state == "game_over":
            self.screen.fill(BG_COLOR)
            self.draw_grid()
            self.draw_food()
            self.draw_snake()
            if self.particle_effects:
                self.draw_particles()
            self.draw_ui()
            self.draw_game_over()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update_snake()
            if self.particle_effects:
                self.update_particles()
            self.draw()
            fps = 60 if self.smooth_movement else self.current_speed
            self.clock.tick(fps if self.game_state == "playing" else 60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()