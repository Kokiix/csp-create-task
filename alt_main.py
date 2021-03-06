import tkinter as tk
import random as r
import math
import threading
import time
### need to be installed

# python3 -m pip install playsound
# python3 -m pip install Pillow

from PIL import ImageTk, Image
from playsound import playsound


class Minesweeper(tk.Frame):
    def __init__(self, parent, board_pixel_height):
        self.root = parent
        tk.Frame.__init__(self, self.root)

        self.dark_green = "#A2D149"
        self.light_green = "#AAD751"

        # minesweeper = Minesweeper(root, 10, 8, 10, screen_height) # easy
        # minesweeper = Minesweeper(root, 18, 14, 40, screen_height) # medium
        # minesweeper = Minesweeper(root, 24, 20, 99, screen_height) # hard

        # DEFAULT  = medium
        self.board_tile_width = 18
        self.board_tile_length = 14
        self.mine_number = 40

        self.tile_length = board_pixel_height / self.board_tile_length
        self.board_pixel_length = int(self.tile_length * self.board_tile_length)
        self.board_pixel_width = int(self.tile_length * self.board_tile_width)    
        
        self.lose_screen = ImageTk.PhotoImage(Image.open("funnybunny_red.jpg").resize((self.board_pixel_width, self.board_pixel_length)))
        self.menu_screen = ImageTk.PhotoImage(Image.open("funnybunny_black.jpg").resize((int(self.board_pixel_width * 0.7), int(self.board_pixel_length * 0.7))))
        self.win_screen = ImageTk.PhotoImage(Image.open("funnybunny_green.jpg").resize((self.board_pixel_width, self.board_pixel_length)))
        self.canvas = tk.Canvas(
            root, 
            width = self.board_pixel_width, height = self.board_pixel_length, 
            highlightthickness = 0, bg = "white")
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)

        self.start_time = 0
        self.pixel = tk.PhotoImage(width = 1, height = 1)
        self.buttons = []

        self.menu_font = ('Helvetica', -1 * int(self.board_pixel_length / 35))
        self._start_menu(None)
        

    def _start_menu(self, event):
        self.root.unbind("<Key>")
        self.root.unbind("<Button>")

        self.canvas.tag_bind("clickable", "<Button>", self._on_tile_click)

        self.canvas.delete("all")
        button_width = int(self.board_pixel_width / 4)
        button_length = int(self.board_pixel_length / 10)
        difficulties = ["Easy", "Medium", "Hard"]
        self.canvas.create_image(
            self.board_pixel_width / 3, self.board_pixel_length / 1.55, 
            anchor = "center", 
            image = self.menu_screen)
        for button_number in range(3):
            button = tk.Button(
                self.root,
                bg = self.light_green,
                bd = 0,
                text = difficulties[button_number],
                font = self.menu_font,
                image = self.pixel,
                width = button_width,
                height = button_length,
                command = lambda buttonid = button_number : self._menu_button(buttonid),
                compound = "c"
                )
            button.pack()
            button.place(relx = 0.85, rely = 0.2 * (button_number + 1) + 0.1, anchor = "center")
            self.buttons.append(button)


    def _menu_button(self, buttonid):
        self.canvas.delete("all")
        for button in self.buttons:
            button.destroy()

        if buttonid == 0: # easy
            self.board_tile_width = 10
            self.board_tile_length = 8
            self.mine_number = 10
        elif buttonid == 1: # medium
            self.board_tile_width = 18
            self.board_tile_length = 14
            self.mine_number = 40
        elif buttonid == 2: # hard
            self.board_tile_width = 24
            self.board_tile_length = 20
            self.mine_number = 99

        self.tile_length = self.board_pixel_length / self.board_tile_length
        self.board_pixel_width = self.tile_length * self.board_tile_width
        self.canvas.configure(width = self.board_pixel_width)
        self.root.geometry("%dx%d" % (self.board_pixel_width, self.board_pixel_length))
        self._start()


    def _start(self):
        self.tiles_cleared = 0
        self.first_click_detector_id = -10
        self.canvas.delete("all")
        self.minefield = [[self._create_tile(row, col) for col in range(self.board_tile_width)] for row in range(self.board_tile_length)]
        self._setup_first_click_detector()


    def _create_tile(self, row, col):
        # swap colors every other tile & every row
        color1 = self.light_green if row % 2 == 0 else self.dark_green
        color2 = self.light_green if color1 == self.dark_green else self.dark_green
        fill_color = color1 if col % 2 == 0 else color2
        
        return Tile(
            self.canvas, 
            self.tile_length, 
            fill_color,
            "blank",
            row, col)


    def _setup_first_click_detector(self):
        # cover screen in invisible rect to detect first click
        self.first_click_detector_id = self.canvas.create_rectangle(
            0, 0, self.board_pixel_width, self.board_pixel_length,
            fill = "",
            outline = "",
            tags = "first_click_setup")


    def _on_first_click(self, event):
        first_tile_col = math.floor(event.x / self.tile_length)
        first_tile_row = math.floor(event.y / self.tile_length)
        first_tile = self.minefield[first_tile_row][first_tile_col]

        for mine_num in range(self.mine_number):
            # ensure first click isn't a mine; 
            # keeps finding mine placement that isn't already first click or another mine
            mine_tile = first_tile
            while ((first_tile_col - 2 < mine_tile.col < first_tile_col + 2) and \
                    (first_tile_row - 2 < mine_tile.row < first_tile_row + 2)) or \
                    mine_tile.type == "mine":

                mine_tile = r.choice(r.choice(self.minefield))
            mine_tile.type = "mine"

            # self.canvas.itemconfig(mine_tile.tile_id, fill = "#FFF012") # DEBUG

            # increment numbers for tiles around mine
            for neighbor in self._get_neighbors(mine_tile):
                if neighbor.type != "mine":
                    neighbor.mines_near += 1
                    neighbor.type = "near_mine"

        self.canvas.delete(self.first_click_detector_id)
        self._clear_tiles(first_tile)
        self.start_time = time.time()


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]

        if event.num == 1 and not tile.has_flag:
            if tile.type == "blank" or tile.type == "near_mine":
                self._clear_tiles(tile)
                self.canvas.pack() # reload visual changes
            elif tile.type == "mine":
                self._display_end_screen("loss")
                
        elif event.num == 3 and tile.type != "cleared":
            if tile.has_flag:
                tile.deflag()
            else:
                tile.flag()

            

    def _clear_tiles(self, tile): # RENAME function to reflect recursive nature
        tile_type = tile.type
        tile.clear()
        self.tiles_cleared += 1
        if self.tiles_cleared == self.board_tile_length * self.board_tile_width - self.mine_number:
            self._display_end_screen("win")
            return
        if tile_type != "near_mine":
            for neighbor in self._get_neighbors(tile):
                if neighbor.type == "blank" or neighbor.type == "near_mine":
                    self._clear_tiles(neighbor)


    def _get_neighbors(self, tile):
        neighbor_coords = []
        neighbor_coords = [
            [tile.row - 1, tile.col], [tile.row - 1, tile.col - 1], [tile.row - 1, tile.col + 1],
            [tile.row + 1, tile.col], [tile.row + 1, tile.col - 1], [tile.row + 1, tile.col + 1], 
            [tile.row, tile.col + 1], [tile.row, tile.col - 1]]

        final_tileset = []
        for coord_pair in neighbor_coords:
            if -1 not in coord_pair                        and \
                self.board_tile_width != coord_pair[1]     and \
                self.board_tile_length != coord_pair[0]:

                final_tileset.append(self.minefield[coord_pair[0]][coord_pair[1]])
        return final_tileset


    def _display_end_screen(self, result):
        end_screen = self.canvas.create_image(
            self.board_pixel_width / 2, self.board_pixel_length / 2, 
            anchor = "center", 
            image = self.lose_screen if result == "loss" else self.win_screen)

        threading.Thread(target = playsound, args = ("boing.wav",), daemon = True).start()
        threading.Thread(target = self._end_animation, args = (end_screen,), daemon = True).start()

        if result == "win":
            print("Final Score: %d seconds" % round(time.time() - self.start_time, 2))


    def _end_animation(self, img):
        time.sleep(2)

        # Medium difficulty
        if self.mine_number == 40 or self.mine_number == 99:
            img_x = 0
            img_y = 0
            for move in range(int(self.board_pixel_width / 12)):
                print(move)
                self.canvas.move(img, img_x, img_y)
                img_x += 0.5
                time.sleep(0.005)

        for row in self.minefield:
            for tile in row:
                self.canvas.itemconfig(tile.tile_id, tags = "")
                tile.bring_to_front()
                if self.mine_number == 10:
                    time.sleep(0.005)

        self.root.bind("<Key>", self._start_menu)
        self.root.bind("<Button>", self._start_menu)


class Tile(object):
    def __init__(self, canvas, length, color, tile_type, row, col):
        self.LIGHT_BROWN = "#E5C29F"
        self.DARK_BROWN = "#D7B899"
        self.light_green = "#AAD751"

        self.canvas = canvas
        self.row = row
        self.col = col
        self.length = length
        self.x = self.col * self.length
        self.y = self.row * self.length

        self.type = tile_type
        self.mines_near = 0
        self.font = ('Helvetica',
        int(length / 2), 'bold')
        self.color = "light" if color == self.light_green else "dark"

        self.has_flag = False
        self.flag_part_ids = []
        

        # canvas object constructors return a unique id for that obj
        self.text_id = None
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.length, self.y + self.length,
            fill = color,
            outline = "",
            tags = ["clickable", self.type])


    def _get_distance_color(self):
        colors = [
            "#1976D2", # Blue
            "#388E3C", # Green
            "#D32F2F", # Red
            "#7B1FA2", # Purple
            "#FF8F00", # Gold
            "#0097A7", # Aqua
            "#424242", # Black
            "#9E9E9E"] # Silver
        return colors[self.mines_near - 1]


    def clear(self):
        self.deflag()
        self.canvas.itemconfig(self.tile_id, fill = self.LIGHT_BROWN if self.color == "light" else self.DARK_BROWN)
        if self.type == "near_mine":
            self.text_id = self.canvas.create_text(
                self.x + self.length / 2, self.y + self.length / 2, 
                text = str(self.mines_near),
                fill = self._get_distance_color(),
                font = self.font)
        self.type = "cleared"

    def flag(self):
        pole_x = self.x + self.length * 0.35
        pole_y = self.y + self.length * 0.20
        pole_width = self.length * 0.08
        pole_length = self.length * 0.55

        flag_pole = self.canvas.create_rectangle(
            pole_x, pole_y,
            pole_x + pole_width, pole_y + pole_length,
            fill = "red", outline = "")

        cloth_tip_x = pole_x + self.length * 0.4
        cloth_tip_y = pole_y + self.length * 0.1
        cloth_base_y = pole_y + self.length * 0.25

        cloth_points = [pole_x + pole_width, pole_y, 
        cloth_tip_x, cloth_tip_y, 
        pole_x + pole_width, cloth_base_y]

        flag_cloth = self.canvas.create_polygon(
            cloth_points,
            fill = "red", outline = "")

        base_x_offset = pole_width * 0.5
        base_y_offset = pole_length * 0.3
        flag_base = self.canvas.create_arc(
            pole_x - base_x_offset, pole_y + pole_length * 0.9,
            pole_x + pole_width + base_x_offset, pole_y + pole_length + base_y_offset,
            extent = 180, fill = "red", outline = "")

        self.flag_part_ids = [flag_pole, flag_cloth, flag_base]
        for flag_part in self.flag_part_ids:
            self.canvas.itemconfig(flag_part, tags = ["clickable"])
        self.has_flag = True


    def deflag(self):
        for flag_part in self.flag_part_ids:
            self.canvas.delete(flag_part)
        self.flag_part_ids.clear()
        self.has_flag = False


    def bring_to_front(self):
        self.canvas.tag_raise(self.tile_id)
        if self.type == "mine":
            rainbow_colors = [
                "#FF0000", # Red
                "#FC6404", # Orange
                "#FCC201", # Gold
                "#029658", # DARK Green
                "#2B6CC4", # Blue
                "#1ABC9C", # Teal
                "#6454AC", # Purple
                "#FF1DCE" # Magenta
            ]
            self.canvas.itemconfig(self.tile_id, fill = r.choice(rainbow_colors))
        elif self.text_id != None:
            self.canvas.tag_raise(self.text_id)


if __name__ == "__main__":
    root = tk.Tk()

    # game/window settings

    screen_height = root.winfo_screenheight() - 100

    minesweeper = Minesweeper(root, screen_height)

    minesweeper.pack(fill="both", expand=True)
    minesweeper.canvas.pack()

    width = minesweeper.board_pixel_width
    length = minesweeper.board_pixel_length
    root.geometry('%dx%d+%d+%d' % (width, length, root.winfo_screenwidth() / 2 - (width / 2), 10))
    root.title("Minesweeper!")
    root.resizable(False, False)

    root.mainloop()