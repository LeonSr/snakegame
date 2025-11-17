# snake_neon.py
from tkinter import *
import random
import os

# ----------------------------
# Config (Option B speed + Neon theme)
# ----------------------------
GAME_WIDTH = 700
GAME_HEIGHT = 700
SPACE_SIZE = 50            # grid cell size in pixels
BODY_PARTS = 3

# Theme B - Neon Modern
SNAKE_COLOR = "#00C3FF"    # neon blue
FOOD_COLOR = "#8A00FF"     # neon purple
BACKGROUND_COLOR = "#0A0A0A"  # near-black
TEXT_COLOR = "white"

# Speed settings (Option B - normal start -> grows faster moderately)
INITIAL_MOVE_DELAY = 150   # ms between logical moves at start
MIN_MOVE_DELAY = 60        # fastest logical move cap (ms)
SPEEDUP_PER_POINT = 6      # ms faster per point

HIGH_SCORE_FILE = "highscore.txt"

# ----------------------------
# High score persistence
# ----------------------------
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
        except Exception:
            return 0
    return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

# ----------------------------
# Game objects
# ----------------------------
class Snake:
    def __init__(self, canvas):
        self.canvas = canvas
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        # Start centered-ish, vertical snake
        cols = GAME_WIDTH // SPACE_SIZE
        rows = GAME_HEIGHT // SPACE_SIZE
        start_x = (cols // 2) * SPACE_SIZE
        start_y = (rows // 2 - 1) * SPACE_SIZE  # slightly above center

        for i in range(self.body_size):
            self.coordinates.append([start_x - i * SPACE_SIZE, start_y])
        for x, y in self.coordinates:
            rect = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                                           fill=SNAKE_COLOR, tag="snake")
            self.squares.append(rect)

class Food:
    def __init__(self, canvas, snake_coords):
        self.canvas = canvas
        self.coordinates = self.random_location(snake_coords)
        self.id = canvas.create_oval(self.coordinates[0], self.coordinates[1],
                                     self.coordinates[0] + SPACE_SIZE, self.coordinates[1] + SPACE_SIZE,
                                     fill=FOOD_COLOR, tag="food")

    def random_location(self, snake_coords):
        cols = GAME_WIDTH // SPACE_SIZE
        rows = GAME_HEIGHT // SPACE_SIZE
        while True:
            x = random.randint(0, cols - 1) * SPACE_SIZE
            y = random.randint(0, rows - 1) * SPACE_SIZE
            if [x, y] not in snake_coords:
                return [x, y]

    def respawn(self, snake_coords):
        try:
            self.canvas.delete(self.id)
        except Exception:
            pass
        self.coordinates = self.random_location(snake_coords)
        self.id = self.canvas.create_oval(self.coordinates[0], self.coordinates[1],
                                          self.coordinates[0] + SPACE_SIZE, self.coordinates[1] + SPACE_SIZE,
                                          fill=FOOD_COLOR, tag="food")

# ----------------------------
# Game logic (classic grid movement)
# ----------------------------
class Game:
    def __init__(self, root):
        self.root = root
        self.wrap_around = True   # will be set by start menu
        self.paused = False
        self.running = False

        self.high_score = load_high_score()

        # UI setup
        self.root.title("Snake - Neon")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.resizable(False, False)

        self.label = Label(root, text="Score: 0", font=('consolas', 26), fg=TEXT_COLOR, bg=BACKGROUND_COLOR)
        self.label.pack()

        self.canvas = Canvas(root, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH, highlightthickness=0)
        self.canvas.pack()

        # controls
        self.controls = Frame(root, bg=BACKGROUND_COLOR)
        self.controls.pack(fill="x")
        self.pause_btn = Button(self.controls, text="Pause (P)", command=self.toggle_pause, font=('consolas', 12))
        self.pause_btn.pack(side="left", padx=8, pady=6)
        self.restart_btn = Button(self.controls, text="Restart", command=self.restart_game, font=('consolas', 12))
        self.restart_btn.pack(side="left", padx=8)
        self.mode_label = Label(self.controls, text=f"Mode: {'Wrap' if self.wrap_around else 'Walls'}", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=('consolas', 12))
        self.mode_label.pack(side="right", padx=12)

        # overlay ids
        self.pause_text_id = None
        self.gameover_text_id = None
        self.restart_text_id = None

        # bind keys
        root.bind('<Left>', lambda e: self.change_direction('left'))
        root.bind('<Right>', lambda e: self.change_direction('right'))
        root.bind('<Up>', lambda e: self.change_direction('up'))
        root.bind('<Down>', lambda e: self.change_direction('down'))
        root.bind('<space>', lambda e: self.restart_game())
        root.bind('<p>', lambda e: self.toggle_pause())

        # center window
        root.update()
        w = root.winfo_width()
        h = root.winfo_height()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = int((sw/2) - (w/2))
        y = int((sh/2) - (h/2))
        root.geometry(f"{w}x{h}+{x}+{y}")

        # show start menu
        self.create_start_menu()

    def create_start_menu(self):
        # overlay frame in canvas center
        self.menu_frame = Frame(self.canvas, bg="#101014", bd=2, relief=FLAT)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        title = Label(self.menu_frame, text="S N A K E", font=('consolas', 36, 'bold'), fg="white", bg="#101014")
        title.pack(padx=40, pady=(16,8))
        desc = Label(self.menu_frame, text=f"High score: {self.high_score}", font=('consolas', 14), fg="white", bg="#101014")
        desc.pack(pady=(0,10))

        wrap_btn = Button(self.menu_frame, text="Start (Wrap-Around)", font=('consolas', 14),
                          command=lambda: self.start_game(True))
        wrap_btn.pack(pady=8, padx=20, fill="x")

        walls_btn = Button(self.menu_frame, text="Start (Walls)", font=('consolas', 14),
                           command=lambda: self.start_game(False))
        walls_btn.pack(pady=8, padx=20, fill="x")

        quit_btn = Button(self.menu_frame, text="Quit", font=('consolas', 12), command=self.root.quit)
        quit_btn.pack(pady=(10,16), padx=20, fill="x")

    def start_game(self, wrap_choice):
        # set mode and remove menu
        self.wrap_around = bool(wrap_choice)
        try:
            self.menu_frame.destroy()
        except Exception:
            pass
        self.mode_label.config(text=f"Mode: {'Wrap' if self.wrap_around else 'Walls'}")
        self.reset_game_objects()
        self.running = True
        self.paused = False
        # start loop
        self.root.after(self.move_delay, self.schedule_next_move)

    def reset_game_objects(self):
        self.canvas.delete(ALL)
        self.score = 0
        self.direction = 'right'
        self.move_delay = INITIAL_MOVE_DELAY
        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas, self.snake.coordinates)
        self.label.config(text=f"Score: {self.score}   High: {self.high_score}")
        self.pause_text_id = None
        self.gameover_text_id = None
        self.restart_text_id = None

    def restart_game(self, event=None):
        # if menu exists, ignore restart (or start new game)
        if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
            return
        # restart fresh
        self.running = True
        self.paused = False
        self.canvas.delete(ALL)
        self.reset_game_objects()
        self.root.after(self.move_delay, self.schedule_next_move)

    # direction handling (prevent 180-degree turn)
    def change_direction(self, new_direction):
        if not getattr(self, 'running', False) or getattr(self, 'paused', False):
            return
        opposite = {'left':'right','right':'left','up':'down','down':'up'}
        if new_direction == opposite.get(self.direction):
            return
        self.direction = new_direction

    # pause logic
    def toggle_pause(self, event=None):
        if not getattr(self, 'running', False):
            return
        self.paused = not self.paused
        if self.paused:
            self.show_pause_text()
        else:
            self.hide_pause_text()

    def show_pause_text(self):
        if self.pause_text_id is None:
            self.pause_text_id = self.canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2,
                                                         font=('consolas', 44, 'bold'),
                                                         text="PAUSED", fill="#FFD400", tag="pause")

    def hide_pause_text(self):
        if self.pause_text_id is not None:
            try:
                self.canvas.delete(self.pause_text_id)
            except Exception:
                pass
            self.pause_text_id = None

    # main loop ========================
    def schedule_next_move(self):
        if not getattr(self, 'running', False):
            return
        if self.paused:
            # poll while paused
            self.root.after(80, self.schedule_next_move)
            return
        self.next_turn()

    def next_turn(self):
        if not getattr(self, 'running', False) or self.paused:
            self.root.after(80, self.schedule_next_move)
            return

        x, y = self.snake.coordinates[0]

        # compute next head
        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        # wrap or walls behavior
        if self.wrap_around:
            if x < 0:
                x = GAME_WIDTH - SPACE_SIZE
            elif x >= GAME_WIDTH:
                x = 0
            if y < 0:
                y = GAME_HEIGHT - SPACE_SIZE
            elif y >= GAME_HEIGHT:
                y = 0
        else:
            # walls => out of bounds = game over
            if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
                self.game_over()
                return

        # self-collision
        for part in self.snake.coordinates:
            if x == part[0] and y == part[1]:
                self.game_over()
                return

        # move: insert head
        self.snake.coordinates.insert(0, [x, y])
        rect = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
        self.snake.squares.insert(0, rect)

        # check food
        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:
            self.score += 1
            self.update_speed()
            self.label.config(text=f"Score: {self.score}   High: {self.high_score}")
            self.food.respawn(self.snake.coordinates)
        else:
            # remove tail
            try:
                tail_id = self.snake.squares.pop()
                self.canvas.delete(tail_id)
            except Exception:
                pass
            try:
                self.snake.coordinates.pop()
            except Exception:
                pass

        # schedule next
        if getattr(self, 'running', False):
            self.root.after(self.move_delay, self.schedule_next_move)

    def update_speed(self):
        new_delay = INITIAL_MOVE_DELAY - (self.score * SPEEDUP_PER_POINT)
        if new_delay < MIN_MOVE_DELAY:
            new_delay = MIN_MOVE_DELAY
        self.move_delay = new_delay

    # game over
    def game_over(self):
        self.running = False
        # show texts
        self.canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2 - 36, font=('consolas', 56, 'bold'),
                                text="GAME OVER", fill="#FF3366", tag="gameover")
        self.canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2 + 30, font=('consolas', 18),
                                text="Press SPACE or click Restart to play again", fill="white", tag="restart_text")

        # update high score
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
            self.canvas.create_text(GAME_WIDTH/2, GAME_HEIGHT/2 + 68, font=('consolas', 14),
                                    text=f"New High Score: {self.high_score}", fill="#FFD400", tag="highscore")

        self.label.config(text=f"Score: {self.score}   High: {self.high_score}")

# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    root = Tk()
    game = Game(root)
    root.mainloop()
