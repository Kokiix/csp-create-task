import tkinter as tk
import random as r
import math


class Minesweeper(tk.Frame):
    def __init__(self, parent, board_tile_width, board_tile_length, mine_number, board_pixel_size):
        tk.Frame.__init__(self, parent)

        self.DARK_GREEN = "#A2D149"
        self.LIGHT_GREEN = "#AAD751"

        self.mine_number = mine_number
        self.board_tile_width = board_tile_width
        self.board_tile_length = board_tile_length
        self.tile_length = board_pixel_size / board_tile_width
        self.board_pixel_length = self.tile_length * board_tile_length
        self.board_pixel_width = self.tile_length * board_tile_width
        
        self.canvas = tk.Canvas(
            root, 
            width = self.board_pixel_width, height = self.board_pixel_length, 
            highlightthickness = 0)

        self.minefield = [[self._create_tile(row, col) for col in range(board_tile_width)] for row in range(board_tile_length)]

        self.canvas.tag_bind("tile", "<Button-1>", self._on_tile_click)

        self.first_click_detector_id = -10
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)
        self._setup_first_click_detector()


    def _create_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
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

        for bomb_num in range(self.mine_number):
            # ensure first click isn't a bomb
            bomb_tile = first_tile
            while bomb_tile == first_tile:
                bomb_tile = r.choice(r.choice(self.minefield))
            bomb_tile.type = "bomb"

            self.canvas.itemconfig(bomb_tile.tile_id, fill = "#FFF012") # DEBUG

            # increment numbers for tiles around bomb
            for neighbor_coords in bomb_tile.get_8_direction_neighbors():
                if -1 not in neighbor_coords                        and \
                    self.board_tile_width != neighbor_coords[1]     and \
                    self.board_tile_length != neighbor_coords[0]:

                    neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]

                    if neighbor.type != "bomb":
                        neighbor.bombs_near += 1
                        neighbor.type = "near_bomb"

        self.canvas.delete(self.first_click_detector_id)
        self._clear_tiles(first_tile)


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]

        if tile.type == "blank" or tile.type == "near_bomb:
            self._clear_tiles(tile)
            self.canvas.pack() # reload visual changes
        elif tile.type == "bomb":
            return # BOOM


    def _clear_tiles(self, tile): # RENAME function to reflect recursive nature
        tile_type = tile.type
        tile.clear()
        if tile_type != "near_bomb": # stop clear on reaching numbers - DOESN'T WORK ON CORNERS :(
            for neighbor_coords in tile.get_4_direction_neighbors():
                if -1 not in neighbor_coords                        and \
                    self.board_tile_width != neighbor_coords[1]     and \
                    self.board_tile_length != neighbor_coords[0]:

                    neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                    if neighbor.type == "blank" or neighbor.type == "near_bomb":
                        self._clear_tiles(neighbor)


class Tile(object):
    def __init__(self, canvas, length, color, tile_type, row, col):
        self.LIGHT_BROWN = "#E5C29F"
        self.DARK_BROWN = "#D7B899"
        self.LIGHT_GREEN = "#AAD751"

        self.canvas = canvas
        self.type = tile_type
        self.row = row
        self.col = col
        self.bombs_near = 0
        self.font = ('Helvetica',
        int(length / 2), 'bold')
        self.length = length
        self.color = "light" if color == self.LIGHT_GREEN else "dark"

        self.x = self.col * self.length
        self.y = self.row * self.length

        # canvas object constructors return a unique id for that obj
        self.text_id = None
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.length, self.y + self.length,
            fill = color,
            outline = "",
            tags = ["tile", self.type])


    def _get_distance_color(self):
        match self.bombs_near:
            case 1: return "#1976D2" # Blue
            case 2: return "#388E3C" # Green
            case 3: return "#D32F2F" # Red
            case 4: return "#7B1FA2" # Purple


    def clear(self):
        self.canvas.itemconfig(self.tile_id, fill = self.LIGHT_BROWN if self.color == "light" else self.DARK_BROWN)
        if self.type == "near_bomb":
            self.text_id = self.canvas.create_text(
                self.x + self.length / 2, self.y + self.length / 2, 
                text = str(self.bombs_near),
                fill = self._get_distance_color(),
                font = self.font)
        self.type = "cleared"


    # REDUCE REPETITIVENESS AND DO SOMETHING ABOUT RELIANCE ON MINEFIELD CLASS FOR FINDING NEIGHBORS
    def get_4_direction_neighbors(self):
        return [
            [self.row - 1, self.col], [self.row + 1, self.col], 
            [self.row, self.col - 1], [self.row, self.col + 1]]


    def get_8_direction_neighbors(self):
        return [
            [self.row - 1, self.col], [self.row - 1, self.col - 1], [self.row - 1, self.col + 1],
            [self.row + 1, self.col], [self.row + 1, self.col - 1], [self.row + 1, self.col + 1], 
            [self.row, self.col + 1], [self.row, self.col - 1]]


if __name__ == "__main__":
    root = tk.Tk()

    # game/window settings

    minesweeper = Minesweeper(root, 10, 8, 10, 900) # easy
    # minesweeper = Minesweeper(root, 18, 14, 40, 900) # medium
    minesweeper.pack(side="top", fill="both", expand=False)
    minesweeper.canvas.pack()

    root.title("Minesweeper!")
    root.resizable(False, False)
    root.mainloop()