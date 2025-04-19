import pygame
import pygame_gui
import logging
import os
import json
import time
from src.render.render_sprite import load_sprite
from src.render.error_handler import error_handler, ErrorLevel
from src.render.sound_manager import sound_manager

PLAYER_FOLDER = "data/player"
OPTIONS_FILE = "data/options.json"

class GameScreen:
    def __init__(self, screen, manager, change_scene, game_manager, level_name, level_folder):
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene
        self.game_manager = game_manager
        self.level_name = level_name
        self.level_number = level_name.split("_")[0]
        self.current_robot = None
        self.folder = level_folder
        self.last_score = 0
        self.score_overlay_visible = False
        self.player_name = self.get_player_name()

        self.game_manager.load_level(level_name)

        if not self.game_manager.current_level:  # Level loading failed
            logging.error(f"Level '{level_name}' could not be loaded. Returning to level select.")
            self.change_scene("level_select")
            return

        self.tile_size = self.game_manager.current_level.tile_size
        self.create_ui()


    def create_ui(self):
        """Creates the UI elements for the game screen."""
        width, height = self.screen.get_size()
        sidebar_width = int(width * 0.35)
        popup_width = 500
        popup_height = 300

        # UI Panel (Left Side Menu)
        self.ui_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (sidebar_width, height)),
            manager=self.manager,
            object_id="sidebar_panel"
        )

        # Level Name Display
        self.level_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (sidebar_width - 40, 25)),
            text=f"Level: {self.level_name.split("_", 1)[1]}",
            manager=self.manager,
            container=self.ui_panel,
            object_id="label"
        )

        # Dynamic Objective List (Scrollable)
        self.objective_list = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 50), (sidebar_width - 40, 135)), #50 more
            html_text="",  # Placeholder
            manager=self.manager,
            container=self.ui_panel,
            object_id="objective_list"
        )

        # Coding area (Text Editor)
        self.code_input = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((10, 200), (sidebar_width - 40, height - 350)),
            manager=self.manager,
            container=self.ui_panel,
            object_id="code_editor"
        )
        self.update_code_input()

        # Buttons
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, self.code_input.get_relative_rect().height + 225), (sidebar_width / 2 - 40, 40)),
            text="Play",
            manager=self.manager,
            container=self.ui_panel,
            object_id="good_button"
        )

        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.play_button.get_relative_rect().width + 50, self.code_input.get_relative_rect().height + 225), (sidebar_width / 2 - 40, 40)),
            text="Reset",
            manager=self.manager,
            container=self.ui_panel,
            object_id="bad_button"
        )

        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, self.code_input.get_relative_rect().height + 275), (sidebar_width - 40, 50)),
            text="Exit",
            manager=self.manager,
            container=self.ui_panel,
            object_id="bad_button"
        )

        # Popup panel
        self.score_popup = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                (width//2 - popup_width//2, height//2 - popup_height//2),
                (popup_width, popup_height)
            ),
            manager=self.manager,
            visible=self.score_overlay_visible,
            object_id="score_popup",
            starting_height=9999,  # Always on top
        )

        self.score_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, popup_width-55, 40),
            text=f"Congratulations {self.player_name}!",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="title_small"
        )

        self.score_title_under = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 50, popup_width-55, 40),
            text="You have completed the level!",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="subtitle"
        )

        self.steps_display = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 100, popup_width-55, 40),
            text="Steps Taken: 0",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="label"
        )

        self.collectables_display = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 130, popup_width-55, 40),
            text="Collectables: 0% (0/0)",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="label"
        )

        self.score_display = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 160, popup_width-55, 40),
            text="Your Score: 0",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="label"
        )


        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 220, popup_width-55, 50),
            text="Submit Score",
            manager=self.manager,
            container=self.score_popup,
            visible=self.score_overlay_visible,
            object_id="good_button"
        )

        self.calculate_viewport()  # Calculate the viewport size (Radious of tiles rendered)


    def calculate_viewport(self):
        """Calculate how many tiles fit based on the available game area."""
        width, height = self.screen.get_size()

        # Exclude the side menu width
        game_area_width = width - self.ui_panel.get_relative_rect().width
        game_area_height = height

        # Find the smaller dimension to determine the square view radius
        min_dim = min(game_area_width, game_area_height)

        # Ensure odd sizes for the viewport
        self.tiles_x = min_dim // self.tile_size
        if self.tiles_x % 2 == 0:
            self.tiles_x -= 1
        self.tiles_y = min_dim // self.tile_size
        if self.tiles_y % 2 == 0:
            self.tiles_y -= 1


    def get_player_name(self):
        """Get the player's name from the options file."""
        try:
            with open(OPTIONS_FILE, 'r') as f:
                data = json.load(f)
                player_name = data["last_player"]
                if not player_name or not isinstance(player_name, str):
                    raise ValueError("Invalid player name in options file.")
                return player_name
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Options file not found or corrupted. Using default name.")
            return "Anonymous"
        except Exception as e:
            logging.error(f"Unexpected error reading options file: {e}")
            return "Anonymous"


    def handle_events(self, event):
        match event.type:
            case pygame.QUIT:
                self.game_manager.save_script(self.code_input.get_text(), self.player_name)
            case pygame_gui.UI_BUTTON_PRESSED:
                match event.ui_element:
                    case self.exit_button:  # Exit button
                        error_handler.dismiss_all()
                        self.game_manager.save_script(self.code_input.get_text(), self.player_name)
                        self.change_scene("level_select")

                    case self.play_button:  # Play button
                        error_handler.dismiss_all()
                        self.game_manager.save_script(self.code_input.get_text(), self.player_name)
                        self.code_input.disable()
                        self.code_input.set_text("Simulation running...\n\nScript editing is disabled.")
                        self.game_manager.start_game()

                    case self.reset_button:  # Reset button
                        error_handler.dismiss_all()
                        if not self.game_manager.is_running:
                            self.game_manager.save_script(self.code_input.get_text(), self.player_name)
                        self.game_manager.reset_level()
                        self.update_code_input()

                    case self.submit_button if self.submit_button:
                        score = self.game_manager.calculate_score()
                        self.save_score_to_leaderboard(score)
                        self.hide_score_popup()
                        self.change_scene("level_select")

            case pygame.KEYDOWN:  # Keyboard input
                if not self.code_input.is_focused and not self.score_overlay_visible:
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                        if not self.game_manager.is_running:
                            self.game_manager.save_script(self.code_input.get_text(), self.player_name)
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                self.game_manager.move_camera("up")
                            case pygame.K_DOWN | pygame.K_s:
                                self.game_manager.move_camera("down")
                            case pygame.K_LEFT | pygame.K_a:
                                self.game_manager.move_camera("left")
                            case pygame.K_RIGHT | pygame.K_d:
                                self.game_manager.move_camera("right")
                        if not self.game_manager.is_running:
                            self.update_code_input()
                    

    def update_code_input(self):
        if self.game_manager.camera_robot:
            self.code_input.enable()
            self.code_input.set_text(self.game_manager.load_script(self.player_name))
        else:
            self.code_input.disable()
            self.code_input.set_text("No bot selected\n\nSelect a bot to modify it's script.")
            

    def update(self, time_delta):
        self.manager.update(time_delta)
        # Check for level completion
        if (self.game_manager.is_running and 
            not self.game_manager.is_paused and  
            self.game_manager.check_completion()):

            score = self.game_manager.calculate_score()
            self.show_score_popup(score)
            self.game_manager.is_running = False  # Stop the game
        

    def render(self):
        """Render the game screen."""
        self.screen.fill((0, 0, 0))
        self.update_objectives()

        if not self.game_manager.current_level:
            self.change_scene("level_select")
            logging.error("No level loaded, returning to level select")
            return

        # Get the grid boundaries
        sidebar_width = self.ui_panel.get_relative_rect().width
        grid_width = self.tiles_x * self.tile_size
        grid_height = self.tiles_y * self.tile_size

        grid_x = sidebar_width + ((self.screen.get_width() - sidebar_width - grid_width) // 2)
        grid_y = (self.screen.get_height() - grid_height) // 2

        # Draw a border around the grid
        border_color = (255, 255, 255)  # White border
        border_thickness = 3
        pygame.draw.rect(self.screen, border_color, (grid_x - border_thickness, grid_y - border_thickness, grid_width + 2 * border_thickness, grid_height + 2 * border_thickness), border_thickness)

        self.render_level(grid_x, grid_y)  # Pass adjusted position
        self.manager.draw_ui(self.screen)


    def update_objectives(self):
        """
        Update the objective list based on the current level's objectives.
        """
        new_text = ""

        def format_objective(text, completed, total):
            """Helper function to color completed objectives green."""
            if (completed >= total):
                return f"<font color='#00FF00'>{text} ({completed}/{total})</font><br>"
            return f"{text} ({completed}/{total})<br>"

        if self.game_manager.current_level.objectives["charge_pads"] > 0:
            new_text += format_objective(
                "Charge bots",
                self.game_manager.completed_objectives["charge_pads"],
                self.game_manager.current_level.objectives["charge_pads"]
            )

        if self.game_manager.current_level.objectives["crates_small"] > 0:
            new_text += format_objective(
                "Deliver crates S",
                self.game_manager.completed_objectives["crates_small"],
                self.game_manager.current_level.objectives["crates_small"]
            )

        if self.game_manager.current_level.objectives["crates_large"] > 0:
            new_text += format_objective(
                "Deliver crates L",
                self.game_manager.completed_objectives["crates_large"],
                self.game_manager.current_level.objectives["crates_large"]
            )

        if self.game_manager.current_level.objectives["terminals"] > 0:
            new_text += format_objective(
                "Configure terminals",
                self.game_manager.completed_objectives["terminals"],
                self.game_manager.current_level.objectives["terminals"]
            )

        if self.game_manager.current_level.objectives["collectables"] > 0:
            new_text += format_objective(
                "(Opt) Collect drives",
                self.game_manager.completed_objectives["collectables"],
                self.game_manager.current_level.objectives["collectables"]
            )

        # Only update if text has changed
        if new_text != self.objective_list.html_text:
            current_scroll = 0  # Preserve the scroll position
            if self.objective_list.scroll_bar is not None:
                current_scroll = self.objective_list.scroll_bar.scroll_position  

            self.objective_list.set_text(new_text)
            self.objective_list.rebuild()

            if self.objective_list.scroll_bar is not None and self.objective_list.scroll_bar.bottom_limit > 0:
                self.objective_list.scroll_bar.set_scroll_from_start_percentage(
                    current_scroll / self.objective_list.scroll_bar.bottom_limit
                )

    def show_score_popup(self, score):
        """Show the score submission popup"""
        error_handler.dismiss_all()  # Close all error popups
        self.score_overlay_visible = True
        self.last_score = score
        self.score_popup.show()
        self.score_title.show()
        self.score_title_under.show()
        self.score_display.show()
        self.score_display.set_text(f"Your Score: {score}")
        self.steps_display.set_text(f"Steps Taken: {self.game_manager.steps_taken}")
        if self.game_manager.current_level.objectives["collectables"] > 0:
            # Show collectables only if there are any
            self.collectables_display.set_text(f"Drives: {int(self.game_manager.completed_objectives['collectables'] / self.game_manager.current_level.objectives['collectables'] * 100)}% ({self.game_manager.completed_objectives['collectables']}/{self.game_manager.current_level.objectives['collectables']})")
        else:
            self.collectables_display.set_text("Drives: None available")
        self.submit_button.show()
        
        # Disable other UI elements
        self.code_input.disable()
        self.play_button.disable()
        self.reset_button.disable()
        self.exit_button.disable()
        
        # Stop the game
        self.game_manager.is_running = False


    def hide_score_popup(self):
        """Hide the score popup"""
        self.score_overlay_visible = False
        self.score_popup.hide()
        self.score_title.hide()
        self.score_title_under.hide()
        self.score_display.hide()
        self.submit_button.hide()
        
        # Re-enable other UI elements
        self.code_input.enable()
        self.play_button.enable()
        self.reset_button.enable()
        self.exit_button.enable()


    def save_score_to_leaderboard(self, score):
        """Save score to the level's leaderboard with robust error handling"""
        leaderboard_file = os.path.join("data", "level", self.level_name, "leaderboard.json")
        leaderboard_dir = os.path.dirname(leaderboard_file)
        
        try:
            # Ensure directory exists
            os.makedirs(leaderboard_dir, exist_ok=True)
            
            # Initialize empty leaderboard
            leaderboard = []
            
            # Try to load existing leaderboard if file exists
            if os.path.exists(leaderboard_file):
                try:
                    with open(leaderboard_file, 'r') as f:
                        file_content = f.read().strip()
                        if file_content:  # Only parse if file isn't empty
                            leaderboard = json.loads(file_content)
                            # Validate it's a list
                            if not isinstance(leaderboard, list):
                                logging.warning("Leaderboard file corrupted - not a list, resetting")
                                leaderboard = []
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logging.warning(f"Leaderboard file corrupted - resetting (error: {e})")
                    leaderboard = []
                except Exception as e:
                    logging.error(f"Unexpected error reading leaderboard: {e}")
                    leaderboard = []

            percentage_collectables = int(self.game_manager.completed_objectives["collectables"] / self.game_manager.current_level.objectives["collectables"] * 100 if self.game_manager.current_level.objectives["collectables"] > 0 else 0)
            
            # Add new entry with timestamp
            leaderboard.append({
                "name": self.player_name,
                "score": score,
                "steps_taken": self.game_manager.steps_taken,
                "collectables": percentage_collectables,
                "timestamp": int(time.time())  # Using Unix timestamp
            })
            
            # Sort by score (ascending - lower is better) then by timestamp (older first)
            leaderboard.sort(key=lambda x: (x["score"], x["timestamp"]))
            
            # Save back with atomic write pattern
            temp_file = leaderboard_file + ".tmp"
            try:
                with open(temp_file, 'w') as f:
                    json.dump(leaderboard, f, indent=4)
                
                if os.path.exists(leaderboard_file):
                    os.replace(temp_file, leaderboard_file)
                else:
                    os.rename(temp_file, leaderboard_file)
                    
            except Exception as e:
                logging.error(f"Failed to write leaderboard file: {e}")
                try:
                    os.remove(temp_file)
                except:
                    pass

            # Update the player highest level on it's file
            player_file = os.path.join(PLAYER_FOLDER, f"{self.player_name}.json")
            try:
                if os.path.exists(player_file):
                    with open(player_file, 'r') as f:
                        player_data = json.load(f)
                    player_data["highest_level"] = max(player_data.get("highest_level", 0), int(self.level_number))
                else:
                    player_data = {"highest_level": int(level_number)}

                with open(player_file, 'w') as f:
                    json.dump(player_data, f, indent=4)
            except Exception as e:
                logging.error(f"Failed to update player file: {e}")
                
        except Exception as e:
            logging.error(f"Critical error saving leaderboard: {e}")
            try:
                with open(leaderboard_file, 'w') as f:
                    json.dump([], f)
            except Exception as e2:
                logging.critical(f"Failed to create empty leaderboard file: {e2}")

            
    def render_level(self, grid_x, grid_y):        
        camera_x, camera_y = self.game_manager.current_level.get_camera_position()

        half_x = self.tiles_x // 2
        half_y = self.tiles_y // 2

        for y in range(-half_y, half_y + 1):
            for x in range(-half_x, half_x + 1):
                tile_x = camera_x + x
                tile_y = camera_y + y

                screen_x = grid_x + (x + half_x) * self.tile_size
                screen_y = grid_y + (y + half_y) * self.tile_size

                if (0 <= tile_x < self.game_manager.current_level.width and 0 <= tile_y < self.game_manager.current_level.height):
                    tile = self.game_manager.current_level.tiles[tile_y][tile_x]

                    tile_sprite = pygame.transform.scale(tile.image, (self.tile_size, self.tile_size))
                    self.screen.blit(tile_sprite, (screen_x, screen_y))

                    missing_sprite_colors = {
                        "tile": '#FF0000FF',
                        "ground": '#1AFF00FF', 
                        "air": '#00EEFFFF',
                        "camera": '#FFFFFFFF'
                    }

                    for height, color in missing_sprite_colors.items():
                        entity = tile.entities.get(height)
                        if entity:
                            entity_name = entity.__class__.__name__.lower()
                            match entity_name:
                                case "crate":
                                    if entity.small:
                                        sprite_name = f"{entity_name}_small.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "crategen":
                                    if entity.crate_type == "small":
                                        sprite_name = f"{entity_name}_small"
                                    else:
                                        sprite_name = f"{entity_name}"
                                    if entity.crate_count <= 0:
                                        sprite_name += "_empty.png"
                                    else:
                                        if entity.active:
                                            sprite_name += "_on.png"
                                        else:
                                            sprite_name += ".png"
                                case "cratedel":
                                    if entity.active:
                                        sprite_name = f"{entity_name}_on.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "trap":
                                    if entity.active:
                                        sprite_name = f"{entity_name}_on.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "red":
                                    if entity.crate == None:
                                        sprite_name = f"{entity_name}.png"
                                    elif entity.crate.small == "small":
                                        sprite_name = f"{entity_name}_small.png"
                                    else:
                                        sprite_name = f"{entity_name}_big.png"
                                case "green":
                                    if entity.crate == None:
                                        sprite_name = f"{entity_name}.png"
                                    else:
                                        sprite_name = f"{entity_name}_small.png"
                                case "inputter":
                                    if not entity.activated:
                                        match entity.operation:
                                            case "+":
                                                sprite_name = f"{entity_name}_add.png"
                                            case "-":
                                                sprite_name = f"{entity_name}_sub.png"
                                            case "*":
                                                sprite_name = f"{entity_name}_mul.png"
                                            case "/":
                                                sprite_name = f"{entity_name}_div.png"
                                    else:
                                        sprite_name = f"{entity_name}_done.png"
                                case "collectable":
                                    if entity.height == 1:
                                        sprite_name = f"{entity_name}.png"
                                    else:
                                        sprite_name = f"{entity_name}_air.png"
                                case _:
                                    sprite_name = f"{entity.__class__.__name__.lower()}.png"

                            sprite = load_sprite(sprite_name, self.tile_size, color_on=color, color_off='#010001', entity=entity)
                            # N = Up, E = Right, S = Down, W = Left
                            rotation = {"N": 0, "E": 270, "S": 180, "W": 90}.get(entity.direction, 0)
                            sprite = pygame.transform.rotate(sprite, rotation)
                            self.screen.blit(sprite, (screen_x, screen_y))

                else:
                    pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, self.tile_size - 1, self.tile_size - 1))


    def resize(self):
        last_script = self.code_input.get_text()  # Preserve the script
        self.game_manager.save_script(last_script, self.player_name)  # Save the script to a file
        self.manager.clear_and_reset()
        self.calculate_viewport()
        self.create_ui()
        self.code_input.set_text(last_script)

        # Recreate score popup UI
        width, height = self.screen.get_size()
        popup_width = 400
        popup_height = 300
        
        # Recreate overlay
        self.score_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Only recreate popup if it was visible
        if self.score_overlay_visible and self.last_score is not None:
            self.show_score_popup(self.last_score)


    def destroy(self):
        logging.debug("Destroying game scene")
        # Save last script before that
        last_script = self.code_input.get_text()
        self.game_manager.save_script(last_script, self.player_name)
        self.game_manager.is_paused = False
        self.game_manager.is_running = False
        self.manager.clear_and_reset()
