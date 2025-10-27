import pygame, os, time, random, math, sys

IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "monster_images")

class Visualizer:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Monster Fusion Visualizer")
        self.font = pygame.font.SysFont("consolas", 32)
        self.smallfont = pygame.font.SysFont("consolas", 22)
        self.tinyfont = pygame.font.SysFont("consolas", 12)
        self.clock = pygame.time.Clock()
        self.bg_color = (20, 20, 25)  # dark mode is the best
        self.running = True

    def handle_events(self):
        """Handle pygame events to prevent crashes"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, 
                              pygame.MOUSEMOTION, pygame.KEYDOWN, pygame.KEYUP,
                              pygame.ACTIVEEVENT, pygame.VIDEORESIZE]:
                continue  # tried fixing crashing issue with pygame but didn't work. avoid clicking graphics window

    def find_monster_image(self, name):
        """handles duplicate fusions to make sure the original image is loaded"""
        # Try exact name first
        path = os.path.join(IMAGE_FOLDER, f"{name}.png")
        if os.path.exists(path):
            return path
            
        # For duplicate fusions try the base fusion name
        if "_" in name and name.count("_") >= 2:
            # Remove the number suffix and try base fusion name
            parts = name.split("_")
            base_name = "_".join(parts[:-1])  # Remove the number part
            path = os.path.join(IMAGE_FOLDER, f"{base_name}.png")
            if os.path.exists(path):
                return path
                
            # If still not found, try the original species combination
            if len(parts) >= 3:
                # For names like vapor_tigron_2, try vapor_tigron
                original_fusion = "_".join(parts[:2])
                path = os.path.join(IMAGE_FOLDER, f"{original_fusion}.png")
                if os.path.exists(path):
                    return path
        
        return None

    def load_image(self, name):
        """Load regular sized images"""
        path = self.find_monster_image(name)
        if path:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (200, 200))
        
        # Fallback image
        surf = pygame.Surface((200, 200))
        surf.fill((80, 80, 80))
        pygame.draw.rect(surf, (255, 50, 50), surf.get_rect(), 4)
        txt = self.smallfont.render("Missing", True, (255, 255, 255))
        surf.blit(txt, (60, 80))
        return surf

    def load_small_image(self, name):
        """Load smaller images for Pokedex view"""
        path = self.find_monster_image(name)
        if path:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (80, 80))
        
        # Fallback image
        surf = pygame.Surface((80, 80))
        surf.fill((60, 60, 70))
        pygame.draw.rect(surf, (200, 50, 50), surf.get_rect(), 2)
        txt = self.tinyfont.render("?", True, (200, 200, 200))
        surf.blit(txt, (35, 30))
        return surf

    # SUMMON PHASE
    def show_summon(self, monster_data):
        name = monster_data["name"]
        img = self.load_image(name)
        
        start_time = time.time()
        while time.time() - start_time < 3.0:  # Show for 3 seconds
            self.handle_events()  # Handle events to prevent crashing
            if not self.running:
                return
                
            self.screen.fill(self.bg_color)
            
            # Display monster image
            self.screen.blit(img, (self.WIDTH // 2 - 100, 150))
            
            # Display name
            name_label = self.font.render(f"{name}", True, (0, 200, 255))
            self.screen.blit(name_label, (self.WIDTH // 2 - name_label.get_width() // 2, 80))
            
            # Display stats
            stats_bg = pygame.Rect(self.WIDTH // 2 - 150, 400, 300, 200)
            pygame.draw.rect(self.screen, (40, 40, 50), stats_bg)
            pygame.draw.rect(self.screen, (100, 100, 120), stats_bg, 3)
            
            stats = [
                f"HP: {(monster_data['atk'] + monster_data['def']) // 2}",
                f"ATK: {monster_data['atk']}",
                f"DEF: {monster_data['def']}",
                f"SPD: {monster_data['spd']}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.smallfont.render(stat, True, (200, 200, 200))
                self.screen.blit(stat_text, (self.WIDTH // 2 - stat_text.get_width() // 2, 420 + i * 35))

            pygame.display.flip()
            self.clock.tick(30)  # Maintain 30 FPS

    # FUSION VISUALIZATION
    def show_fusion(self, mon1, mon2, result):
        # Use the actual monster images being fused
        # Extract the actual elements from the result monster's name
        result_parts = result["name"].split("_")
        if len(result_parts) >= 2:
            # For fused monsters, use the first element from the result
            elem1 = result["elements"][0] if "elements" in result else "fire"
            elem2 = result["elements"][1] if len(result["elements"]) > 1 else "water"
        else:
            elem1, elem2 = "fire", "water"
        
        m1_img = self.load_image(f"{elem1}_{mon1}")
        m2_img = self.load_image(f"{elem2}_{mon2}")
        result_img = self.load_image(result["name"])

        # Phase 1
        self.handle_events()
        if not self.running:
            return
            
        self.screen.fill(self.bg_color)
        self.screen.blit(m1_img, (200, 200))
        self.screen.blit(m2_img, (680, 200))
        txt = self.font.render(f"{elem1}_{mon1} + {elem2}_{mon2}", True, (255, 255, 255))
        self.screen.blit(txt, (self.WIDTH//2 - txt.get_width()//2, 100))
        pygame.display.flip()
        
        # Wait with event handling
        start_time = time.time()
        while time.time() - start_time < 1.2:
            self.handle_events()
            if not self.running:
                return
            self.clock.tick(30)

        # Flash
        for _ in range(3):
            self.handle_events()
            if not self.running:
                return
                
            self.screen.fill((255, 255, 255))
            pygame.display.flip()
            
            flash_start = time.time()
            while time.time() - flash_start < 0.1:
                self.handle_events()
                if not self.running:
                    return
                self.clock.tick(30)
                
            self.handle_events()
            if not self.running:
                return
                
            self.screen.fill(self.bg_color)
            self.screen.blit(m1_img, (200, 200))
            self.screen.blit(m2_img, (680, 200))
            pygame.display.flip()
            
            flash_start = time.time()
            while time.time() - flash_start < 0.1:
                self.handle_events()
                if not self.running:
                    return
                self.clock.tick(30)

        # Result
        self.handle_events()
        if not self.running:
            return
            
        self.screen.fill(self.bg_color)
        self.screen.blit(result_img, (self.WIDTH // 2 - 100, 200))
        label = self.font.render(f"Fusion Result: {result['name']}", True, (255, 255, 255))
        self.screen.blit(label, (self.WIDTH // 2 - label.get_width() // 2, 450))
        pygame.display.flip()
        
        # Wait with event handling
        start_time = time.time()
        while time.time() - start_time < 2.5:
            self.handle_events()
            if not self.running:
                return
            self.clock.tick(30)

    # BATTLE VISUALIZATION
    def show_battle(self, mon1, mon2, winner):
        m1_img = self.load_image(mon1)
        m2_img = self.load_image(mon2)

        hp1, hp2 = 100, 100

        def draw_hp(x, y, hp, color):
            pygame.draw.rect(self.screen, (80, 80, 80), (x, y, 200, 20))
            pygame.draw.rect(self.screen, color, (x, y, 2 * hp, 20))
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 200, 20), 2)

        # pre-battle delay phase
        self.handle_events()
        if not self.running:
            return
            
        self.screen.fill(self.bg_color)
        self.screen.blit(m1_img, (200, 240))
        self.screen.blit(m2_img, (680, 240))
        lbl = self.font.render("Battle Starting...", True, (255, 255, 255))
        self.screen.blit(lbl, (self.WIDTH // 2 - lbl.get_width() // 2, 80))
        pygame.display.flip()
        
        start_time = time.time()
        while time.time() - start_time < 1.5:
            self.handle_events()
            if not self.running:
                return
            self.clock.tick(30)

        # rounds
        for r in range(1, 6):
            self.handle_events()
            if not self.running:
                return
                
            self.screen.fill(self.bg_color)
            self.screen.blit(m1_img, (200, 240))
            self.screen.blit(m2_img, (680, 240))
            dmg1, dmg2 = random.randint(10, 20), random.randint(10, 20)
            hp2 = max(0, hp2 - dmg1)
            hp1 = max(0, hp1 - dmg2)
            draw_hp(220, 200, hp1, (0, 255, 0))
            draw_hp(860, 200, hp2, (255, 0, 0))
            lbl = self.font.render(f"Round {r}", True, (255, 255, 255))
            self.screen.blit(lbl, (self.WIDTH // 2 - 80, 80))
            pygame.display.flip()
            
            start_time = time.time()
            while time.time() - start_time < 1.5:
                self.handle_events()
                if not self.running:
                    return
                self.clock.tick(30)

        self.handle_events()
        if not self.running:
            return
            
        self.screen.fill(self.bg_color)
        winner_img = self.load_image(winner)
        self.screen.blit(winner_img, (self.WIDTH // 2 - 100, 200))
        lbl = self.font.render(f"Winner: {winner}", True, (255, 255, 0))
        self.screen.blit(lbl, (self.WIDTH // 2 - lbl.get_width() // 2, 450))
        pygame.display.flip()
        
        start_time = time.time()
        while time.time() - start_time < 3.5:
            self.handle_events()
            if not self.running:
                return
            self.clock.tick(30)

    # ENCYCLOPEDIA VISUALIZATION
    def show_pokedex(self, encyclopedia):
        start_time = time.time()
        while time.time() - start_time < 3.0:  # Show for 3 seconds
            self.handle_events()
            if not self.running:
                return
                
            self.screen.fill(self.bg_color)
            
            # Title
            title = self.font.render("MONSTER DEX", True, (255, 255, 255))
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 20))
            
            # Define all possible monsters (base + fusions)
            base_combinations = []
            for element in ["fire", "water", "grass"]:
                for monster in ["cat", "dog", "rat"]:
                    base_combinations.append(f"{element}_{monster}")
            
            fusion_combinations = [
                "vapor_tigron", "vapor_cerberus", "vapor_felhound", "vapor_scavlynx", "vapor_burrowfang", "vapor_gnawlord",
                "blaze_tigron", "blaze_cerberus", "blaze_felhound", "blaze_scavlynx", "blaze_burrowfang", "blaze_gnawlord", 
                "mud_tigron", "mud_cerberus", "mud_felhound", "mud_scavlynx", "mud_burrowfang", "mud_gnawlord",
                "inferno_tigron", "inferno_cerberus", "inferno_felhound", "inferno_scavlynx", "inferno_burrowfang", "inferno_gnawlord",
                "torrent_tigron", "torrent_cerberus", "torrent_felhound", "torrent_scavlynx", "torrent_burrowfang", "torrent_gnawlord",
                "thorn_tigron", "thorn_cerberus", "thorn_felhound", "thorn_scavlynx", "thorn_burrowfang", "thorn_gnawlord"
            ]
            
            all_monsters = base_combinations + fusion_combinations
            
            # Display in a grid
            x_start, y_start = 40, 70
            slot_width = 120
            slot_height = 120
            cols = 8
            rows = 5
            
            for i, monster_name in enumerate(all_monsters):
                if i >= cols * rows:
                    break
                    
                row = i // cols
                col = i % cols
                x = x_start + col * slot_width
                y = y_start + row * slot_height
                
                # Draw slot background
                slot_rect = pygame.Rect(x, y, slot_width - 10, slot_height - 10)
                pygame.draw.rect(self.screen, (40, 40, 50), slot_rect)
                pygame.draw.rect(self.screen, (100, 100, 120), slot_rect, 2)
                
                # Check if discovered
                discovered = any(key.startswith(monster_name) for key in encyclopedia.keys())
                
                if discovered:
                    # Find the actual discovered monster name
                    actual_name = None
                    for key in encyclopedia.keys():
                        if key.startswith(monster_name):
                            actual_name = key
                            break
                    
                    if actual_name:
                        # Show actual image and name
                        img = self.load_small_image(actual_name)
                        self.screen.blit(img, (x + (slot_width - 10 - 80) // 2, y + 5))
                        
                        # Display name (shortened if too long)
                        display_name = actual_name
                        if len(display_name) > 12:
                            display_name = display_name[:10] + ".."
                        name_text = self.tinyfont.render(display_name, True, (200, 255, 200))
                        self.screen.blit(name_text, (x + (slot_width - 10) // 2 - name_text.get_width() // 2, y + 90))
                else:
                    # Show silhouette and ???
                    silhouette = pygame.Surface((80, 80))
                    silhouette.fill((60, 60, 80))
                    
                    # Add question mark
                    question = self.tinyfont.render("???", True, (120, 120, 150))
                    self.screen.blit(silhouette, (x + (slot_width - 10 - 80) // 2, y + 5))
                    self.screen.blit(question, (x + (slot_width - 10) // 2 - question.get_width() // 2, y + 30))
                    
                    # Display ??? as name
                    name_text = self.tinyfont.render("???", True, (150, 150, 170))
                    self.screen.blit(name_text, (x + (slot_width - 10) // 2 - name_text.get_width() // 2, y + 90))

            unique_discoveries = set()
            for monster_name in all_monsters:
                for key in encyclopedia.keys():
                    if key.startswith(monster_name):
                        unique_discoveries.add(monster_name)
                        break
            
            discovered_count = len(unique_discoveries)
            total_count = 36
            stats_text = self.smallfont.render(f"Discovered: {discovered_count}/{total_count}", True, (255, 255, 255))
            self.screen.blit(stats_text, (self.WIDTH // 2 - stats_text.get_width() // 2, self.HEIGHT - 40))
            
            pygame.display.flip()
            self.clock.tick(30)