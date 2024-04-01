# -------------------------------------------------------------------

# 3/12/24

# -------------------------------------------------------------------

import pygame
from rich.console import Console 
from time import sleep
import math

# -------------------------------------------------------------------

console = Console()
pygame.init()
pygame.font.init()

# -------------------------------------------------------------------
# CONSTANTS

FONT_SIZE = 64

# Controls 
MOVE_LEFT = pygame.K_LEFT
MOVE_RIGHT = pygame.K_RIGHT

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 700
SCREEN_BG = 'black'
CLOCK_SPEED = 60

# Object Constants
PLAYER_WIDTH = 75
PLAYER_HEIGHT = 10
PLAYER_SPEED = 7
PLAYER_COLOR = 'red'
PLAYER_TOP = SCREEN_HEIGHT - PLAYER_HEIGHT - 10 #  the top of the rectangle
PLAYER_STARTX = 200

BALL_SIZE = 6
BALL_SPEED = 2
BALL_COLOR = 'white'

BALL_STARTX = 250
BALL_STARTY = 250

PLAYER_HIT_MODIFIER = 1.2
WALL_HIT_MODIFIER = 1
TOP_HIT_MODIFIER = 1

# -------------------------------------------------------------------
#  Lucas' Cringe mathematics class 101

class Vector2D:

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def multiply(self, num):
        return Vector2D(self.x * num, self.y * num)


# -------------------------------------------------------------------
# Entities

class Starship:
    def __init__(self):
        # Rect values
        self.width = PLAYER_WIDTH 
        self.height = PLAYER_HEIGHT
        self.xpos = PLAYER_STARTX #  Left 
        self.ypos = PLAYER_TOP
        self.move_amt = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.rect = None 

    def update(self):
        self.rect = (self.xpos, self.ypos, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.rect)

    def move_left(self):
        new_x = self.xpos - self.move_amt
        if new_x < 0:
            new_x = 0
        self.xpos = new_x

    def move_right(self):
        limit = SCREEN_WIDTH - self.width
        new_x = self.xpos + self.move_amt
        if new_x > limit: 
            new_x = limit
        self.xpos = new_x


class Ball:
    def __init__(self):
        self.xpos = BALL_STARTX
        self.ypos = BALL_STARTY
        self.speed = Vector2D(2, 2)
        self.width = BALL_SIZE
        self.height = BALL_SIZE
        self.color = BALL_COLOR
        self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)

    def _calculate_position(self, ship):
        new_xpos = self.xpos + self.speed.x
        new_ypos = self.ypos + self.speed.y
        right_bounds = SCREEN_WIDTH - self.width
        top_bounds = 0 
        left_bounds = 0
        # Top of screen
        if new_ypos <= 0: 
            new_ypos = 0
            self.speed.y *= -1
        
        # Left boundary 
        if new_xpos <= left_bounds:
            new_xpos = left_bounds
            self.speed.x *= -1
        
        # Right boundary 
        if new_xpos >= right_bounds:
            new_xpos = right_bounds
            self.speed.x *= -1
        
        # Ship bounce
        if self.rect.colliderect(ship.rect):
            # Calculate the distance from the center of the ship
            new_ypos = PLAYER_TOP - 10
            ship_center_x = ship.xpos + ship.width / 2
            ball_center_x = self.xpos + self.width / 2
            distance_from_center = ball_center_x - ship_center_x
            
            normalized_distance = (distance_from_center / (ship.width / 2))

            self.speed.x = normalized_distance * BALL_SPEED * 2 # Adjust the multiplier based on desired effect
            self.speed.y *= -1 * PLAYER_HIT_MODIFIER




        # Bottom screen
        if new_ypos >= SCREEN_HEIGHT + BALL_SIZE:
            console.print("[red]RESET")
            new_xpos, new_ypos = BALL_STARTX, BALL_STARTY
            self.speed = Vector2D(BALL_SPEED, BALL_SPEED)
            sleep(1)



        # Set new positions
        self.xpos = round(new_xpos, 2)
        self.ypos = round(new_ypos, 2)
        console.print(f"POSITION: X/{str(self.xpos)} Y/{str(self.ypos)}")
        console.print(f"SPEED: X/{str(self.speed.x)} Y/{str(self.speed.y)}")
        
        
    def update(self, ship):
        self._calculate_position(ship)
        self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.rect)


class Brick:
    def __init__(self, x, y, w, h, color='blue', points=0):
        self.xpos = x
        self.ypos = y
        self.width = w
        self.height = h
        
        self.rect = pygame.Rect(x, y, w, h)
        self.color = 'blue' 
        self.points_worth = None 

    def draw(self):
        self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.rect)


class BrickManager:
    def __init__(self):
        self.brick_width = 40
        self.brick_height = 10
        self.gap_x = 10
        self.gap_y = None

        self.field_bounds_x = 100
        self.field_bounds_y = 50 
        self.field_bounds_height = 600 
        self.field_bounds_width = 500
        self.field_bounds_rect = (
            self.field_bounds_x, 
            self.field_bounds_y, 
            self.field_bounds_width, 
            self.field_bounds_height
        )

        self.bricks_x = round(self.field_bounds_width / (self.brick_width + self.gap_x))    # How many bricks in each row
        self.bricks_y = None    # How many bricks in each column
        self.bricks = []      # Rects of each brick to compare w/ ball position
        
        self._brick_row()

    def _brick_row(self):
        for i in range(0, self.bricks_x):
            space_from_edge = self.field_bounds_x
            x = i * (self.brick_width + self.gap_x) + space_from_edge #! Will cause a gap before the first brick in the row
            y = self.field_bounds_y
            brick = Brick(x, y, self.brick_width, self.brick_height)
            self.bricks.append(brick)

    def update(self):
        print(self.bricks_x)
        for b in self.bricks: 
            b.draw()
    

# -------------------------------------------------------------------
# Gameloop

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(SCREEN_BG)
font = pygame.font.Font(None, FONT_SIZE)
clock = pygame.time.Clock()
running = True
frame = 0

ship = Starship()
ball = Ball()
brick_field = BrickManager()

while running:
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 

    print()
    console.print("---------------------------------------------")
    print()
    console.print(f"FRAME: {str(frame)}")
    
    screen.fill('black')
    keys = pygame.key.get_pressed()
    if keys[MOVE_LEFT]:
        ship.move_left()
    if keys[MOVE_RIGHT]:
        ship.move_right()


    ship.update()
    ball.update(ship)
    brick_field.update()

    text = font.render(f'Speed: {str(abs(round(math.sqrt(ball.speed.x*ball.speed.x + ball.speed.y*ball.speed.y), 2)))}', False, 'white')
    screen.blit(text, (0,0))

    pygame.display.flip()
    clock.tick(60)
