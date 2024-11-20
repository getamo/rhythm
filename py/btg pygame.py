from pynput.mouse import Listener
import time
import pygame
import sys
import os
from rhytm import gameloop  # นำเข้า gameloop จากไฟล์ gameplay.py

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (0, 0, 0)

# Initialize pygame and set up the screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Settings Menu")

# Load background music and set volume
pygame.mixer.init()
pygame.mixer.music.load("py\\rw.mp3")
volume_level = 0.5
pygame.mixer.music.set_volume(volume_level)
pygame.mixer.music.play(loops=-1)
def start_bgm():
    pygame.mixer.music.load("py\\rw.mp3")
    pygame.mixer.music.set_volume(volume_level)
    pygame.mixer.music.play(loops=-1)
start_bgm()
# Font and colors
font = pygame.font.Font(None, 32)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (34, 5, 10)
BUTTON_HOVER_COLOR = (200, 180, 160)
ARROW_COLOR = (132, 15, 80)  # Pink color for arrows

# Settings variables
frame_rate = 60  # Frame rate for screen updates
bg_animation = True  # Toggle for background animation
state = "main"  # State for menu navigation
control_mode = "Keyboard"  # Initial control mode
current_option = 0  # Tracks the current option in the settings menu
mouse_clicked = False  # Prevents double-click issues

# Settings menu options
settings_options = [
    "Frame Rate",
    "Volume",
    "Background Animation",
    "Game Control Mode"
]

# Load background frames
frame_folder = "../BTG"
frames = []
for filename in sorted(os.listdir(frame_folder)):
    if filename.endswith(".png"):
        frame_path = os.path.join(frame_folder, filename)
        frame_image = pygame.image.load(frame_path)
        frame_image = pygame.transform.scale(frame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frames.append(frame_image)

current_frame = 0
last_frame_time = pygame.time.get_ticks()

# ฟังก์ชันเพื่อเริ่มเกม (เรียกใช้คลาส gameloop ของโค้ดเกมหลัก)
def start_game():
    # สร้าง instance ของ gameloop และเรียกใช้ .run()
    game_instance = gameloop(fps=frame_rate, volume_level=volume_level)  # สร้าง instance ของ gameloop
    game_result = game_instance.run()  # เริ่มเกมโดยเรียกใช้ .run()
    
    # ตรวจสอบผลลัพธ์ของเกม เช่น 'win' หรือ 'exit'
    if game_result[0] == 'exit':
        pygame.quit()
        sys.exit()
    elif game_result[0] == 'win':
        set_state("main")  # กลับไปที่เมนูหลักเมื่อเล่นจบ
        start_bgm()
    elif game_result[0] == 'exitpause':
        set_state("main")
        start_bgm()

# ฟังก์ชันการวาดปุ่ม Play และ Settings
def draw_button(x, y, text, action=None):
    global mouse_clicked
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_color = BUTTON_HOVER_COLOR if x < mouse[0] < x + 200 and y < mouse[1] < y + 50 else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, (x, y, 200, 50), border_radius=12)
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + 100, y + 25))
    screen.blit(text_surf, text_rect)
    if x < mouse[0] < x + 200 and y < mouse[1] < y + 50:
        if click[0] == 1 and action and not mouse_clicked:
            action()
            mouse_clicked = True

def draw_arrow_button(x, y, direction, action=None):
    global mouse_clicked
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if direction == "left":
        points = [(x, y + 15), (x + 20, y), (x + 20, y + 30)]
    else:
        points = [(x, y), (x + 20, y + 15), (x, y + 30)]
    arrow_color = BUTTON_HOVER_COLOR if pygame.Rect(x, y, 20, 30).collidepoint(mouse) else ARROW_COLOR
    pygame.draw.polygon(screen, arrow_color, points)
    if pygame.Rect(x, y, 20, 30).collidepoint(mouse):
        if click[0] == 1 and action and not mouse_clicked:
            action()
            mouse_clicked = True

def open_settings():
    global frame_rate, volume_level, bg_animation, control_mode, current_option, mouse_clicked
    screen.fill((30, 30, 30))  # พื้นหลังสีเทาสำหรับหน้า Settings
    y_offset = 50

    # แสดงตัวเลือกการตั้งค่า
    for i, option in enumerate(settings_options):
        text_color = TEXT_COLOR if i != current_option else (255, 255, 0)
        text_surface = font.render(option, True, text_color)
        screen.blit(text_surface, (50, y_offset))
        
        # กำหนดค่าและวาดลูกศรปรับค่า
        if option == "Frame Rate":
            value_text = f"{frame_rate} FPS"
        elif option == "Volume":
            value_text = f"{int(volume_level * 100)}%"
        elif option == "Background Animation":
            value_text = "On" if bg_animation else "Off"
        elif option == "Game Control Mode":
            value_text = control_mode
        value_rect = pygame.Rect(SCREEN_WIDTH - 250, y_offset, 150, 30)
        screen.blit(font.render(value_text, True, TEXT_COLOR), value_rect.topleft)
        draw_arrow_button(value_rect.left - 50, y_offset, "left", lambda: adjust_option("left"))
        draw_arrow_button(value_rect.right + 10, y_offset, "right", lambda: adjust_option("right"))
        y_offset += 50

    # เพิ่มปุ่ม "Back" ที่ด้านล่างของหน้า Settings
    draw_button(300, 500, "Back", lambda: set_state("main"))
# ฟังก์ชันปรับค่าแต่ละตัวเลือก
def adjust_option(direction):
    global frame_rate, volume_level, bg_animation, control_mode
    if settings_options[current_option] == "Frame Rate":
        if direction == "right" and frame_rate < 60:
            frame_rate += 10
        elif direction == "left" and frame_rate > 10:
            frame_rate -= 10
    elif settings_options[current_option] == "Volume":
        if direction == "right" and volume_level < 1.0:
            volume_level = min(1.0, volume_level + 0.1)
        elif direction == "left" and volume_level > 0.0:
            volume_level = max(0.0, volume_level - 0.1)
        pygame.mixer.music.set_volume(volume_level)
    elif settings_options[current_option] == "Background Animation":
        bg_animation = not bg_animation
    elif settings_options[current_option] == "Game Control Mode":
        control_mode = "Mouse" if control_mode == "Keyboard" else "Keyboard"

# ฟังก์ชันตั้งค่า state
def set_state(new_state):
    global state
    state = new_state

def handle_controls():
    global current_option, bg_animation, control_mode, mouse_clicked
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if state == "main" and control_mode == "Keyboard":
                if event.key == pygame.K_RETURN:
                    set_state("settings")
            elif state == "settings" and control_mode == "Keyboard":
                if event.key == pygame.K_s:
                    current_option = (current_option + 1) % len(settings_options)
                elif event.key == pygame.K_w:
                    current_option = (current_option - 1) % len(settings_options)
                elif event.key == pygame.K_d:
                    adjust_option("right")
                elif event.key == pygame.K_a:
                    adjust_option("left")
                elif event.key == pygame.K_RETURN:
                    if settings_options[current_option] == "Background Animation":
                        bg_animation = not bg_animation
                    elif settings_options[current_option] == "Game Control Mode":
                        control_mode = "Mouse" if control_mode == "Keyboard" else "Keyboard"
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_clicked = False

def display_main_menu():
    global current_frame, last_frame_time
    screen.fill(BG_COLOR)
    current_time = pygame.time.get_ticks()
    if bg_animation and current_time - last_frame_time >= 100:
        last_frame_time = current_time
        current_frame = (current_frame + 1) % len(frames)
    screen.blit(frames[current_frame], (0, 0))
    draw_button(300, 300, "Play", start_game)  # ปุ่ม Play เรียก start_game
    draw_button(300, 400, "Settings", lambda:  set_state("settings"))

# ลูปหลักของโปรแกรม
clock = pygame.time.Clock()
running = True
while running:
    handle_controls()

    # แสดงผลตาม state
    if state == "main":
        display_main_menu()
    elif state == "settings":
        open_settings()

    pygame.display.flip()
    clock.tick(frame_rate)