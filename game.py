import pygame, sys, random
from pygame.math import Vector2
import numpy as np

from enum import Enum

pygame.mixer.pre_init(44100,-16,2,512)  
pygame.init()

font = pygame.font.Font("font/04B_30__.ttf", 25)


SPEED = 40
WHITE = (255, 255, 255)

class Direction(Enum):
    RIGHT = 1 
    LEFT = 2
    UP = 3
    DOWN = 4


class Snake:
    def __init__(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(0,0)
        self.new_block = False
        
        self.body_bl = pygame.image.load("static/body_bottomleft.png").convert_alpha()
        self.body_br = pygame.image.load("static/body_bottomright.png").convert_alpha()
        self.body_tl = pygame.image.load("static/body_topleft.png").convert_alpha()
        self.body_tr = pygame.image.load("static/body_topright.png").convert_alpha()
        
        self.head_down = pygame.image.load("static/head_down.png").convert_alpha()
        self.head_left = pygame.image.load("static/head_left.png").convert_alpha()
        self.head_right = pygame.image.load("static/head_right.png").convert_alpha()
        self.head_up = pygame.image.load("static/head_up.png").convert_alpha()
        
        self.body_horizontal = pygame.image.load("static/body_horizontal.png").convert_alpha()
        self.body_vertical = pygame.image.load("static/body_vertical.png").convert_alpha()
        
        self.tail_down = pygame.image.load("static/tail_down.png").convert_alpha()
        self.tail_left = pygame.image.load("static/tail_left.png").convert_alpha()
        self.tail_right = pygame.image.load("static/tail_right.png").convert_alpha()
        self.tail_up = pygame.image.load("static/tail_up.png").convert_alpha()
        
        self.eat_sound = pygame.mixer.Sound('Sound/crunch.wav')
        
    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()
        for index,block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)
            
            if index == 0:
                screen.blit(self.head,block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        screen.blit(self.body_tl, block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        screen.blit(self.body_bl, block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        screen.blit(self.body_br, block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        screen.blit(self.body_tr, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down

    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
        elif tail_relation == Vector2(0,1): self.tail = self.tail_up
        elif tail_relation == Vector2(0,-1): self.tail = self.tail_down
            
            

    def move_snake(self, action):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True
        
    def play_crunch_sound(self):
        self.eat_sound.set_volume(1.0)
        self.eat_sound.play()    

    def reset(self):
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(0,0)


        
class Fruit:
    def __init__(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x,self.y)
        
    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(raspberry, fruit_rect)
        
    def randomize(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x,self.y)

class Main:
    def __init__(self):
        self.direction = Direction.RIGHT
        self.snake = Snake()
        self.fruit = Fruit()
        self.display = pygame.display.update
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(SCREEN_UPDATE, 150)
        self.draw_elements()
        self.frame_iteration = 0
        self.score = 0
        
        
    def update(self):
        self.snake.move_snake()
        self._check_collision()
        self.check_fail()
        
    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def _check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
            reward = +10
            self.score =+ 1
            
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

            
    def check_fail(self, pt=None):
        if pt is None:
            pt = self.snake.body[0]
        if not 0 <= pt.x < cell_number or self.frame_iteration > 100*len(self.snake.body):
            self.game_over()
            
        if not 0 <= pt.y < cell_number or self.frame_iteration > 100*len(self.snake.body):
            self.game_over()
            
        for block in self.snake.body[1:]:
            if block == pt or self.frame_iteration > 100*len(self.snake.body):
                self.game_over()
            
    def game_over(self):
        reward = -10
        self.score = 0
        self.frame_iteration = 0
        self.snake.reset()
        return reward
        
        
    def draw_grass(self):
        grass_color = (148, 216, 81)
        for row in range(cell_number):
            if row % 2 == 0:
                for col in range(cell_number):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * cell_size , row * cell_size , cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)
            else:
                for col in range(cell_number):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)
        
    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text, True, (13, 11, 58))
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center = (score_x, score_y))
        raspberry_rect= raspberry.get_rect(midright = (score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(raspberry_rect.left, raspberry_rect.top, raspberry_rect.width + score_rect.width + 6,raspberry_rect.height)
        
        pygame.draw.rect(screen, (167,209,61), bg_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(score_image, raspberry_rect)
        pygame.draw.rect(screen, (13,11,58), bg_rect,2)
        
    def play_step(self, action):
        self.frame_iteration += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        self._move(action)
        
        
        reward = 0
        game_over = False
        if self.check_fail() or self.frame_iteration > 100*len(self.snake.body):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        
        self._check_collision()
        
        self.clock.tick(SPEED)
        
        return reward, game_over, self.score
        


    def _move(self, action):
        
       
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        
        idx = clock_wise.index(self.direction)
        
        
        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else: 
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]
            
        main_game.snake.direction = new_dir
        
        if self.direction == Direction.RIGHT:
            main_game.snake.direction = Vector2(1,0)
        if self.direction == Direction.DOWN:
            main_game.snake.direction = Vector2(0,1)
        if self.direction == Direction.LEFT:
            main_game.snake.direction = Vector2(-1, 0)
        if self.direction == Direction.UP:
            main_game.snake.direction = Vector2(0, -1)
            
            
    def _update_ui(self):
        screen.fill((166,216,81))
        self.draw_elements()
        text = font.render("Score :" + str(self.score), True, WHITE)
        self.display.blit(text, [0,0])
            
cell_size = 40
cell_number = 20
screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
score_image = pygame.image.load("static/RealRaspberry.png").convert_alpha()
raspberry = pygame.image.load("static/Raspberry-.png").convert_alpha()
game_font = pygame.font.Font("font/04B_30__.ttf", 25)



SCREEN_UPDATE = pygame.USEREVENT


main_game = Main()


    
    
