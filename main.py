import tkinter as tk
import random as r
import math




class Tile(object):
    def __init__(self, canvas, length, color, tile_type, row, col):
        self.canvas = canvas
        self.type = tile_type
        self.row = row
        self.col = col

        x = self.col * length
        y = self.row * length
        self.tile_id = self.canvas.create_rectangle(
            x, y,
            x + length, y + length,
            fill = color,
            outline = "",
            tags = ["tile", self.type])



    def clear(self):
        self.canvas.delete(self.tile_id)
        self.type = "cleared"



    def get_neighbors(self):
        return [[self.row - 1, self.col], [self.row + 1, self.col], [self.row, self.col - 1], [self.row, self.col + 1]]




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
        for neighbor_coords in tile.get_neighbors():
            if -1 not in neighbor_coords and 10 not in neighbor_coords:
                neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                if neighbor.type != "bomb" and neighbor.type != "cleared":
                    self._recursive_tile_clear(neighbor)



    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]

        if tile.type == "blank":
            self._recursive_tile_clear(tile)



    def _create_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # MAKE EASIER TO READ
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2

        is_bomb = True if r.random() > 0.10 else False # temporary bomb assignment for debug
        
        return Tile(
            self.canvas, 
            self.tile_length, 
            fill_color if is_bomb else "#53131E", # debug outline
            "bomb" if not is_bomb else "blank",
            row, col)



    def _create_minefield(self):
        self.minefield = [[self._create_tile(row, col) for col in range(10)] for row in range(10)]




# determines if this is imported module or module being run 
if __name__ == "__main__":
    root = tk.Tk()

    instance = Minesweeper(root)
    instance.pack(side="top", fill="both", expand=False)
    instance.canvas.pack()

    root.mainloop()