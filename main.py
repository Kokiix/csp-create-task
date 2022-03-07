import tkinter as tk
import random as r
import math
import threading
# need to be installed
from PIL import ImageTk, Image
from playsound import playsound


class Minesweeper(tk.Frame):
    def __init__(self, parent, board_tile_width, board_tile_length, mine_number, board_pixel_size):
        self.root = parent
        tk.Frame.__init__(self, self.root)

        self.DARK_GREEN = "#A2D149"
        self.LIGHT_GREEN = "#AAD751"

        self.mine_number = mine_number
        self.board_tile_width = board_tile_width
        self.board_tile_length = board_tile_length
        self.tile_length = board_pixel_size / board_tile_width
        self.board_pixel_length = self.tile_length * board_tile_length
        self.board_pixel_width = self.tile_length * board_tile_width
        
        self.tiles_cleared = 0
        self.lose_screen = ImageTk.PhotoImage(Image.open("funnybunny.jpg").resize((int(self.board_pixel_width), int(self.board_pixel_length))))
        self.win_screen = ImageTk.PhotoImage(Image.open("funnybunnywin.jpg").resize((int(self.board_pixel_width), int(self.board_pixel_length))))
        self.canvas = tk.Canvas(
            root, 
            width = self.board_pixel_width, height = self.board_pixel_length, 
            highlightthickness = 0, bg = "white")

        self.minefield = [[self._create_tile(row, col) for col in range(board_tile_width)] for row in range(board_tile_length)]

        self.canvas.tag_bind("clickable", "<Button>", self._on_tile_click)

        self.first_click_detector_id = -10
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)
        self._setup_first_click_detector()


    def _create_tile(self, row, col):
        # swap colors every other tile & every row
        color1 = self.LIGHT_GREEN if row % 2 == 0 else self.DARK_GREEN
        color2 = self.LIGHT_GREEN if color1 == self.DARK_GREEN else self.DARK_GREEN
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
        first_tile_column = math.floor(event.x / self.tile_length)
        first_tile_row = math.floor(event.y / self.tile_length)
        first_tile = self.minefield[first_tile_row][first_tile_column]

        for mine_num in range(self.mine_number):
            # ensure first click isn't a mine; 
            # keeps finding mine placement that isn't already first click or another mine
            mine_tile = first_tile
            while mine_tile == first_tile or mine_tile.type == "mine":
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
        self.canvas.delete("all")
        threading.Thread(target = playsound, args = ("boing.wav",), daemon = True).start()
        self.canvas.create_image(
            self.board_pixel_width / 2, self.board_pixel_length / 2, 
            anchor = "center", 
            image = self.lose_screen if result == "loss" else self.win_screen)


class Tile(object):
    def __init__(self, canvas, length, color, tile_type, row, col):
        self.LIGHT_BROWN = "#E5C29F"
        self.DARK_BROWN = "#D7B899"
        self.LIGHT_GREEN = "#AAD751"

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
        self.color = "light" if color == self.LIGHT_GREEN else "dark"

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
        match self.mines_near:
            case 1: return "#1976D2" # Blue
            case 2: return "#388E3C" # Green
            case 3: return "#D32F2F" # Red
            case 4: return "#7B1FA2" # Purple
            case 5: return "#FF8F00" # Gold
            case 6: return "#0097A7" # Aqua
            case 7: return "#424242" # Black
            case 8: return "#9E9E9E" # Silver


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


if __name__ == "__main__":
    root = tk.Tk()

    # game/window settings

    minesweeper = Minesweeper(root, 10, 8, 10, 1000) # easy
    # minesweeper = Minesweeper(root, 18, 14, 40, 1000) # medium
    # minesweeper = Minesweeper(root, 24, 20, 99, 1000) # hard
    minesweeper.pack(fill="both", expand=True)
    minesweeper.canvas.pack()

    root.title("Minesweeper!")
    root.resizable(False, False)
    root.mainloop()