import pygame
import time

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Rhythm Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load and play music
pygame.mixer.music.load('rasen.mp3')  # Load your music file here
pygame.mixer.music.play(-1)  # Loop music indefinitely

# Game variables
clock = pygame.time.Clock()
score = 0
font = pygame.font.Font(None, 36)

# Beat timing
BEAT_INTERVAL = 1000  # milliseconds (1 beat per second)
last_beat_time = pygame.time.get_ticks()

# Game loop
running = True
while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Check if key was pressed on the beat
                time_since_last_beat = current_time - last_beat_time
                if abs(time_since_last_beat) < 200:  # Give 200ms window for "perfect"
                    score += 10
                    result_text = "Perfect!"
                    result_color = GREEN
                elif abs(time_since_last_beat) < 500:  # Give 500ms window for "good"
                    score += 5
                    result_text = "Good!"
                    result_color = BLACK
                else:
                    score -= 5
                    result_text = "Miss!"
                    result_color = RED

    # Draw beat indicator
    beat_progress = (current_time - last_beat_time) / BEAT_INTERVAL
    beat_x = SCREEN_WIDTH // 2
    beat_y = int(SCREEN_HEIGHT * beat_progress)

    # Reset beat time when it reaches the bottom
    if beat_progress >= 1.0:
        last_beat_time = current_time

    # Draw beat marker and feedback text
    pygame.draw.circle(screen, BLACK, (beat_x, beat_y), 20)
    feedback = font.render(f"Score: {score}", True, BLACK)
    screen.blit(feedback, (20, 20))

    # Display result text for last key press
    if 'result_text' in locals():
        result_display = font.render(result_text, True, result_color)
        screen.blit(result_display, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()