import tkinter as tk

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                x+self.radius, y+self.radius,
                                fill='#B565A7')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                    y - self.height / 2,
                                    x + self.width / 2,
                                    y + self.height / 2,
                                    fill='#F47777') 
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#FFB6C1', 2: '#FF69B4', 3: '#FF1493'} 
    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                    y - self.height / 2,
                                    x + self.width / 2,
                                    y + self.height / 2,
                                    fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 5
        self.points = 0  # Initialize points
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='white',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        # Heart lives
        self.hearts = []

        # Adding bricks with different hit capacities - 3, 2 and 1
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                        lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                        lambda _: self.paddle.move(10))

        # Score display
        self.score_text = self.canvas.create_text(self.width - 20, 15, text='Your Scores: 0', font=('Roboto', 12), anchor='ne')

    def create_heart(self, x, y):
        return self.canvas.create_text(x, y, text='💜', font=('Roboto', 20))

    def setup_game(self):
        for heart in self.hearts:
            self.canvas.delete(heart)
        self.hearts.clear()

        for i in range(self.lives):
            heart = self.create_heart(30 + (i * 30), 20)
            self.hearts.append(heart)

        self.add_ball()
        self.text = self.draw_text(300, 200, 'Press space to start', color='#FF69B4')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, color='black', size='35'):
        font = ('Roboto', size)
        return self.canvas.create_text(x, y, text=text,
                                    font=font, fill=color)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'Kamu Menang!')  # Display win message
            self.canvas.bind('<space>', lambda _: self.restart_game())
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            
            # Remove a heart
            if self.hearts:
                self.canvas.delete(self.hearts.pop())
            
            if self.lives < 0:
                self.show_game_over()  # Show game over message
            else:
                self.after(1000, self.setup_game)
                self.canvas.bind('<space>', lambda _: self.restart_game())
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

        # Increase points for each collision with a brick
        for game_object in objects:
            if isinstance(game_object, Brick):
                self.points += 10  # Add 10 points for each brick hit
                self.update_score_display()

    def update_score_display(self):
        self.canvas.itemconfig(self.score_text, text='Your Scores: ' + str(self.points))

    def show_game_over(self):
        self.draw_text(300, 200, 'Sorry.. you lose!', color='red')
        self.draw_text(300, 260, f'Your Scores: {self.points}', color='pink')

    def restart_game(self):
        self.points = 0  # Reset points for the new game
        self.update_score_display()  # Reset score display
        self.setup_game()  # Restart the game setup


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
