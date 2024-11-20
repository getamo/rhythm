import pygame
import random
import os

# Define a generic 'Spirit' class as a base for all objects in the game
class spirit():
    def __init__(self, x, y, layer, lifetime, fps, screen, scale, gaphicpath):
        self.scale = scale
        self.gaphicpath = gaphicpath
        self.screen = screen
        self.x = x
        self.y = y
        self.layer = layer
        self.lifetime = lifetime
        self.fps = fps

    def activate(self):
        self.lifetime -= 3
        self.show(self.gaphicpath)
        if self.lifetime == 0:
            return 'delete'

    def show(self, gaphicpath):
        image = pygame.image.load(gaphicpath)
        image = pygame.transform.scale(image, (self.scale[0], self.scale[1]))
        image_rect = image.get_rect(center=(self.x, self.y))
        self.screen.blit(image, image_rect.topleft)

# Define a 'Note' class to represent musical notes

class note(spirit):
    def __init__(self, x, y, layer, lifetime, fps, screen, scale, gaphicpath, type):
        super().__init__(x, y, layer, lifetime, fps, screen, scale, gaphicpath)
        self.initx = x
        self.distance_per_tick = (x * 1 / lifetime)
        self.type = type

    def activate(self):
        self.x -= self.distance_per_tick  # Move left
        self.lifetime -= 1  # Reduce lifetime per tick
        self.show()
        if self.x <= 0:
            return 'miss'

    def show(self):
        # Dynamically draw circles instead of using images
        circle_color = (255, 0, 0) if self.type == 1 else (255, 255, 255)  # Green for type 1, Red for type 0
        pygame.draw.circle(self.screen, circle_color, (int(self.x), int(self.y)), self.scale[0] // 2)

class Effect(spirit):
    def __init__(self, x, y, layer, lifetime, fps, screen, scale, color):
        super().__init__(x, y, layer, lifetime, fps, screen, scale, gaphicpath=None)
        self.color = color
        self.alpha = 255  # Fully opaque at the start
        self.radius = 0

    def activate(self):
        # Expand the circle
        self.radius += 2
        # Gradually fade out
        self.alpha -= int(255 / self.lifetime)
        self.alpha = max(0, self.alpha)  # Ensure alpha doesn't go negative
        if self.alpha == 0:
            return 'delete'

        self.show(None)

    def show(self, gaphicpath=None):
        # Draw a fading circle at the location
        surface = pygame.Surface((self.scale[0] * 2, self.scale[1] * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, self.alpha), (self.scale[0], self.scale[1]), self.radius)
        self.screen.blit(surface, (self.x - self.scale[0], self.y - self.scale[1]))

# Define the main game loop class
class gameloop():
    def __init__(self, SCREEN_WIDTH=800, SCREEN_HEIGHT=600, fps=30, music='game_music.mp3', musiclength=230, notelifetime=2, notenumber=300, control_mode="Keyboard", volume_level = 0.5):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.fps = fps
        self.music = music
        self.volume_level = volume_level
        self.current_tick = 0
        self.notenumber = notenumber
        self.notelifetime = notelifetime * fps
        maplength = (musiclength + 10) * fps
        self.maplength = maplength
        self.songmap = [[] for _ in range(maplength)]
        self.score = 0
        self.combo = 0
        self.control_mode = control_mode
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.floating_images = []
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.statistics = {
            "perfect": 0,
            "good": 0,
            "bad": 0,
            "miss": 0
        }

            # Generate random notes
        self.generate_random_notes(notenumber)

        # Load frames for background animation
        self.frame_folder = "extracted_frames"
        self.frames = []
        
        for filename in sorted(os.listdir(self.frame_folder)):
            if filename.endswith(".jpg"):  # เพิ่ม .jpg
                frame_path = os.path.join(self.frame_folder, filename)
                frame_image = pygame.image.load(frame_path)
                frame_image = pygame.transform.scale(frame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.frames.append(frame_image)
                
            else:
                self.frames.append(None)  # Fallback to plain background if no frames are found
            
    def generate_random_notes(self, notenumber, step=0.2):
        """
        Generate random notes with a minimum gap of 'step' frames between consecutive notes.
        
        :param notenumber: Total number of notes to generate.
        :param step: Minimum gap (in frames) between notes.
        """
        step = int(step * self.fps)
        used_times = set()  # Keep track of used times to enforce gaps

        for _ in range(notenumber):
            while True:
                time = random.randint(0, self.maplength - 1)

                # Ensure the time is valid and respects the 'step' gap
                if all(abs(time - used_time) >= step for used_time in used_times):
                    used_times.add(time)
                    break

            position_x = self.SCREEN_WIDTH  # Start from the right edge
            position_y = self.hight(0.9)
            note_type = random.choices([0, 1], weights=[70, 30], k=1)[0]  # Weighted note types
            note_object = note(
                position_x, 
                position_y, 
                10, 
                self.notelifetime, 
                self.fps, 
                self.screen, 
                (self.width(0.045) , self.hight(0.045)), 
                gaphicpath=None, 
                type=note_type
            )

            self.songmap[time].append(note_object)

    def process_hit(self, hit_type, spiritlist, target_center, target_radius=50):
        condition = 'miss'
        type_colors = {
        1: (255, 0, 0),
        0: (255, 255, 255),
        }
        for spirit in spiritlist:
            if isinstance(spirit, note) and spirit.type == hit_type:
                note_rect = pygame.Rect(spirit.x - 10, spirit.y - 10, 20, 20)
                space_deviation = 0.4 * self.width(1) / (self.notelifetime/self.fps)
                target_rect = pygame.Rect(target_center[0] - space_deviation, target_center[1] - space_deviation, space_deviation * 2, space_deviation * 2)
                
                if target_rect.colliderect(note_rect):  # ตรวจสอบการกดโดน
                    spiritlist.remove(spirit)
                    effect = Effect(
                        x=spirit.x,
                        y=spirit.y,
                        layer=spirit.layer + 1,
                        lifetime=0.3*self.fps,  # Duration of the effect
                        fps=self.fps,
                        screen=self.screen,
                        scale=(self.width(0.045) , self.hight(0.045)),  # Initial size of the circle
                        color=type_colors.get(spirit.type, (0, 0, 0))  # Default black if type not in dict
                    )
                    spiritlist.append(effect)
                    deviation = abs((spirit.lifetime / self.fps) - (0.1*self.notelifetime/self.fps))  # ค่า deviation ที่ตั้งให้เหมาะกับจังหวะของเพลง
                    if deviation <= 0.05:
                        condition = 'perfect'
                    elif deviation <= 0.15:
                        condition = 'good'      
                    elif deviation <= 0.3:
                        condition = 'bad'
                    break
        self.evaluate(condition)
    
    def evaluate(self, condition):
        self.statistics[condition] += 1  # Record the hit type
    
        multiplier = {'perfect': 1, 'good': 0.65, 'bad': 0.28, 'miss': 0.00}[condition]
        self.combo = 0 if condition == 'miss' else self.combo + 1
        score_increase = multiplier * (100000 / self.notenumber) * (0.5 + (self.combo / self.notenumber))
        self.score += score_increase

        # Load feedback image based on condition
        image_path = f'image/{condition}.png'  # Path to condition image
        feedback_image = pygame.image.load(image_path)
        feedback_image = pygame.transform.scale(feedback_image, (120, 150))  # Smaller image size for floating effect

        # Initialize floating effect properties
        self.floating_images.append({
            'image': feedback_image,
            'x': self.SCREEN_WIDTH // 10,
            'y': int(self.SCREEN_HEIGHT * 0.6),
            'alpha': 255,  # Fully opaque at start
            'float_speed': -1.5  # Controls speed of floating up
        })

    def pause_menu(self):
        font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 36)
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))

        button_width = self.width(0.3)
        button_height = self.hight(0.1)
        button_x = (self.SCREEN_WIDTH - button_width) // 2
        continue_button_y = self.hight(0.4)
        exit_button_y = self.hight(0.6)

        continue_text = button_font.render("Continue", True, (255, 255, 255))
        exit_text = button_font.render("Exit", True, (255, 255, 255))

        paused = True
        while paused:
            self.screen.blit(overlay, (0, 0))

            continue_button = pygame.Rect(button_x, continue_button_y, button_width, button_height)
            exit_button = pygame.Rect(button_x, exit_button_y, button_width, button_height)

            pygame.draw.rect(self.screen, (100, 100, 255), continue_button, border_radius=10)
            pygame.draw.rect(self.screen, (255, 100, 100), exit_button, border_radius=10)

            self.screen.blit(
                continue_text, 
                (button_x + (button_width - continue_text.get_width()) // 2, continue_button_y + (button_height - continue_text.get_height()) // 2)
            )
            self.screen.blit(
                exit_text, 
                (button_x + (button_width - exit_text.get_width()) // 2, exit_button_y + (button_height - exit_text.get_height()) // 2)
            )

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if continue_button.collidepoint(mouse_pos):
                        paused = False
                    elif exit_button.collidepoint(mouse_pos):
                        return 1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False

    def run(self):
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.set_volume(self.volume_level)
        pygame.mixer.music.play(-1)
        clock = pygame.time.Clock()
        spiritlist = []
        running = True

        # Define the white bridge and red target circle
        bridge_rect = pygame.Rect(0, self.SCREEN_HEIGHT * 0.9 - (self.width(0.005)//2), self.SCREEN_WIDTH, self.width(0.005))
        target_circle_radius = self.width(0.025)
        target_circle_center = (self.SCREEN_WIDTH * 0.1, self.SCREEN_HEIGHT * 0.9)

        # เพิ่มค่า delay ของพื้นหลังเป็น 200ms
        bg_frame_delay = 50  # ระยะเวลาในการรอให้เฟรมถัดไปปรากฏ (หน่วยมิลลิวินาที)
        while running:
            tick = self.current_tick
            if tick == self.maplength:
                return 'win', self.statistics

            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time >= bg_frame_delay:  # ใช้ bg_frame_delay ในการควบคุมการเปลี่ยนเฟรม
                self.last_frame_time = current_time
                self.current_frame = (self.current_frame + 1) % len(self.frames)

            if self.frames[0]:  # Check if frames exist
                self.screen.blit(self.frames[self.current_frame], (0, 0))
            else:
                self.screen.fill((100, 100, 100))  # Gray background if no frames

            # Draw the bridge and target circle
            pygame.draw.rect(self.screen, (200, 150, 120), bridge_rect)
            pygame.draw.circle(self.screen, (255, 0, 0), target_circle_center, target_circle_radius, 2)

            # Display floating images
            for floating in self.floating_images[:]:
                floating['y'] += floating['float_speed']
                floating['alpha'] -= 5
                floating_surface = floating['image'].copy()
                floating_surface.set_alpha(max(0, floating['alpha']))
                self.screen.blit(floating_surface, (floating['x'] - self.width(0.075), floating['y']))

                if floating['alpha'] <= 0:
                    self.floating_images.remove(floating)

            for note in self.songmap[tick]:
                spiritlist.append(note)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit", self.statistics
                elif event.type == pygame.KEYDOWN and self.control_mode == "Keyboard":
                    if event.key == pygame.K_p:
                        result = self.pause_menu()
                        if result == 1:
                            return 'exitpause', self.statistics  # Exit game
                        elif result == 0:
                            return 'exit', self.statistics
                    if event.key == pygame.K_1:
                        hit_type = 0
                    elif event.key == pygame.K_2:
                        hit_type = 1
                    else:
                        continue
                    self.process_hit(hit_type, spiritlist, target_circle_center, target_circle_radius)

            for spirit in sorted(spiritlist, key=lambda obj: obj.layer):
                condition = spirit.activate()
                if condition in ['delete', 'miss']:
                    spiritlist.remove(spirit)
                    if condition == 'miss':
                        self.evaluate('miss')

            font = pygame.font.Font(None, 36)
            score_render = font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
            self.screen.blit(score_render, (self.width(0.8), self.hight(0.05)))
            combo_render = font.render(f"combo: {int(self.combo)}", True, (255, 255, 255))
            self.screen.blit(combo_render, (self.width(0.8), self.hight(0.10)))
            pygame.display.flip()

            self.current_tick += 1
            clock.tick(self.fps)
    def width(self, ratio):
        return int(self.SCREEN_WIDTH * ratio)

    def hight(self, ratio):
        return int(self.SCREEN_HEIGHT * ratio)