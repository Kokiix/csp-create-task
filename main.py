import tkinter as tk
import random as r
import math
import threading
import time

# Modules that need to be installed

# python3 -m pip install playsound==1.2.2
# python3 -m pip install Pillow
from PIL import ImageTk, Image
from playsound import playsound




class Minesweeper(tk.Frame):
    def __init__(self, parent, board_pixel_height):
        """
        Defines board sizes and game constants
        """
        self.root = parent
        tk.Frame.__init__(self, self.root)


        # Set up board size; default size is medium
        self.board_tile_width = 18
        self.board_tile_height = 14
        self.mine_number = 40
        self.tile_length = board_pixel_height / self.board_tile_height
        self.board_pixel_width = int(self.tile_length * self.board_tile_width)   
        self.board_pixel_height = int(self.tile_length * self.board_tile_height)
        self.canvas = tk.Canvas(
            root, 
            width = self.board_pixel_width, height = self.board_pixel_height, 
            highlightthickness = 0, bg = "white")
        

        # Menu setup
        self.buttons = []
        self.button_font = ('Rockwell', int(self.board_pixel_height / 35))
        self.button_placeholder = tk.PhotoImage(width = 1, height = 1) # Make label pos based off of pixels instead of font size
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.button_padding = 0.2
        self.button_y_offset = 0.25

        self.title_screen = ImageTk.PhotoImage(Image.open("title.png").resize(
            (int(self.board_pixel_width), int(self.board_pixel_height * 0.40))))


        # Dancing mochi
        bg_img = Image.open(
            "funnybunny_gray.jpg").resize(
            (int(self.board_pixel_width * 0.525), int(self.board_pixel_height * 0.525)))
        self.mochi_pos_1 = ImageTk.PhotoImage(bg_img.rotate(25, fillcolor = "white", expand = 1))
        self.mochi_pos_2 = ImageTk.PhotoImage(bg_img.rotate(-25, fillcolor = "white",  expand = 1))
        self.menu_active = True


        # Miscallaneous setup
        self.start_time = 0
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)
        self.lose_screen = ImageTk.PhotoImage(Image.open("funnybunny_red.jpg").resize((self.board_pixel_width, self.board_pixel_height)))
        self.win_screen = ImageTk.PhotoImage(Image.open("funnybunny_green.jpg").resize((self.board_pixel_width, self.board_pixel_height)))
        self.rainbow_colors = {
            "#FF0000": "#7f0000", # Red
            "#FC6404": "#7e3101", # Orange
            "#FCC201": "#7e6100", # Gold
            "#029658": "#004b2c", # DARK Green
            "#2B6CC4": "#153662", # Blue
            "#1ABC9C": "#0c5e4e", # Teal
            "#6454AC": "#312956", # Purple
            "#FF1DCE": "#8e006f" # Magenta
        }

        self._start_menu(None)        

        
        

    def _start_menu(self, event):
        """
        Creates components for the main menu (title, dance, buttons)
        """
        self.canvas.delete("all")
        self.menu_active = True


        # Click is used after game over to get to the menu; this binding needs to be reset
        self.root.unbind("<Button>")
        self.canvas.tag_bind("clickable", "<Button>", self._on_tile_click)


        # Setup difficulty buttons; board size can change between loops
        button_width = int(self.board_pixel_width / 4)
        button_height = int(self.board_pixel_height / 10)

        for button_number in range(3):
            button = tk.Button(
                self.root,
                fg = "#696773",
                bd = 3,
                text = self.difficulties[button_number],
                font = self.button_font,
                image = self.button_placeholder,
                width = button_width,
                height = button_height,
                # Assign callback to each button along with id
                command = lambda buttonid = button_number : self._on_menu_select(buttonid),
                # Displays text and placeholder instead of just the placeholder
                compound = "c",
                overrelief = tk.GROOVE
                )
            button.pack()
            button.place(relx = 0.85, rely = self.button_padding * (button_number + 1) + self.button_y_offset, anchor = "center")
            self.buttons.append(button)


        # Create title, start mochi dance
        displayed_bg = self.canvas.create_image(
                    self.board_pixel_width / 3, self.board_pixel_height / 1.55, 
                    anchor = "center", 
                    image = self.mochi_pos_1)
        self.canvas.create_image(
            0, 0, 
            anchor = "nw", 
            image = self.title_screen)
        threading.Thread(target = self._bun_dance, args = (displayed_bg,), daemon = True).start()  
              



    def _bun_dance(self, bg):
        """
        MOCHI DANCE MOCHI DANCE
        """
        while self.menu_active == True:
            time.sleep(0.75)
            self.canvas.itemconfig(bg, image = self.mochi_pos_2)
            time.sleep(0.75)
            self.canvas.itemconfig(bg, image = self.mochi_pos_1)




    def _on_menu_select(self, buttonid):
        """
        Listens for button press and starts the game
        """

        # Clear start menu
        self.menu_active = False
        self.canvas.delete("all")
        for button in self.buttons:
            button.destroy()


        # Buttonid tells which is pressed
        if buttonid == 0: # Easy
            self.board_tile_width = 10
            self.board_tile_height = 8
            self.mine_number = 10
        elif buttonid == 1: # Medium
            self.board_tile_width = 18
            self.board_tile_height = 14
            self.mine_number = 40
        elif buttonid == 2: # Hard
            self.board_tile_width = 24
            self.board_tile_height = 20
            self.mine_number = 99


        # Sizes need to change based on the new amount of tiles
        self.tile_length = self.board_pixel_height / self.board_tile_height
        self.board_pixel_width = self.tile_length * self.board_tile_width
        self.canvas.configure(width = self.board_pixel_width)
        self.root.geometry("%dx%d" % (self.board_pixel_width, self.board_pixel_height))


        # Generate the minefield, a 2D array of Tile objects
        self.minefield = [[Tile(self.canvas, self.tile_length, row, col) for col in range(self.board_tile_width)] for row in range(self.board_tile_height)] # MAKE IT SO CANVAS DOESN'T HAVE TO BE PASSED TO EVERY TILE
        self.tiles_cleared = 0


        # Creates invisible rectangle to intercept first click
        self.first_click_detector_id = self.canvas.create_rectangle(
            0, 0, self.board_pixel_width, self.board_pixel_height,
            fill = "",
            outline = "",
            tags = "first_click_setup")




    def _on_first_click(self, event):
        """
        Ensures player gets open space around first click
        """


        # Figure out tile first click corresponds to
        first_tile_col = math.floor(event.x / self.tile_length)
        first_tile_row = math.floor(event.y / self.tile_length)
        first_tile = self.minefield[first_tile_row][first_tile_col]


        # Distribute mines, ensuring not within 1 tile radius of cursor
        for mine_num in range(self.mine_number):
            mine_tile = first_tile
            while ((first_tile_col - 2 < mine_tile.col < first_tile_col + 2) and \
                    (first_tile_row - 2 < mine_tile.row < first_tile_row + 2)) or \
                    mine_tile.type == "mine":
                mine_tile = r.choice(r.choice(self.minefield))
            mine_tile.type = "mine"

            # Update numbers for all tiles around mine
            for neighbor in self._get_neighbors(mine_tile):
                if neighbor.type != "mine":
                    neighbor.mines_near += 1
                    neighbor.type = "near_mine"


        # Begin the game
        self.canvas.delete(self.first_click_detector_id)
        self._clear_tiles(first_tile)
        self.start_time = time.time()

    


    def _get_neighbors(self, tile):
        """
        Find the 8 tiles around a given tile
        """


        # Find tiles
        neighbor_coords = [
            [tile.row - 1, tile.col], [tile.row - 1, tile.col - 1], [tile.row - 1, tile.col + 1],
            [tile.row + 1, tile.col], [tile.row + 1, tile.col - 1], [tile.row + 1, tile.col + 1], 
            [tile.row, tile.col + 1], [tile.row, tile.col - 1]]


        # Remove ones that fall outside window
        final_tileset = []
        for coord_pair in neighbor_coords:
            if -1 not in coord_pair                        and \
                self.board_tile_width != coord_pair[1]     and \
                self.board_tile_height != coord_pair[0]:

                final_tileset.append(self.minefield[coord_pair[0]][coord_pair[1]])
        return final_tileset




    def _on_tile_click(self, event):
        """
        Simple click handler
        """

        
        # Find clicked tile        
        tile_column = math.floor(event.x / self.tile_length)
        tile_row = math.floor(event.y / self.tile_length)
        tile = self.minefield[tile_row][tile_column]


        # Left click
        if event.num == 1 and tile.state == tk.NORMAL and not tile.has_flag:
            if tile.type != "mine":
                self._clear_tiles(tile)
                self.canvas.pack() # Reload visual changes
            else:
                self._display_end_screen("loss")
        

        # Right click
        elif event.num == 3 and tile.state == tk.NORMAL:
            if tile.has_flag:
                tile.deflag()
            else:
                tile.flag()




    def _clear_tiles(self, tile):
        """
        Recursive algorithm to clear tiles; stops on numbered tiles
        """


        # Update tiles
        tile.clear()
        self.tiles_cleared += 1
        if self.tiles_cleared == self.board_tile_height * self.board_tile_width - self.mine_number:
            self._display_end_screen("win")
            return


        # Spread to all nearby tiles if current isn't numbered
        # if current numbered add borders
        if tile.type != "near_mine":
            for neighbor in self._get_neighbors(tile):
                if neighbor.state == tk.NORMAL and not neighbor.has_flag:
                    self._clear_tiles(neighbor)
        else:
            for neighbor in self._get_neighbors(tile):
                if neighbor.state == tk.NORMAL:
                    xdiff = neighbor.col - tile.col
                    ydiff = neighbor.row - tile.row
                    direction = None
                    
                    if 0 in [xdiff, ydiff]:
                        if xdiff == 1:
                            direction = "W"
                        elif xdiff == -1:
                            direction = "E"

                        if ydiff == 1:
                            direction = "N"
                        elif ydiff == -1:
                            direction = "S"
                        neighbor.create_border(direction)




    def _display_end_screen(self, result):
        """
        Start the threads for end audio and animation
        """


        end_screen = self.canvas.create_image(
            self.board_pixel_width / 2, self.board_pixel_height / 2, 
            anchor = "center", 
            image = self.lose_screen if result == "loss" else self.win_screen)
        threading.Thread(target = playsound, args = ("boing.wav",), daemon = True).start()
        threading.Thread(target = self._end_animation, args = (end_screen,), daemon = True).start()


        if result == "win":
            print("Final Score: %d seconds" % round(time.time() - self.start_time, 2))




    def _end_animation(self, img):
        """
        Mochi appears & slides off the screen; mines revealed
        """
        time.sleep(0.75)


        # Disable input
        for row in self.minefield:
            for tile in row:
                self.canvas.itemconfig(tile.tile_id, tags = "", activefill = "")


        # Image slides off screen in random direction
        img_x = 0
        img_y = 0
        x_shift = r.choice([-0.5, 0, 0.5])
        y_shift = r.choice([-0.5, 0, 0.5]) if x_shift != 0 else r.choice([-0.5, 0.5])
        for move in range(int(self.board_pixel_width / 15)):
            self.canvas.move(img, img_x, img_y)
            img_x += x_shift
            img_y += y_shift
            time.sleep(0.005)


        # Rainbow color mines
        for row in self.minefield:
            for tile in row:
                pad = tile.length * 0.3
                if tile.type == "mine":
                    tile.deflag()
                    c = r.choice(list(self.rainbow_colors))
                    self.canvas.itemconfig(tile.tile_id, fill = c)
                    self.canvas.create_oval(
                        tile.x + pad, tile.y + pad,
                        tile.x + tile.length - pad, tile.y + tile.length - pad,
                        outline = "",
                        fill = self.rainbow_colors[c])
        

        # Get back to main menu
        self.root.bind("<Button>", self._start_menu)




class Tile(object):




    number_colors = [
            "#1976D2", # Blue
            "#388E3C", # Green
            "#D32F2F", # Red
            "#7B1FA2", # Purple
            "#FF8F00", # Gold
            "#0097A7", # Aqua
            "#424242", # Black
            "#9E9E9E"] # Silver




    def __init__(self, canvas, length, row, col):
        self.canvas = canvas
        self.row = row
        self.col = col
        self.length = length
        self.x = self.col * self.length
        self.y = self.row * self.length


        # Type can be blank, near_mine, or mine; type never changes
        # State is if a tile is "covered" or not
        self.type = "blank"
        self.state = tk.NORMAL


        # Miscallaneous
        self.tone = "light" if (self.row + self.col) % 2 == 0 else "dark"
        self.mines_near = 0
        self.text_id = None


        # Tile components
        self.font = ('Helvetica', int(self.length / 2), 'bold')

        self.flag_parts = []
        self.has_flag = False

        self.border_width = self.length * 0.1
        self.borders = []

        
        # Build final canvas object
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.length, self.y + self.length,
            fill = "#AAD751" if self.tone == "light" else "#A2D149",
            activefill = "#BFE17D" if self.tone == "light" else "#B9DD77",
            outline = "",
            tags = ["clickable"],
        )




    def clear(self):
        """
        Updates tile color, state, and borders on clear
        """


        # Color from green to brown
        self.canvas.itemconfig(self.tile_id, activefill = "", fill = "#E5C29F" if self.tone == "light" else "#D7B899")


        # Clear borders
        for border in self.borders:
            self.canvas.delete(border)
        self.borders = []


        # Create text for tiles near mines
        if self.type == "near_mine":
            self.text_id = self.canvas.create_text(
                self.x + self.length / 2, self.y + self.length / 2, 
                text = str(self.mines_near),
                fill = Tile.number_colors[self.mines_near - 1],
                font = self.font)

        self.state = tk.DISABLED




    def create_border(self, side):
        """
        Adds tile border on given side
        """

        # how do i explain this
        x1 = self.x + ((self.length + self.border_width) if side == "E" else 0)
        y1 = self.y + ((self.length + self.border_width) if side == "S" else 0)

        x2 = self.x - (self.border_width if side == "W" else -1 * self.length)
        y2 = self.y - (self.border_width if side == "N" else -1 * self.length)

        self.borders.append(self.canvas.create_rectangle(
            x1, y1,
            x2, y2,
            outline = "",
            fill = "#8FB044"))




    def flag(self):
        """
        Creates a flag for the tile
        The numbers are very fine tuned
        """


        # Flagpole
        pole_x = self.x + self.length * 0.35
        pole_y = self.y + self.length * 0.20
        pole_width = self.length * 0.08
        pole_height = self.length * 0.55
        flag_pole = self.canvas.create_rectangle(
            pole_x, pole_y,
            pole_x + pole_width, pole_y + pole_height,
            fill = "red", outline = "")


        # Flag cloth
        cloth_tip_x = pole_x + self.length * 0.4
        cloth_tip_y = pole_y + self.length * 0.1
        cloth_base_y = pole_y + self.length * 0.25
        cloth_points = [pole_x + pole_width, pole_y, 
        cloth_tip_x, cloth_tip_y, 
        pole_x + pole_width, cloth_base_y]
        flag_cloth = self.canvas.create_polygon(
            cloth_points,
            fill = "red", outline = "")


        # Flag base
        base_x_offset = pole_width * 0.5
        base_y_offset = pole_height * 0.3
        flag_base = self.canvas.create_arc(
            pole_x - base_x_offset, pole_y + pole_height * 0.9,
            pole_x + pole_width + base_x_offset, pole_y + pole_height + base_y_offset,
            extent = 180, fill = "red", outline = "")


        # Build flag and stop it from blocking click
        self.flag_parts = [flag_pole, flag_cloth, flag_base]
        for flag_part in self.flag_parts:
            self.canvas.itemconfig(flag_part, tags = ["clickable"])
        self.has_flag = True




    def deflag(self):
        """
        Remove flag
        """


        for flag_part in self.flag_parts:
            self.canvas.delete(flag_part)
        self.flag_parts.clear()
        self.has_flag = False




if __name__ == "__main__":
    root = tk.Tk()


    # Start the game using screen height (100 is taskbar height)
    minesweeper = Minesweeper(root, root.winfo_screenheight() - 100)
    minesweeper.pack(fill="both", expand=True)
    minesweeper.canvas.pack()


    # Center/config the window and begin the game
    width = minesweeper.board_pixel_width
    height = minesweeper.board_pixel_height
    window_x = root.winfo_screenwidth() / 2 - (width / 2)
    window_y = 10

    root.geometry('%dx%d+%d+%d' % (width, height, window_x, window_y))
    root.title("Minesweeper!")
    root.resizable(False, False)
    root.mainloop()