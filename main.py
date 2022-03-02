import tkinter as tk
import random as r
import math




class Tile(object):
    def __init__(self, canvas, length, color, tile_type, row, col):
        self.canvas = canvas
        self.type = tile_type
        self.row = row
        self.col = col
        self.bombs_near = 0
        self.font = ('Helvetica',
        36, 'bold')
        self.length = length

        self.x = self.col * self.length
        self.y = self.row * self.length

        self.text_id = None
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.length, self.y + self.length,
            fill = color,
            outline = "",
            tags = ["tile", self.type])



    def display_bombs_near(self):
        self.canvas.create_text(
            self.x + self.length / 2, self.y + self.length / 2, 
            text = str(self.bombs_near),
            fill = self._get_distance_color(),
            font = self.font)



    def _get_distance_color(self):
        match self.bombs_near:
            case 1: return "#1976D2"
            case 2: return "#388E3C"
            case 3: return "#D32F2F"
            case 4: return "#7B1FA2"



    def clear(self):
        self.canvas.delete(self.tile_id)
        self.type = "cleared"



    def get_4_direction_neighbors(self):
        return [
            [self.row - 1, self.col], [self.row + 1, self.col], 
            [self.row, self.col - 1], [self.row, self.col + 1]]



    def get_8_direction_neighbors(self):
        return [
            [self.row - 1, self.col], [self.row - 1, self.col - 1], [self.row - 1, self.col + 1],
            [self.row + 1, self.col], [self.row + 1, self.col - 1], [self.row + 1, self.col + 1], 
            [self.row, self.col + 1], [self.row, self.col - 1]]




# inherit from frame; gui setup
class Minesweeper(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.board_length = 700
        self.tile_length = self.board_length / 10
        self.canvas = tk.Canvas(
            root, 
            width = self.board_length, height = self.board_length, 
            bg = "#d7b899", 
            highlightthickness = 0)
        self.canvas.tag_bind("tile", "<Button-1>", self._on_tile_click) # adds tile click event
        self._create_minefield()



    def _recursive_tile_clear(self, tile):
        tile.clear()
        for neighbor_coords in tile.get_4_direction_neighbors():
            if -1 not in neighbor_coords and 10 not in neighbor_coords:
                neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                if neighbor.type == "blank":
                    self._recursive_tile_clear(neighbor)
                elif neighbor.type == "near_bomb":
                    neighbor.display_bombs_near()


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]

        if tile.type == "blank":
            self._recursive_tile_clear(tile)
            self.canvas.pack()



    def _create_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # MAKE EASIER TO READ
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2

        # temporary bomb assignment for debug
        is_bomb = False if r.random() < 0.10 else True
        
        return Tile(
            self.canvas, 
            self.tile_length, 
            fill_color if is_bomb else "#53131E", # debug outline
            "bomb" if not is_bomb else "blank",
            row, col)



    def _create_minefield(self):
        self.minefield = [[self._create_tile(row, col) for col in range(10)] for row in range(10)]
        for row in self.minefield:
            for tile in row:
                for neighbor_coords in tile.get_8_direction_neighbors():
                    if -1 not in neighbor_coords and 10 not in neighbor_coords: 
                        neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                        if neighbor.type == "bomb":
                            tile.bombs_near += 1
                if tile.bombs_near > 0:
                    tile.type = "near_bomb"




# determines if this is imported module or module being run 
if __name__ == "__main__":
    root = tk.Tk()

    instance = Minesweeper(root)
    instance.pack(side="top", fill="both", expand=False)
    instance.canvas.pack()

    root.title("Minesweeper!")
    root.resizable(False, False)
    root.mainloop()