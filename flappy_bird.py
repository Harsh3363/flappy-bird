import pygame
import neat
import time
import os
import random

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VAL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    #         method to call when we want the bird to jump up =>
    def jump(self):
        self.val = -10.5
        self.tick_count = 0
        self.height = self.y

    #         method to moce our bird =>
    def move(self):
        self.tick_count += 1

        # below line tells how much we are moving up and how much we are moving dow =>
        # self.tick_count tells how many seconds we are moving for  =>

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VAL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # tilting image in Pygame =>

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

        def get_mask(self):
            return pygame.mask.from_surface(self.img)


class Pipe:
    # the gap between each pipes =>
    GAP = 200
    # the velocity with which each pipe will move backwards =>
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        #  below line of code to keep track of the pipe image =>
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        #  to keep track if the bird has passed that pipe or not =>
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    #  this one to keep track of the position of the pipes =>
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # for the collision purpose we are using mask inside the pygame => here we are assuming the pipe and the bird
    # inside two different boxes and when these boxes collide we consider the bird and box collision but there is
    # some part inside the box taking extra space then the box or bird so when that extra area collide we don't want
    # collision to be taken as so what mask does is it takes the makes the 2-D array of the pixels in the image and
    # see if the pixels are colliding or not if so then only collision is considered else not=>
    def collide(self, bird, win):
        """
               returns if a point is colliding with the pipe
               :param bird: Bird object
               :return: Bool
               """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        #         the difference between the top mask and the bird =>

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #         checking if the mask collides =>
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # initially b_point and t_point are none if they collide then it will have some value =>
        if b_point or t_point:
            return True
        return False


#     this class is for the base as it need to be keep on moving as the game proceeds =>

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # so in the case of the base what we are doing is we  are creating two images of the base one behind the other
    # both the images move in the left with same speed and as one image gets out of the screen it goes and get behind
    # the one who is on the screen =>
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# this function is responsible for drawing window and then bird on top of it =>
def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    #   pygame command to update the display =>
    pygame.display.update()


# adding genoms and config is a must as the props when we are using NEAT =>
# the genoms are the neural network that is going to control the birds =>
def main(genomes, config):
    nets = []
    ge=[]
    birds = []

    for g in genomes:
        net = neat.nn.FeedForwardNetwork(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    score = 0
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #  now if we clock on the X button of the Pygame we will quit Pygame =>
                run = False
        # bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness+=5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, bird, pipes, base, score)
    pygame.quit()
    quit()


main()


#  SETTING NEAT BELOW =>
def run(config_file):
    """
       runs the NEAT algorithm to train a neural network to play flappy bird.
       :param config_file: location of config file
       :return: None
       """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))
    # Run for up to 50 generations.
    winner = p.run(main, 50)


# below lines of code is something what NEAT recommends to do =>
if __name__ == "__main":
    # below line of code gives us the path to the directory we currently are inside =>
    local_dir = os.path.dirname(__file__)
    # joining directory to the configuration file =>
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
