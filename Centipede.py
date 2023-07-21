import arcade
from random import uniform
import math
import time


class Segment:
    def __init__(self, x_init, y_init, size_init, width_init, height_init):
        self.centerX = x_init
        self.centerY = y_init
        self.size = size_init
        self.window_width = width_init
        self.window_height = height_init
        self.xDir = 1
        self.speed = 5

    def update(self):
        # moves centipede segment
        self.centerX += self.xDir * self.speed
        # if segment is moving right and reaches edge of window, go down and reverse direction
        if self.xDir > 0 and self.centerX > self.window_width-self.size:
            self.centerY -= 2*self.size
            self.xDir *= -1
        # if segment is moving left and reaches edge of window, go down and reverse direction
        elif self.xDir < 0 and self.centerX < self.size:
            self.centerY -= 2*self.size
            self.xDir *= -1

    def display(self):
        arcade.draw_circle_filled(self.centerX, self.centerY, self.size, arcade.color.ELECTRIC_PURPLE)


class Centipede:
    def __init__(self, length_init, segsize_init, winwidth_init, winheight_init):
        self.centipede_list = []
        self.centipede_length = length_init
        self.segment_size = segsize_init
        self.window_width = winwidth_init
        self.window_height = winheight_init

        # populates centipede_list with segments
        i = 0
        x = 0
        while i <= self.centipede_length:
            self.centipede_list.append(Segment(x + self.segment_size, self.window_height - self.segment_size, 10, self.window_width, self.window_height))
            i += 1
            x += 20

    def hit_obstacle(self, obstacle):
        for segment in self.centipede_list:
            # hit detection
            if math.sqrt((segment.centerX - obstacle.centerX) ** 2 + (segment.centerY - obstacle.centerY) ** 2) <= segment.size/2 + obstacle.size/2:
                segment.centerY -= 2 * segment.size
                segment.xDir *= -1

    def game_over(self):
        for segment in self.centipede_list:
            if segment.centerY < self.window_height/6:  # if centipede reaches bottom of window, end game
                return True


class Torpedo:

    def __init__(self, x_init, y_init):
        self.centerX = x_init
        self.centerY = y_init
        self.size = 5

    def update(self):
        self.centerY += 3

    def display(self):
        arcade.draw_circle_filled(self.centerX, self.centerY, self.size, arcade.color.ANTI_FLASH_WHITE)


class Obstacle:

    def __init__(self, x_init, y_init):
        self.centerX = x_init
        self.centerY = y_init
        self.size = 10

    def display(self):
        arcade.draw_circle_filled(self.centerX, self.centerY, self.size, arcade.color.RADICAL_RED)


class Main(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.radius = 25
        self.centerX = self.width/2
        self.centerY = self.radius
        self.moving_left = False
        self.moving_right = False
        self.torpedo_list = []
        self.obstacle_list = []
        self.obstacle_num = 50
        self.centipede = Centipede(10, 10, self.width, self.height)
        self.points = 0

        # populates obstacle_list
        i = 0
        while i <= self.obstacle_num:
            self.obstacle_list.append(Obstacle(uniform(0, width), uniform(height/4, height-20)))
            i += 1

    # called every time screen refreshes
    def on_draw(self):
        # clears screen every time it refreshes
        self.clear()

        # ends game if all segments are destroyed or if centipede reaches bottom of window
        if len(self.centipede.centipede_list) <= 0:
            self.win_game()
        elif self.centipede.game_over():
            self.lose_game()

        # player object
        arcade.draw_circle_filled(self.centerX, self.centerY, self.radius, arcade.color.UFO_GREEN)
        if self.moving_left:
            self.centerX -= 3
        elif self.moving_right:
            self.centerX += 3

        # displays objects
        for torpedo in self.torpedo_list:
            torpedo.display()
            torpedo.update()

        for obstacle in self.obstacle_list:
            obstacle.display()

        for segment in self.centipede.centipede_list:
            segment.display()
            segment.update()

        # checks if centipede hits obstacles to change direction
        for obstacle in self.obstacle_list:
            self.centipede.hit_obstacle(obstacle)

        arcade.draw_text("Points: " + str(self.points), 5, 5, arcade.color.ANTI_FLASH_WHITE, 30, 30, "left")

        self.hit()

    # key controls for player
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.LEFT:
            self.moving_left = True
        elif symbol == arcade.key.RIGHT:
            self.moving_right = True

        if symbol == arcade.key.SPACE:
            self.torpedo_list.append(Torpedo(self.centerX, self.centerY))

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LEFT:
            self.moving_left = False
        elif symbol == arcade.key.RIGHT:
            self.moving_right = False

    def hit(self):
        # checks if torpedo hits obstacles and deletes on collision
        for torpedo in self.torpedo_list:
            hit = False  # makes sure torpedo doesn't get removed twice when hitting 2 obstacles
            for obstacle in self.obstacle_list:
                if math.sqrt((obstacle.centerX-torpedo.centerX)**2 + (obstacle.centerY-torpedo.centerY)**2) <= torpedo.size+obstacle.size:
                    hit = True
                    self.points += 1
                    self.obstacle_list.remove(obstacle)
            if hit:
                self.torpedo_list.remove(torpedo)

        # checks if torpedo hits centipede, changes hit segment to obstacle
        for torpedo in self.torpedo_list:
            hit = False
            for segment in self.centipede.centipede_list:
                if math.sqrt((segment.centerX - torpedo.centerX) ** 2 + (segment.centerY - torpedo.centerY) ** 2) <= torpedo.size+segment.size:
                    hit = True
                    self.points += 1
                    self.centipede.centipede_list.remove(segment)
                    self.obstacle_list.append(Obstacle(segment.centerX, segment.centerY))
            if hit:
                self.torpedo_list.remove(torpedo)

    def win_game(self):
        arcade.draw_text("You win!", self.width / 2 - 250, self.height/2, arcade.color.ANTI_FLASH_WHITE, 100, 100, "left")
        self.obstacle_list.clear()
        self.torpedo_list.clear()
        self.radius = 0

    def lose_game(self):
        arcade.draw_text("You lose.", self.width / 2 - 250, self.height/2, arcade.color.ANTI_FLASH_WHITE, 100, 100, "left")
        self.obstacle_list.clear()
        self.torpedo_list.clear()
        self.radius = 0



# constructs object of type Main
arcade.window = Main(1000, 500, "Centipede")
arcade.run()


