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

        self.delete_list = []
        self._create_minefield()



    def _clear_tile_row(self, cleared_tile_ids, vdir):
        clear_tile_ids = []
        for index, tile_id_below in enumerate(cleared_tile_ids):
            tags = self.canvas.gettags(tile_id_below)
            if "bomb" in tags or len(tags) == 0:
                continue

            tile_row = int(tags[2][0]) + vdir
            tile_column = int(tags[2][1])

            if tile_row < 0 or tile_row > 9:
                [self.canvas.delete(tile_id) for tile_id in self.delete_list]
                self.delete_list.clear()
                return

            tile_id = self.minefield[tile_row][tile_column]

            at_previous_tile = False
            at_edge = False
            for hdir in range(-1, 2, 2):
                while not (at_previous_tile or at_edge):
                    if tile_column == 0 or tile_column == 9:
                        at_edge = True
                    elif cleared_tile_ids[index - 1] == self.minefield[tile_row + (-1 * vdir)][tile_column + hdir]:
                        at_previous_tile = True
                    elif "bomb" in self.canvas.gettags(self.minefield[tile_row][tile_column]) or\
                        len(self.canvas.gettags(self.minefield[tile_row][tile_column])) == 0:
                        break
                    tile_column += hdir
                    tile_id = self.minefield[tile_row][tile_column]
                    clear_tile_ids.append(tile_id)
                    self.delete_list.append(tile_id)

        if len(clear_tile_ids) != 0:
            self._clear_tile_row(clear_tile_ids, vdir)


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile_id = self.minefield[tile_row][tile_column]
        staggered_tile_id = self.minefield[tile_row + (-1 if tile_column < 9 else 1)][tile_column]

        if "clear" in self.canvas.gettags(tile_id):
            self._clear_tile_row([staggered_tile_id], 1)
            self._clear_tile_row([tile_id], -1)


    def _prepare_default_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # swap colors in row & stagger colors between rows
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2

        is_bomb = True if r.random() > 0.10 else False
        
        tile_id = self.canvas.create_rectangle(
            x, y, x + self.tile_length, y + self.tile_length, 
            fill = fill_color if is_bomb else "#53131E", outline = "", tags = "tile")
        self.canvas.addtag_withtag("bomb" if not is_bomb else "clear", tile_id)
        self.canvas.addtag_withtag(str(row) + str(col), tile_id)

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