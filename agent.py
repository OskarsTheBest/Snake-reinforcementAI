import torch
import random
import numpy as np
from collections import deque
from game import Main, Snake, Vector2, Fruit
from model import Linear_QNet, QTrainer
from helper import plot
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
fruit = Fruit()
snake = Snake()

class Agent:
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
    

    def get_state(self,game, fruit, snake):
        head = snake.body[0]
        
        fruit_x = fruit.x
        fruit_y = fruit.y
        
        point_l = Vector2(head.x - 20, head.y)
        point_r = Vector2(head.x + 20, head.y)
        point_u = Vector2(head.x, head.y - 20)
        point_d = Vector2(head.x, head.y + 20)
        
        dir_l = snake.direction == Vector2(-1, 0)
        dir_r = snake.direction == Vector2(1,0)
        dir_u = snake.direction == Vector2(0, -1)
        dir_d = snake.direction == Vector2(0,1)
        
        state =[
            
            (dir_r and Main.check_collision(point_r)) or
            (dir_l and Main.check_collision(point_l)) or
            (dir_u and Main.check_collision(point_u)) or
            (dir_d and Main.check_collision(point_d)),
            
            
            (dir_u and Main.check_collision(point_r)) or
            (dir_d and Main.check_collision(point_l)) or
            (dir_l and Main.check_collision(point_u)) or
            (dir_r and Main.check_collision(point_d)),
            
            
            (dir_d and Main.check_collision(point_r)) or
            (dir_u and Main.check_collision(point_l)) or
            (dir_r and Main.check_collision(point_u)) or
            (dir_l and Main.check_collision(point_d)),
            
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            fruit_x < head.x,
            fruit_x > head.x,
            fruit_y < head.y,
            fruit_y > head.y
            
        ]
        
        return np.array(state, dtype=int)
        
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    
    def train_long_memory(self):
        if len(self.memory) < BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
            
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, next_state, done in mini_sample:
    
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else: 
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        return final_move

    
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Main()
    fruit = Fruit()
    snake = Snake()
    
    while True:
        state_old = agent.get_state(game, fruit, snake)
        
        final_move = agent.get_action(state_old)
        
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game, fruit, snake)
        
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            Snake.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.model.save()
                
            print("Games", agent.n_games, "Score:", score, "Record:", record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
    
if __name__ == '__main__':
    train()
