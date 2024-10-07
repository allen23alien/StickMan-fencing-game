import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fencing")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Stickman properties
STICKMAN_WIDTH, STICKMAN_HEIGHT = 60, 100
GROUND_LEVEL = HEIGHT - 100  # Adjusted to leave room for the floor

# Floor properties
FLOOR_HEIGHT = 20

# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', 45)

# Load background image
background_image = pygame.image.load('pxfuel.jpg')  # Replace 'background.png' with your image file

# Load background music
pygame.mixer.music.load('Fight.mp3')  # Replace 'background_music.mp3' with your music file
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

class Stickman:
    def __init__(self, x, y, color, sword_color, sword_hand='left'):
        self.x = x
        self.y = y
        self.color = color
        self.sword_color = sword_color
        self.vel_x = 5
        self.vel_y = 0
        self.on_ground = True
        self.strength = 1  # Strength can be adjusted as needed
        self.hand_angle = 270  # Angle of the sword-wielding hand initially pointing downwards
        self.sword_length = 70
        self.sword_thickness = 6  # Thickness of the sword
        self.health = 10  # Stickman's health points
        self.attacking = False
        self.attack_offset = 0  # Offset for sword thrusting
        self.sword_hand = sword_hand  # Sword hand ('left' or 'right')

    def draw(self):
        # Drawing the stickman as a stick figure with a sword
        head_radius = 20
        body_length = 60
        arm_length = 47
        leg_length = 40
        
        # Head
        pygame.draw.circle(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2), head_radius)
        # Body
        pygame.draw.line(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2 + head_radius), 
                         (self.x, self.y - STICKMAN_HEIGHT // 2 + head_radius + body_length), 2)
        # Arms
        if self.sword_hand == 'left':
            self.draw_left_arm(arm_length)
        else:
            self.draw_right_arm(arm_length)
        
        # Sword
        hand_x = self.x + int(arm_length * np.cos(np.radians(self.hand_angle)))
        hand_y = self.y - STICKMAN_HEIGHT // 2 + head_radius + 10 + int(arm_length * np.sin(np.radians(self.hand_angle)))
        sword_x = hand_x + int((self.sword_length + self.attack_offset) * np.cos(np.radians(self.hand_angle)))
        sword_y = hand_y + int((self.sword_length + self.attack_offset) * np.sin(np.radians(self.hand_angle)))
        pygame.draw.line(screen, self.sword_color, (hand_x, hand_y), (sword_x, sword_y), self.sword_thickness)
        
        # Legs
        pygame.draw.line(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2 + head_radius + body_length), 
                         (self.x - leg_length, self.y - STICKMAN_HEIGHT // 2 + head_radius + body_length + leg_length), 2)
        pygame.draw.line(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2 + head_radius + body_length), 
                         (self.x + leg_length, self.y - STICKMAN_HEIGHT // 2 + head_radius + body_length + leg_length), 2)
    
    def draw_left_arm(self, arm_length):
        pygame.draw.line(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2 + 20), 
                         (self.x - arm_length, self.y - STICKMAN_HEIGHT // 2 + 20), 2)
    
    def draw_right_arm(self, arm_length):
        pygame.draw.line(screen, self.color, (self.x, self.y - STICKMAN_HEIGHT // 2 + 20), 
                         (self.x + arm_length, self.y - STICKMAN_HEIGHT // 2 + 20), 2)
    
    def move(self, keys, controls):
        if keys[controls['left']] and self.x - self.vel_x > 0:
            self.x -= self.vel_x
        if keys[controls['right']] and self.x + self.vel_x < WIDTH - STICKMAN_WIDTH:
            self.x += self.vel_x
        if keys[controls['up']] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False
        if keys[controls['hand_up']]:
            self.hand_angle = (self.hand_angle - 5) % 360
        if keys[controls['hand_down']]:
            self.hand_angle = (self.hand_angle + 5) % 360
        if keys[controls['attack']]:
            self.attacking = True
    
    def apply_gravity(self):
        if not self.on_ground:
            self.y += self.vel_y
            self.vel_y += 1
            if self.y >= GROUND_LEVEL - STICKMAN_HEIGHT // 2:
                self.y = GROUND_LEVEL - STICKMAN_HEIGHT // 2
                self.on_ground = True
                self.vel_y = 0
    
    def update_attack(self):
        if self.attacking:
            self.attack_offset += 5
            if self.attack_offset >= 20:
                self.attack_offset = 0
                self.attacking = False
    
    def check_collision(self, other):
        if (self.x + STICKMAN_WIDTH > other.x and
            self.x < other.x + STICKMAN_WIDTH and
            self.y + STICKMAN_HEIGHT > other.y and
            self.y < other.y + STICKMAN_HEIGHT):
            return True
        return False
    
    def handle_collision(self, other):
        if self.check_collision(other):
            overlap_x = min(self.x + STICKMAN_WIDTH - other.x, other.x + STICKMAN_WIDTH - self.x)
            overlap_y = min(self.y + STICKMAN_HEIGHT - other.y, other.y + STICKMAN_HEIGHT - self.y)
            
            if overlap_x < overlap_y:
                if self.x < other.x:
                    self.x -= overlap_x // 2
                    other.x += overlap_x // 2
                else:
                    self.x += overlap_x // 2
                    other.x -= overlap_x // 2
            else:
                if self.y < other.y:
                    self.y -= overlap_y // 2
                    other.y += overlap_y // 2
                    self.vel_y = 0
                    other.vel_y = 0
                else:
                    self.y += overlap_y // 2
                    other.y -= overlap_y // 2
                    self.vel_y = 0
                    other.vel_y = 0
    
    def check_sword_hit(self, other):
        # Check if the sword of this stickman hits the other stickman
        hand_x = self.x + int(20 * np.cos(np.radians(self.hand_angle)))
        hand_y = self.y - STICKMAN_HEIGHT // 2 + 10 + int(20 * np.sin(np.radians(self.hand_angle)))
        sword_x = hand_x + int((self.sword_length + self.attack_offset) * np.cos(np.radians(self.hand_angle)))
        sword_y = hand_y + int((self.sword_length + self.attack_offset) * np.sin(np.radians(self.hand_angle)))
        
        hit_boxes = [
            (other.x, other.y - STICKMAN_HEIGHT // 2, STICKMAN_WIDTH, STICKMAN_HEIGHT // 2),  # Head
            (other.x, other.y - STICKMAN_HEIGHT // 2 + STICKMAN_HEIGHT // 2, STICKMAN_WIDTH, STICKMAN_HEIGHT // 2),  # Body
            (other.x - 20, other.y - STICKMAN_HEIGHT // 2 + 60, 40, 40),  # Left leg
            (other.x + STICKMAN_WIDTH - 20, other.y - STICKMAN_HEIGHT // 2 + 60, 40, 40)  # Right leg
        ]
        
        for box in hit_boxes:
            if (box[0] < sword_x < box[0] + box[2] and
                box[1] < sword_y < box[1] + box[3]):
                other.health -= 1
                print(f"Hit! {other.color} has {other.health} health left.")
                break
        
        # Check if swords clash
        if (abs(self.x - other.x) < 50 and
            abs(self.y - other.y) < 50 and
            abs(self.hand_angle - other.hand_angle) < 10):
            self.health -= 1
            other.health -= 1
            print("Swords clashed! Both players take damage.")
    
def draw_floor():
    pygame.draw.rect(screen, GREEN, (0, GROUND_LEVEL, WIDTH, FLOOR_HEIGHT))

def display_health(player1, player2):
    player1_health_text = font.render(f"Player 1 Health: {player1.health}", True, RED)
    player2_health_text = font.render(f"Player 2 Health: {player2.health}", True, BLUE)
    screen.blit(player1_health_text, (10, 10))
    screen.blit(player2_health_text, (WIDTH - player2_health_text.get_width() - 10, 10))

def display_winner(player):
    winner_text = font.render(f"{player.color} Wins!", True, BLACK)
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))

def display_controls():
    screen.fill(WHITE)
    instructions = [
        "Player 1 Controls:",
        "Move Left: A",
        "Move Right: D",
        "Jump: W",
        "Move Sword Up: Q",
        "Move Sword Down: E",
        "Attack: F",
        "",
        "Player 2 Controls:",
        "Move Left: Left Arrow",
        "Move Right: Right Arrow",
        "Jump: Up Arrow",
        "Move Sword Up: Comma (,)",
        "Move Sword Down: Period (.)",
        "Attack: Slash (/)",
        "",
        "Press any key to start"
    ]
    y_offset = 50
    for instruction in instructions:
        text = font.render(instruction, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 40
    
    pygame.display.update()

def main():
    run = True
    clock = pygame.time.Clock()
    
    player1 = Stickman(100, GROUND_LEVEL - STICKMAN_HEIGHT // 2, RED, BLACK)
    player2 = Stickman(1000, GROUND_LEVEL - STICKMAN_HEIGHT // 2, BLUE, BLACK, sword_hand='right')
    
    player1_controls = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'up': pygame.K_w,
        'hand_up': pygame.K_q,
        'hand_down': pygame.K_e,
        'attack': pygame.K_g
    }
    
    player2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'up': pygame.K_UP,
        'hand_up': pygame.K_COMMA,
        'hand_down': pygame.K_PERIOD,
        'attack': pygame.K_SLASH
    }
    
    # Display controls and wait for a key press to start the game
    display_controls()
    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                waiting_for_start = False
            elif event.type == pygame.KEYDOWN:
                waiting_for_start = False
    
    while run:
        clock.tick(30)
        screen.blit(background_image, (0, 0))  # Draw the background image
        draw_floor()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys = pygame.key.get_pressed()
        player1.move(keys, player1_controls)
        player2.move(keys, player2_controls)
        
        player1.apply_gravity()
        player2.apply_gravity()
        
        player1.handle_collision(player2)
        
        player1.update_attack()
        player2.update_attack()
        
        player1.check_sword_hit(player2)
        player2.check_sword_hit(player1)
        
        player1.draw()
        player2.draw()
        
        display_health(player1, player2)
        
        if player1.health <= 0:
            display_winner(player2)
            run = False
        elif player2.health <= 0:
            display_winner(player1)
            run = False
        
        pygame.display.update()
    
    pygame.time.delay(5000)  # Delay before closing the game
    pygame.quit()

if __name__ == "__main__":
    main()
