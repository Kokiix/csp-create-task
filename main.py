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
        self.canvas.tag_bind("tile", "<Button-1>", self._on_tile_click) # adds tile click event
        self._create_minefield()



    def _clear_blank_tiles(self, tile_id, tile_column, tile_row):
        self.canvas.delete(tile_id)
        # for direction in range(0, 2):
        #     column_or_row = tile_column if direction == 0 else tile_row
        #     for i in range(-1 if column_or_row > 0 else 1, 2 if column_or_row < (len(self.minefield) - 1) else 0, 2):
        #         tile_row = column_or_row + i if direction == 0 else tile_row
        #         tile_column = column_or_row + i if direction == 1 else tile_column
        #         scan_tile = self.minefield[tile_row][tile_column]

        #         tags = self.canvas.gettags(scan_tile)
        #         if len(tags) != 0 and "bomb" not in tags:
        #             self._clear_blank_tiles(scan_tile, tile_column + i, tile_row)


        for i in range(-1 if tile_column > 0 else 1, 2 if tile_column < (len(self.minefield) - 1) else 0, 2):
            scan_tile = self.minefield[tile_row][tile_column + i]
            tags = self.canvas.gettags(scan_tile)
            if len(tags) != 0 and "bomb" not in tags:
                print(str(tile_row) + " " + str(tile_column + i))
                self._clear_blank_tiles(scan_tile, tile_column + i, tile_row)
                
        for i in range(-1 if tile_row > 0 else 1, 2 if tile_row < (len(self.minefield) - 1) else 0, 2):
            scan_tile = self.minefield[tile_row + i][tile_column]
            tags = self.canvas.gettags(scan_tile)
            if len(tags) != 0 and "bomb" not in tags:
                self._clear_blank_tiles(scan_tile, tile_column, tile_row + i)


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile_id = self.minefield[tile_row][tile_column]

        if "blank" in self.canvas.gettags(tile_id):
            self._clear_blank_tiles(tile_id, tile_column, tile_row)


    def _prepare_default_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # swap colors in row & stagger colors between rows
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2

        is_bomb = True if r.random() > 0.10 else False # temporary bomb assignment for debug
        
        tile_id = self.canvas.create_rectangle(
            x, y, x + self.tile_length, y + self.tile_length, 
            fill = fill_color if is_bomb else "#53131E", outline = "", tags = "tile") # bombs temporarily highlighted for debug
        self.canvas.addtag_withtag("bomb" if not is_bomb else "blank", tile_id)

        return tile_id


    def _create_minefield(self):
        self.minefield = [[self._prepare_default_tile(row, col) for col in range(10)] for row in range(10)]



# determines if this is imported module or module being run 
if __name__ == "__main__":
    root = tk.Tk()

    instance = Minesweeper(root)
    instance.pack(side="top", fill="both", expand=False)
    instance.canvas.pack()

    root.mainloop()