from os import pipe
import time
import cv2
import pygame
import numpy
import matplotlib
import random
import pprint

class movement():
    def __init__(self):
        self.velocity = pygame.Vector2(0,0)
        self.acceleration = pygame.Vector2(0,0)
        self.speed = 5 
        self.gravity = pygame.Vector2(0, 1)
        self.position = pygame.Vector2(0,0)


class GameEvent():
    def __init__(self):
        self.events = pygame.event.get()
    def update(self, game):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.gameStop:
                        game.new_game()
                if event.key == pygame.K_q:
                    game.running = False
            elif event.type == game.pipe_pop:
                game.pipe.add()
class Pipe(movement):

    def __init__(self, width, height):
        super().__init__()
        self.width, self.height = width, height
        self.pipe_count = 0
        self.pipeup = pygame.image.load("pipe_re.png").convert_alpha()
        self.pipedown = pygame.image.load("pipe_re.png").convert_alpha()
        self.pipedown = pygame.transform.flip(self.pipedown, flip_x=False, flip_y=True)
        

        self.pipes_list = []

    def random_pipe(self):
        self.gap = 250
        bar_height = random.randint(200, 800)
        self.pipeup = pygame.transform.scale(self.pipeup, (200, bar_height))

        self.pipedown = pygame.transform.scale(self.pipedown, (200, self.height - self.gap - bar_height))

        self.pipeup_rect = self.pipeup.get_rect(bottomright=(self.width, self.height + 100))          
        self.pipedown_rect = self.pipedown.get_rect(topright=(self.width, 0)) 

        return [[self.pipedown, self.pipedown_rect], [self.pipeup, self.pipeup_rect]]

    def update(self):
        new_list = []
        for pipe_pair in self.pipes_list:
            new_pair = []
            for (surf, rect) in pipe_pair:
                rect.x = rect.x - self.speed
                if rect.topright[0] < 0:
                    continue
                else:
                    new_pair.append([surf, rect])
            new_list.append(new_pair)
        self.pipes_list = new_list


    def reset(self):

        self.gameStop = False

        self.next_pipe = 0
        self.pipes_list = []


    def add(self):
        self.pipes_list.append(self.random_pipe())

    def draw(self, screen):
        for pipe_pair in self.pipes_list:
            for surf, rect in pipe_pair:
                screen.blit(surf, rect)


class Bird(movement):
    def __init__(self):
        super().__init__()
        self.bird = pygame.image.load("flappy_rem.png").convert_alpha()
        self.bird = pygame.transform.scale(self.bird, (120, 80))
        self.spawnx, self.spawny = 150, 400
        self.bird_rect = self.bird.get_rect(topleft=(self.spawnx, self.spawny))
        self.position = pygame.Vector2(self.bird_rect.x, self.bird_rect.y)
        self.get_jumped = False
        self.game_end = False
        self.target_pipe = None

    def collision(self, height, pipes_list) -> bool:
        if self.bird_rect.y < 0:
            self.game_end = True
            return True
        if self.bird_rect.y > height:
            self.game_end = True
            return True
        pipes_list = [rect for pipe_pair in pipes_list for surf, rect in pipe_pair]
        if self.bird_rect.collidelist(pipes_list) != -1:
            print("collision")
            return True
        return False

    def is_passing(self, pipes_list) -> bool:
        if not self.target_pipe:

            self.target_pipe = self.get_infront_pipe(pipes_list)
            return False

        if self.bird_rect.x >= self.target_pipe:
            print("passing")
            self.target_pipe = self.get_infront_pipe(pipes_list)
            return True
        self.target_pipe = self.get_infront_pipe(pipes_list)
        return False

    def get_infront_pipe(self, pipes_list):
        for pipe_pair in pipes_list:
            for surf, rect in pipe_pair:
                if self.bird_rect.x <= rect.x:
                    return rect.x


    def update(self):
        self.acceleration = pygame.Vector2(0,0)
        if self.get_jumped:
            self.velocity = pygame.Vector2(0,0)
            self.acceleration = pygame.Vector2(0,-15)
            self.get_jumped = False

        self.velocity += self.acceleration
        self.velocity += self.gravity

        self.velocity.y = min(self.velocity.y, 20.0)

        self.position += self.velocity
 
        x = int(self.position[0])
        y = int(self.position[1])
        self.bird_rect.center = x,y

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.get_jumped = True

    def reset(self):
        self.pipes_list = []

    def draw(self, screen):
        screen.blit(self.bird, self.bird_rect)

class Coin():
    def __init__(self, width, height) -> None:
        self.width, self.height = width, height
        self.img = pygame.image.load("pngegg.png")
        self.img = pygame.transform.scale_by(self.img, (0.1,0.1))
        self.img_rect = self.img.get_rect(center=(self.width, self.height))
        self.font = pygame.font.SysFont('FreeSans', 48)


    def draw(self, screen, coin):
        screen.blit(self.img, self.img_rect)
        self.coin_text = self.font.render(str(coin), True, (0,0,0))
        self.coin_text_rect = self.coin_text.get_rect(midleft=(self.width + 50, self.height))
        screen.blit(self.coin_text, self.coin_text_rect)

class FloppyBird():
    def __init__(self):
        self.pygame = pygame.init()

        self.width, self.height = 1280 , 1280
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.gameevent = GameEvent()
        self.clock = pygame.time.Clock()

        self.pipe_pop = pygame.USEREVENT + 1
        self.font = pygame.font.SysFont('FreeSans', 36)

        self.best_score = 0

        self.GameOver = pygame.image.load("Gameover.png").convert_alpha()
        self.GameOver_rect = self.GameOver.get_rect(center=(self.width/2, self.height/2))



    def new_game(self):
        self.bird = Bird()
        self.pipe = Pipe(self.width, self.height)
        self.coin = Coin(self.width - 200, int(self.height/20))
        self._coin = 0
        pygame.time.set_timer(self.pipe_pop, 2000)
        self.pipe.add()
        self.point =  0
        self.running = True
        self.gameStop = False

    def Start(self):

        self.new_game()

        while self.running:

            self.gameevent.update(self)

            if not self.gameStop:
                self.screen.fill((255, 255, 0))
                ##
                # Draw  
                #
                self.bird.draw(self.screen)
                self.pipe.draw(self.screen)
                self.coin.draw(self.screen, self._coin)

                self.score_text = self.font.render(f"Score: {self.point}", True, (255,255,255), (0,0,255))
                self.score_text_rect = self.score_text.get_rect(midtop=(self.width / 2, 0))
                self.screen.blit(self.score_text, self.score_text_rect)
                if self.bird.collision(self.height, self.pipe.pipes_list):
                    self.best_score = self.point if self.point >= self.best_score else self.best_score
                    self.gameStop = True


                self.bird.handle_event(self.gameevent.events)
                if self.bird.is_passing(self.pipe.pipes_list):
                    self.point += 10
                    self._coin += self.point
                    print(self.point)
                    #self.next_pipe +=1

                ##
                # update
                #

                self.pipe.update()
                self.bird.update()


            else:
                self.best_score_text = self.font.render(f"Best Score: {self.best_score}", True, (0, 0,0))
                self.best_score_text_rect = self.best_score_text.get_rect(midtop=(self.width/2, self.height/2 + 150))
                self.screen.blit(self.best_score_text,self.best_score_text_rect )
                self.screen.blit(self.GameOver, self.GameOver_rect)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__=="__main__":
    Game = FloppyBird()
    Game.Start()
