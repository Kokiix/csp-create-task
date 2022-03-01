import tkinter as tk
import random as r
import math

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
        self.canvas.tag_bind("tile", "<Button-1>", self._on_tile_click) # add tile click event
        self._create_field()


    def _on_tile_click(self, event):
        tile_x = math.floor(event.x / self.tile_length)
        tile_y = math.floor(event.y / self.tile_length)
        
        # now make other non bombs delete as well

        self.canvas.delete(self.field[tile_y][tile_x])


    def _prepare_default_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # swap colors in row & stagger colors between rows
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2
        
        tile = self.canvas.create_rectangle(
            x, y, x + self.tile_length, y + self.tile_length, 
            fill = fill_color, outline = "", tags = "tile")

        return tile


    def _create_field(self):
        self.field = [[self._prepare_default_tile(row, col) for col in range(10)] for row in range(10)]



# determines if this is imported module or module being run 
if __name__ == "__main__":
    root = tk.Tk()

    instance = Minesweeper(root)
    instance.pack(side="top", fill="both", expand=False)
    instance.canvas.pack()

    root.mainloop()