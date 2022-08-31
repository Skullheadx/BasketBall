import pygame.draw

from setup import *


class Ball:
    radius = 15
    gravity = 9.81 / 1000

    def __init__(self, pos, vel, collide_list):
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(vel)
        self.acceleration = pygame.Vector2(0, self.gravity)

        self.angle = 0

        self.shot_taken = False
        self.on_ground = False

        self.collide_list = collide_list

    def get_input(self):
        if pygame.mouse.get_pressed(3)[0]:
            self.shoot()

    def shoot(self):
        if not self.shot_taken:
            self.shot_taken = True

            self.velocity, self.angle = self.get_initial()

    def get_initial(self):
        mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        velocity = pygame.Vector2(
            mouse_position.x - self.position.x, mouse_position.y - self.position.y).normalize()

        distance = math.sqrt(pow(mouse_position.x - self.position.x, 2) + pow(mouse_position.y - self.position.y, 2))

        # print(distance)

        distance /= 45

        distance = min(distance, 12)

        velocity.x *= distance
        velocity.y *= distance

        # angle = math.atan((mouse_position.y - self.position.y) / (mouse_position.x - self.position.x))  # radians
        angle = 0
        return velocity, angle

    def update(self, delta):

        self.get_input()

        if self.shot_taken:
            self.position, self.velocity = self.get_movement(delta, self.collide_list)

    def get_movement(self, delta, collide_list):
        position, velocity = self.position.copy(), self.velocity.copy()

        self.on_ground = False
        position.y += velocity.y
        for thing in collide_list:
            if thing.get_rect().colliderect(self.get_rect(position.x, position.y)):
                if velocity.y > 0:
                    position.y = thing.position.y - self.radius
                    self.on_ground = True
                else:
                    position.y = thing.position.y + thing.height + self.radius
                velocity.y *= -0.7

        velocity.y += self.acceleration.y * delta
        if self.on_ground and abs(velocity.y) < 0.6:
            velocity.y = 0

        position.x += velocity.x
        for thing in collide_list:
            if thing.get_rect().colliderect(self.get_rect(position.x, position.y)):
                if velocity.x > 0:
                    position.x = thing.position.x - self.radius
                else:
                    position.x = thing.position.x + thing.width + self.radius
                velocity.x *= -0.7
        velocity.x += self.acceleration.x * delta

        if self.on_ground:
            velocity.x *= 0.9
        if self.on_ground and abs(velocity.x) < 0.1:
            velocity.x = 0

        return position, velocity

    def get_rect(self, x=None, y=None):
        if x is None:
            x = self.position.x
        if y is None:
            y = self.position.y
        return pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, Colour.ORANGE, self.position, self.radius)


class BallPath(Ball):
    num_dots = 5
    # separation_distance = 0 gets too long to calc when bounce on floor
    separation_counts = 6
    radius = Ball.radius * 0.85

    def __init__(self, pos, vel, collide_list):
        super().__init__(pos, vel, collide_list)

        self.path = []
        self.initial_position = pygame.Vector2(pos)

    def update(self, delta):
        self.position = self.initial_position.copy()
        self.velocity, self.angle = self.get_initial()

        self.path = [self.position]
        time = (1000 / fps)  # for a smoother result
        dots = 0
        counter = 0
        while (-self.radius < self.position.x < SCREEN_WIDTH + self.radius and
               self.position.y < SCREEN_HEIGHT + self.radius):

            self.position, self.velocity = self.get_movement(time, self.collide_list)
            counter += 1
            if counter % self.separation_counts == 0:
                # if len(self.path) == 0 or (
                #         pow(self.path[-1].y - self.position.y, 2) + pow(self.path[-1].x - self.position.x, 2) > pow(
                #         self.separation_distance, 2)):
                self.path.append(self.position)
                dots += 1

            if dots == self.num_dots:
                break
        # print(self.path, self.position, self.velocity)

    def draw(self, surf):
        for pos in self.path:
            pygame.draw.circle(surf, Colour.LIGHT_GRAY, pos, self.radius)


class Net:
    width, height = Ball.radius * 2 * 2, Ball.radius * 3
    rim_width = 2
    pole_width = 30
    backboard_height = Ball.radius * 5

    def __init__(self, pos):
        self.position = pygame.Vector2(pos)
        self.can_score = False
        self.left_wall = Wall((self.position.x - self.rim_width / 2, self.position.y), self.rim_width, self.height,
                              Colour.WHITE)
        self.right_wall = Wall((self.position.x + self.width - self.rim_width / 2, self.position.y), self.rim_width,
                               self.height, Colour.WHITE)
        self.pole = Wall((self.right_wall.position.x + self.rim_width, self.position.y - self.backboard_height),
                         self.pole_width, SCREEN_HEIGHT - self.position.y, Colour.DARK_GRAY)
        self.scored = False

    def update(self, ball):
        if not self.can_score and ball.position.y < self.position.y:
            self.can_score = True
        if self.can_score and self.get_rect().colliderect(ball.get_rect()):
            self.scored = True
        return self.scored

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def draw(self, surf):
        pygame.draw.rect(surf, Colour.WHITE, self.get_rect())


class Wall:

    def __init__(self, pos, width, height, colour):
        self.position = pygame.Vector2(pos)
        self.width = width
        self.height = height
        self.colour = colour

    def get_rect(self):
        return pygame.Rect(self.position, (self.width, self.height))

    def draw(self, surf):
        pygame.draw.rect(surf, self.colour, self.get_rect())


class Game:
    font = pygame.font.Font('Main/gomarice_no_continue.ttf', 64)
    small_font = pygame.font.Font('Main/gomarice_no_continue.ttf', 32)
    points = 0
    attempts = 0

    def __init__(self):
        self.net = Net((SCREEN_WIDTH * 4 / 5, SCREEN_HEIGHT / 3))

        self.collision_list = [self.net.left_wall, self.net.right_wall, self.net.pole,
                               Wall((0, SCREEN_HEIGHT * 4 / 5), SCREEN_WIDTH, SCREEN_HEIGHT / 5, Colour.TAN)]

        self.ball = Ball((random.randint(SCREEN_WIDTH/10, SCREEN_WIDTH/1.5), SCREEN_HEIGHT * 2 / 3), (0, 0), self.collision_list)
        self.ball_path = BallPath(self.ball.position, self.ball.velocity, self.collision_list)

        self.scored = False
        self.points_added = False
        self.attempt_added = False
        self.game_over = False
        self.timer = 2000

    def update(self, delta):
        self.ball.update(delta)
        if not self.ball.shot_taken:
            self.ball_path.update(delta)

        self.scored = self.net.update(self.ball)

        if not self.points_added and self.scored:
            self.points += 1
            self.points_added = True

        if not self.attempt_added and pygame.mouse.get_pressed(3)[0]:
            self.attempts += 1
            self.attempt_added = True

        if not self.game_over and self.ball.shot_taken and (self.ball.velocity == pygame.Vector2(0, 0) or not (
                -self.ball.radius < self.ball.position.x < SCREEN_WIDTH + self.ball.radius and
                self.ball.position.y < SCREEN_HEIGHT + self.ball.radius)):
            self.game_over = True
        if self.game_over:
            self.timer -= delta
            if self.timer <= 0:
                self.__init__()

    def draw(self, surf):
        surf.fill(Colour.BLUE)
        if not self.ball.shot_taken:
            self.ball_path.draw(surf)

        for thing in self.collision_list:
            thing.draw(surf)
        # self.net.draw(surf)

        self.ball.draw(surf)

        if self.game_over:
            if self.scored:
                text = self.font.render("YOU SCORED", True, Colour.WHITE)
                text_rect = text.get_rect(center=center)
                text2 = self.font.render("YOU SCORED", True, Colour.DARK_GRAY)
                text_rect2 = text.get_rect(center=center-pygame.Vector2(-10,-10))
            else:
                text = self.font.render("YOU MISSED", True, Colour.WHITE)
                text_rect = text.get_rect(center=center)
                text2 = self.font.render("YOU SCORED", True, Colour.DARK_GRAY)
                text_rect2 = text.get_rect(center=center-pygame.Vector2(-10,-10))
            surf.blit(text2, text_rect2)
            surf.blit(text, text_rect)
        text3 = self.small_font.render(f"POINTS: {self.points}", True, Colour.WHITE)
        text_rect3 = text3.get_rect()
        surf.blit(text3, text_rect3)
        text4 = self.small_font.render(f"ATTEMPT #{self.attempts}", True, Colour.WHITE)
        text_rect4 = text4.get_rect(top = text_rect3.height)
        surf.blit(text4, text_rect4)
