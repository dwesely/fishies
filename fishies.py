"""
Source : http://arcade.academy/examples/procedural_caves_cellular.html#procedural-caves-cellular
For more information, see:
https://gamedevelopment.tutsplus.com/tutorials/generate-random-cave-levels-using-cellular-automata--gamedev-9664

Using these sprites:
https://www.kenney.nl/assets/fish-pack

Using these tiles:
https://opengameart.org/content/topdown-tileset

"""

import random
import arcade
import timeit
import os
import math
import procedural_caves_cellular as caves

# Sprite scaling. Make this larger, like 0.5 to zoom in and add
# 'mystery' to what you can see. Make it smaller, like 0.1 to see
# more of the map.
SPRITE_SCALING = 0.25
SPRITE_SIZE = 64 * SPRITE_SCALING

# How big the grid is
GRID_WIDTH = 20#400
GRID_HEIGHT = 20#300

MAP_WIDTH = caves.GRID_WIDTH * caves.SPRITE_SIZE
MAP_HEIGHT = caves.GRID_HEIGHT * caves.SPRITE_SIZE

# Parameters for cellular automata
CHANCE_TO_START_ALIVE = 0.3
DEATH_LIMIT = 3
BIRTH_LIMIT = 4
NUMBER_OF_STEPS = 4

# How fast the player moves
MOVEMENT_SPEED = 5
ANGLE_SPEED = 5

# How close the player can get to the edge before we scroll.
VIEWPORT_MARGIN = 300

# How big the window is
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Fishies"

FRIENDLY_FISHY_COUNT = 3

game = None

def scale_up(factor):
    global GRID_HEIGHT
    global GRID_WIDTH
    global FRIENDLY_FISHY_COUNT
    global MAP_HEIGHT
    global MAP_WIDTH
    global game

    GRID_HEIGHT = int(GRID_HEIGHT * factor)
    GRID_WIDTH = int(GRID_WIDTH * factor)
    FRIENDLY_FISHY_COUNT = int(FRIENDLY_FISHY_COUNT * factor)

    MAP_WIDTH = GRID_WIDTH * SPRITE_SIZE
    MAP_HEIGHT = GRID_HEIGHT * SPRITE_SIZE

    AutoFish.fishy_set = set()

    game.setup()
    arcade.run()

class Player(arcade.Sprite):
    '''
    Your Fish
    '''
    ACCELERATION = .2
    TOP_SPEED = 5

    def __init__(self, image = "kenney_fishpack/PNG/Default size/fishTile_079.png", scale = SPRITE_SCALING):
        # Call the parent init
        super().__init__(image, scale)

        # Create a variable to hold our speed. 'angle' is created by the parent
        self.speed_x = 0
        self.speed_y = 0
        self.turn_speed = 0
        self.status = 1


class AutoFish(arcade.Sprite):
    '''
    AI Fish
    '''
    fishy_set = set()
    TOP_SPEED = 5
    ACCELERATION = 0.05
    TURN_ACCELERATION = 2
    TURN_CHANCE = .01
    HARD_TURN = 60
    HARD_TURN_SPEED = 2
    DECCELERATE_CHANCE = .02
    #random.random()
    fish_tiles = {'green':'kenney_fishpack/PNG/Default size/fishTile_072.png',
                  'purple': 'kenney_fishpack/PNG/Default size/fishTile_074.png',
                  'blue': 'kenney_fishpack/PNG/Default size/fishTile_076.png',
                  'orange': 'kenney_fishpack/PNG/Default size/fishTile_080.png',
                  'puffer': 'kenney_fishpack/PNG/Default size/fishTile_100.png',
                  'eel': 'kenney_fishpack/PNG/Default size/fishTile_102.png'
                   }

    def __init__(self, tile = random.choice(['green','purple','blue','orange','puffer','eel']), scale = SPRITE_SCALING, friendly = True):
        image = AutoFish.fish_tiles.get(tile)
        # Call the parent init
        super().__init__(image, scale)

        # Create a variable to hold our speed. 'angle' is created by the parent
        self.speed = 0
        self.turn_speed = 0
        self.scalar = random.random()
        self.status = 1

        AutoFish.fishy_set.add(self)



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.grid = None
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None
        self.view_bottom = 0
        self.view_left = 0
        self.draw_time = 0
        self.physics_engine = None
        self.game_start_time = timeit.default_timer()
        self.game_stop_time = None

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.water_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()

        # Create cave system using a 2D grid
        self.grid = caves.create_grid(GRID_WIDTH, GRID_HEIGHT)
        caves.initialize_grid(self.grid)
        for step in range(NUMBER_OF_STEPS):
            self.grid = caves.do_simulation_step(self.grid)

        # Create sprites based on 2D grid
        for row in range(GRID_HEIGHT):
            column = 0
            while column < GRID_WIDTH:
                while row > 0 and row < GRID_HEIGHT - 1 and column > 0 and column < GRID_WIDTH - 1 and self.grid[row][column] == 0:
                    column += 1
                start_column = column
                while column < GRID_WIDTH and (self.grid[row][column] == 1 or row in {0, GRID_HEIGHT - 1} or column in {0, GRID_WIDTH - 1}):
                    column += 1
                end_column = column - 1

                column_count = end_column - start_column + 1
                column_mid = (start_column + end_column) / 2

                wall = arcade.Sprite("topdown_tiles/tiles/beach0/straight/0/0.png", SPRITE_SCALING,
                                     repeat_count_x=column_count)
                wall.center_x = column_mid * SPRITE_SIZE + SPRITE_SIZE / 2
                wall.center_y = row * SPRITE_SIZE + SPRITE_SIZE / 2
                wall.width = SPRITE_SIZE * column_count
                self.wall_list.append(wall)

        for row in range(GRID_HEIGHT):
            column = 0
            while column < GRID_WIDTH:
                while column < GRID_WIDTH and (self.grid[row][column] == 1 or row in {0, GRID_HEIGHT - 1} or column in {0, GRID_WIDTH - 1}):
                    column += 1
                start_column = column
                while column < GRID_WIDTH and self.grid[row][column] == 0 and row not in {0, GRID_HEIGHT - 1} and column not in {0, GRID_WIDTH - 1}:
                    column += 1
                end_column = column - 1

                column_count = end_column - start_column + 1
                column_mid = (start_column + end_column) / 2

                water = arcade.Sprite("topdown_tiles/tiles/deep0/straight/0/0.png", SPRITE_SCALING,
                                     repeat_count_x=column_count)
                water.center_x = column_mid * SPRITE_SIZE + SPRITE_SIZE / 2
                water.center_y = row * SPRITE_SIZE + SPRITE_SIZE / 2
                water.width = SPRITE_SIZE * column_count
                self.water_list.append(water)

        # Set up the player
        self.player_sprite = Player()
        self.player_list.append(self.player_sprite)
        for i in range(FRIENDLY_FISHY_COUNT):
            self.player_list.append(AutoFish(tile = random.choice(['green','purple','blue','orange','puffer','eel'])))

        # Randomly place the players. If we are in a wall, repeat until we aren't.
        for player in self.player_list:
            placed = False
            while not placed:

                # Randomly position
                max_x = GRID_WIDTH * SPRITE_SIZE
                max_y = GRID_HEIGHT * SPRITE_SIZE
                player.center_x = random.randrange(max_x)
                player.center_y = random.randrange(max_y)

                # Are we in a wall?
                walls_hit = arcade.check_for_collision_with_list(player, self.wall_list)
                if len(walls_hit) == 0:
                    # Not in a wall! Success!
                    placed = True

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)

    def on_draw(self):
        """ Render the screen. """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Draw the sprites
        self.wall_list.draw()
        self.water_list.draw()
        self.player_list.draw()

        # Draw info on the screen
        chomped_fishies = [fishy for fishy in AutoFish.fishy_set if not fishy.status]

        output = f"Chomped Fishies: {len(chomped_fishies)} out of {len(AutoFish.fishy_set)}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         self.height - 20 + self.view_bottom,
                         arcade.color.WHITE, 16)

        if not self.game_stop_time:
            self.draw_time = timeit.default_timer() - self.game_start_time
        else:
            self.draw_time = self.game_stop_time - self.game_start_time

        output = f"Game time: {self.draw_time:.1f} seconds"
        arcade.draw_text(output,
                         self.view_left + 20,
                         self.height - 40 + self.view_bottom,
                         arcade.color.WHITE, 16)



        output = f"Movement: {self.player_sprite.change_y:.0f},{self.player_sprite.change_x:.0f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         self.height - 60 + self.view_bottom,
                         arcade.color.WHITE, 16)

        for fishy in chomped_fishies:
            arcade.draw_text("CHOMP",
                             fishy.center_x,
                             fishy.center_y,
                             arcade.color.BLACK,
                             10,
                             width=200,
                             align="center",
                             anchor_x="center",
                             anchor_y="center",
                             rotation=fishy.angle)
        if len(chomped_fishies) == len(AutoFish.fishy_set):
            if not self.game_stop_time:
                self.game_stop_time = timeit.default_timer()
                self.player_sprite.status = 0

            arcade.draw_text("All Chomped!\nNew game? (y)",
                             self.player_sprite.center_x,
                             self.player_sprite.center_y,
                             arcade.color.BLACK,
                             24,
                             width=300,
                             align="center",
                             anchor_x="center",
                             anchor_y="center",
                             rotation=0)
        else:
            self.game_stop_time = None
            self.player_sprite.status = 1


        self.draw_time = timeit.default_timer() - draw_start_time

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key in {arcade.key.W, arcade.key.UP}:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key in {arcade.key.S, arcade.key.DOWN}:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key in {arcade.key.A, arcade.key.LEFT}:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key in {arcade.key.D, arcade.key.RIGHT}:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif self.player_sprite.status == 0 and key == arcade.key.Y:
            scale_up(1.5)
        elif key == arcade.key.M:
            self.player_sprite.right = MAP_WIDTH/2
            self.player_sprite.bottom = MAP_HEIGHT/2


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key in {arcade.key.W, arcade.key.UP} or key in {arcade.key.S, arcade.key.DOWN}:
            self.player_sprite.change_y = 0
        elif key in {arcade.key.A, arcade.key.LEFT} or key in {arcade.key.D, arcade.key.RIGHT}:
            self.player_sprite.change_x = 0
            self.player_sprite.change_x = 0


    def on_resize(self, width, height):

        arcade.set_viewport(self.view_left,
                            self.width + self.view_left,
                            self.view_bottom,
                            self.height + self.view_bottom)

    def update(self, delta_time):
        """ Movement and game logic """

        start_time = timeit.default_timer()

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()


        if self.player_sprite.change_x > 0:
            if self.player_sprite.change_y > 0:
                # up-right
                self.player_sprite.change_angle = 45
            elif self.player_sprite.change_y < 0:
                # down-right
                self.player_sprite.change_angle = 315
            else:
                # right
                self.player_sprite.change_angle = 0
        elif self.player_sprite.change_x < 0:
            if self.player_sprite.change_y > 0:
                # up-left
                self.player_sprite.change_angle = 135
            elif self.player_sprite.change_y < 0:
                # down-left
                self.player_sprite.change_angle = 225
            else:
                # left
                self.player_sprite.change_angle = 180
        elif self.player_sprite.change_y > 0:
            # up
            self.player_sprite.change_angle = 90
        elif self.player_sprite.change_y < 0:
            # down
            self.player_sprite.change_angle = 270

        if self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0:
            self.player_sprite.angle = self.player_sprite.change_angle

        # --- update fishies
        for fishy in [fishy for fishy in AutoFish.fishy_set if fishy.status]:
            player_hit = arcade.check_for_collision(fishy, self.player_sprite)
            if player_hit:
                fishy.status = 0
                continue


            # Convert angle in degrees to radians.
            angle_rad = math.radians(fishy.angle - 90)
            fishy_previous_x = fishy.center_x
            fishy_previous_y = fishy.center_y

            # Use math to find our change based on our speed and angle
            if random.random() < AutoFish.DECCELERATE_CHANCE * fishy.scalar:
                fishy.speed = AutoFish.ACCELERATION * fishy.scalar
            else:
                fishy.speed = min(AutoFish.TOP_SPEED, fishy.speed + AutoFish.ACCELERATION * fishy.scalar)
            fishy.center_x += -fishy.speed * math.sin(angle_rad)
            fishy.center_y += fishy.speed * math.cos(angle_rad)

            walls_hit = arcade.check_for_collision_with_list(fishy, self.wall_list)
            if len(walls_hit) > 0:
                if random.random() > 0.5:
                    fishy.angle = fishy.angle + AutoFish.HARD_TURN
                    fishy.speed = max(fishy.speed, AutoFish.HARD_TURN_SPEED * fishy.scalar)
                else:
                    fishy.angle = fishy.angle - AutoFish.HARD_TURN
                    fishy.speed = max(fishy.speed, AutoFish.HARD_TURN_SPEED * fishy.scalar)
                # fishy.speed = 0
                # fishy.turn_speed = fishy.turn_speed + AutoFish.TURN_ACCELERATION
                # fishy.angle = fishy.angle + fishy.turn_speed
                fishy.center_x = fishy_previous_x
                fishy.center_y = fishy_previous_y
            elif random.random() < AutoFish.TURN_CHANCE * fishy.scalar:
                if random.random() > 0.5:
                    fishy.angle = fishy.angle + AutoFish.HARD_TURN
                else:
                    fishy.angle = fishy.angle - AutoFish.HARD_TURN

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + WINDOW_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + WINDOW_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                self.width + self.view_left,
                                self.view_bottom,
                                self.height + self.view_bottom)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    global game
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()