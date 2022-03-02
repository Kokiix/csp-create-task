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
        self.color = "light" if color == "#aad751" else "dark"

        self.x = self.col * self.length
        self.y = self.row * self.length

        self.text_id = None
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.length, self.y + self.length,
            fill = color,
            outline = "",
            tags = ["tile", self.type])



    def _get_distance_color(self):
        match self.bombs_near:
            case 1: return "#1976D2"
            case 2: return "#388E3C"
            case 3: return "#D32F2F"
            case 4: return "#7B1FA2"



    def clear(self):
        self.canvas.itemconfig(self.tile_id, fill = "#E5C29F" if self.color == "light" else "#D7B899")
        if self.type == "near_bomb":
            self.text_id = self.canvas.create_text(
                self.x + self.length / 2, self.y + self.length / 2, 
                text = str(self.bombs_near),
                fill = self._get_distance_color(),
                font = self.font)
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




class Minesweeper(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.board_length = 700
        self.board_width = 560
        self.tile_length = self.board_length / 10
        self.canvas = tk.Canvas(
            root, 
            width = self.board_width, height = self.board_length, 
            highlightthickness = 0)
        self.first_click_detector_id = 0
        self.canvas.tag_bind("tile", "<Button-1>", self._on_tile_click)
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)
        self.minefield = [[self._create_tile(row, col) for col in range(10)] for row in range(10)]
        self._setup_first_click_detector()



    def _recursive_tile_clear(self, tile):
        tile_type = tile.type
        tile.clear()
        if tile_type != "near_bomb":
            for neighbor_coords in tile.get_4_direction_neighbors():
                if -1 not in neighbor_coords and 10 not in neighbor_coords:
                    neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                    if neighbor.type == "blank" or neighbor.type == "near_bomb":
                        self._recursive_tile_clear(neighbor)


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]

        if tile.type != "bomb":
            self._recursive_tile_clear(tile)
            self.canvas.pack()



    def _create_tile(self, row, col):
        x = col * self.tile_length
        y = row * self.tile_length
        
        # MAKE EASIER TO READ
        color1 = "#aad751" if row % 2 == 0 else "#a2d149"
        color2 = "#aad751" if color1 == "#a2d149" else "#a2d149"
        fill_color = color1 if col % 2 == 0 else color2
        
        return Tile(
            self.canvas, 
            self.tile_length, 
            fill_color,
            "blank",
            row, col)
        



    def _setup_first_click_detector(self):
        self.first_click_detector_id = self.canvas.create_rectangle(
            0, 0, self.board_width, self.board_length,
            fill = "",
            outline = "",
            tags = "first_click_setup")




    def _on_first_click(self, event):
        first_tile_column = math.floor(event.x / self.tile_length)
        first_tile_row = math.floor(event.y / self.tile_length)
        first_tile = self.minefield[first_tile_row][first_tile_column]

        for bomb_num in range(10):
            bomb_tile = first_tile
            while bomb_tile == first_tile:
                bomb_tile = r.choice(r.choice(self.minefield))
            bomb_tile.type == "bomb"

            self.canvas.itemconfig(bomb_tile.tile_id, fill = "#FFF012")# DEBUG

            for neighbor_coords in bomb_tile.get_8_direction_neighbors():
                if -1 not in neighbor_coords and 10 not in neighbor_coords:
                    neighbor = self.minefield[neighbor_coords[0]][neighbor_coords[1]]
                    neighbor.bombs_near += 1
                    neighbor.type = "near_bomb"

        self.canvas.delete(self.first_click_detector_id)





if __name__ == "__main__":
    root = tk.Tk()

    instance = Minesweeper(root)
    instance.pack(side="top", fill="both", expand=False)
    instance.canvas.pack()

    root.title("Minesweeper!")
    root.resizable(False, False)
    root.mainloop()