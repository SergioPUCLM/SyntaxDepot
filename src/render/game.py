import pygame
import pygame_gui
import logging
from src.render.render_sprite import load_sprite


class GameScreen:
    def __init__(self, screen, manager, change_scene, game_manager, level_name):
        self.screen = screen
        self.manager = manager
        self.change_scene = change_scene
        self.game_manager = game_manager
        self.level_name = level_name

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

        logging.debug(f"Viewport: {self.tiles_x} x {self.tiles_y} tiles")


    def handle_events(self, event):
        match event.type:
            case pygame_gui.UI_BUTTON_PRESSED:
                match event.ui_element:
                    case self.exit_button:
                        self.change_scene("level_select")
                    case self.play_button:
                        print("Play pressed! (Will trigger script execution)")
                        self.game_manager.start_game()
                    case self.reset_button:
                        print("Reset pressed! (Will reset level state)")
                        self.game_manager.reset_level()
            case pygame.KEYDOWN:
                # If the code editor is focused, don't handle camera movement
                if not self.code_input.is_focused:
                    match event.key:
                        case pygame.K_UP:
                            self.game_manager.move_camera("up")
                        case pygame.K_DOWN:
                            self.game_manager.move_camera("down")
                        case pygame.K_LEFT:
                            self.game_manager.move_camera("left")
                        case pygame.K_RIGHT:
                            self.game_manager.move_camera("right")


    def update(self, time_delta):
        self.manager.update(time_delta)


    def render(self):
        """Render the game screen."""
        self.screen.fill((0, 0, 0))  # Clear the screen
        self.update_objectives()
        self.manager.draw_ui(self.screen)

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
                "(Opt) Collectables",
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
                                        sprite_name = f"{entity_name}_small.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "trap":
                                    if entity.active:
                                        sprite_name = f"{entity_name}_on.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "red":
                                    if entity.crate == "small":
                                        sprite_name = f"{entity_name}_small.png"
                                    elif entity.crate == "big":
                                        sprite_name = f"{entity_name}_big.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case "green":
                                    if entity.crate == "small":
                                        sprite_name = f"{entity_name}_small.png"
                                    else:
                                        sprite_name = f"{entity_name}.png"
                                case _:
                                    sprite_name = f"{entity.__class__.__name__.lower()}.png"

                            sprite = load_sprite(sprite_name, self.tile_size, color_on=color, color_off='#010001')
                            rotation = {"N": 0, "E": 90, "S": 180, "W": 270}.get(entity.direction, 0)
                            sprite = pygame.transform.rotate(sprite, rotation)
                            self.screen.blit(sprite, (screen_x, screen_y))

                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), (screen_x, screen_y, self.tile_size - 1, self.tile_size - 1))


    def resize(self):
        last_script = self.code_input.get_text()  # Preserve the script
        self.manager.clear_and_reset()
        self.calculate_viewport()
        self.create_ui()
        self.code_input.set_text(last_script)


    def destroy(self):
        logging.debug("Destroying game scene")
        self.manager.clear_and_reset()
