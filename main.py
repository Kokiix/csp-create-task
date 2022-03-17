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
    def __init__(self, parent, board_pixel_height): # Height is passed in, then width is based on that because most monitors are horizontal
        self.root = parent
        tk.Frame.__init__(self, self.root)

        # Miscallaneous variables
        self.start_time = 0
        self.DARK_GREEN = "#A2D149"
        self.LIGHT_GREEN = "#AAD751"

        # Set up board size settings; default size is medium
        self.board_tile_width = 18
        self.board_tile_height = 14
        self.mine_number = 40
        self.tile_side_length = board_pixel_height / self.board_tile_height
        self.board_pixel_width = int(self.tile_side_length * self.board_tile_width)   
        self.board_pixel_height = int(self.tile_side_length * self.board_tile_height) 
        
        # Setup canvas using those size settings
        self.canvas = tk.Canvas(
            root, 
            width = self.board_pixel_width, height = self.board_pixel_height, 
            highlightthickness = 0, bg = "white")
        self.canvas.tag_bind("first_click_setup", "<Button-1>", self._on_first_click)

        # Import and scale images
        # self.menu_screen_title = TODO: ***ADRIAN STILL NEEDS TO DELIVER***
        self.menu_screen_bg = ImageTk.PhotoImage(Image.open("funnybunny_black.jpg").resize((int(self.board_pixel_width * 0.7), int(self.board_pixel_height * 0.7))))
        self.lose_screen = ImageTk.PhotoImage(Image.open("funnybunny_red.jpg").resize((self.board_pixel_width, self.board_pixel_height)))
        self.win_screen = ImageTk.PhotoImage(Image.open("funnybunny_green.jpg").resize((self.board_pixel_width, self.board_pixel_height)))

        # First time menu setup
        # Placeholder is to allow button configuration based off of pixels instead of font size
        self.button_placeholder = tk.PhotoImage(width = 1, height = 1)
        self.buttons = []
        self.menu_font = ('Helvetica', -1 * int(self.board_pixel_height / 35)) # TODO: ***IMPROVE MENU FONT SOME TIME***
        self._start_menu(None) # Menu isn't being called by key/mouse callback so no event info
        

    def _start_menu(self, event): # Event not used; required to register as mouse callback
        # Any click is used after game over to get to the menu; this needs to be reset
        self.root.unbind("<Button>")
        self.canvas.tag_bind("clickable", "<Button>", self._on_tile_click)

        # Setup menu background/title
        self.canvas.delete("all")
        self.canvas.create_image(
            self.board_pixel_width / 3, self.board_pixel_height / 1.55, 
            anchor = "center", 
            image = self.menu_screen_bg)

        # Setup difficulty buttons; board size can change between loops
        button_width = int(self.board_pixel_width / 4)
        button_height = int(self.board_pixel_height / 10)
        difficulties = ["Easy", "Medium", "Hard"]
        for button_number in range(3):
            button = tk.Button(
                self.root,
                bg = self.LIGHT_GREEN,
                bd = 0,
                text = difficulties[button_number],
                font = self.menu_font,
                image = self.button_placeholder,
                width = button_width,
                height = button_height,
                # Assign the menu button callback to each button along with id
                command = lambda buttonid = button_number : self._on_menu_select(buttonid),
                # Displays the text instead of just the placeholder
                compound = "c"
                )
            button.pack()

            button_padding = 0.2
            button_y_offset = 0.2
            button.place(relx = 0.85, rely = button_padding * (button_number + 1) + button_y_offset, anchor = "center")
            self.buttons.append(button)


    def _on_menu_select(self, buttonid):
        # Clear start menu
        self.canvas.delete("all")
        for button in self.buttons:
            button.destroy()

        # Choose difficulty based on id of button pressed
        if buttonid == 0: # easy
            self.board_tile_width = 10
            self.board_tile_height = 8
            self.mine_number = 10
        elif buttonid == 1: # medium
            self.board_tile_width = 18
            self.board_tile_height = 14
            self.mine_number = 40
        elif buttonid == 2: # hard
            self.board_tile_width = 24
            self.board_tile_height = 20
            self.mine_number = 99

        # Sizes need to change based on the new amount of tiles
        self.tile_side_length = self.board_pixel_height / self.board_tile_height
        self.board_pixel_width = self.tile_side_length * self.board_tile_width
        self.canvas.configure(width = self.board_pixel_width)
        self.root.geometry("%dx%d" % (self.board_pixel_width, self.board_pixel_height))
        self._start()


    def _start(self):
        self.tiles_cleared = 0

        self.minefield = [[self._create_tile(row, col) for col in range(self.board_tile_width)] for row in range(self.board_tile_height)]
        # Creates invisible rectangle over whole window blocking tile click;
        # canvas widget constructors return an id used to manipulate that widget
        self.first_click_detector_id = self.canvas.create_rectangle(
            0, 0, self.board_pixel_width, self.board_pixel_height,
            fill = "",
            outline = "",
            tags = "first_click_setup")


    def _create_tile(self, row, col):
        # Swap colors every other tile & every row
        color1 = self.LIGHT_GREEN if row % 2 == 0 else self.DARK_GREEN
        color2 = self.LIGHT_GREEN if color1 == self.DARK_GREEN else self.DARK_GREEN
        fill_color = color1 if col % 2 == 0 else color2
        
        return Tile(
            self.canvas, 
            self.tile_side_length, 
            fill_color,
            "blank",
            row, col)


    # Ensures player gets open space around first click
    def _on_first_click(self, event):
        # Figure out what tile first click corresponds to
        first_tile_col = math.floor(event.x / self.tile_side_length)
        first_tile_row = math.floor(event.y / self.tile_side_length)
        first_tile = self.minefield[first_tile_row][first_tile_col]

        # Distribute mines, making sure they aren't within 1 tile radius of cursor
        for mine_num in range(self.mine_number):
            mine_tile = first_tile
            while ((first_tile_col - 2 < mine_tile.col < first_tile_col + 2) and \
                    (first_tile_row - 2 < mine_tile.row < first_tile_row + 2)) or \
                    mine_tile.type == "mine":
                mine_tile = r.choice(r.choice(self.minefield))
            mine_tile.type = "mine"

            # self.canvas.itemconfig(mine_tile.tile_id, fill = "#FFF012") # DEBUG

            # Update numbers for all tiles around mine
            for neighbor in self._get_neighbors(mine_tile):
                if neighbor.type != "mine":
                    neighbor.mines_near += 1
                    neighbor.type = "near_mine"

        self.canvas.delete(self.first_click_detector_id)
        self._clear_tiles(first_tile)
        self.start_time = time.time()

    # Function is in Minesweeper class for access to the minefield
    def _get_neighbors(self, tile):
        # Find 8 surrounding tiles
        neighbor_coords = [
            [tile.row - 1, tile.col], [tile.row - 1, tile.col - 1], [tile.row - 1, tile.col + 1],
            [tile.row + 1, tile.col], [tile.row + 1, tile.col - 1], [tile.row + 1, tile.col + 1], 
            [tile.row, tile.col + 1], [tile.row, tile.col - 1]]

        # Remove coords that fall outside of the window
        final_tileset = []
        for coord_pair in neighbor_coords:
            if -1 not in coord_pair                        and \
                self.board_tile_width != coord_pair[1]     and \
                self.board_tile_height != coord_pair[0]:

                final_tileset.append(self.minefield[coord_pair[0]][coord_pair[1]])

        return final_tileset


    def _on_tile_click(self, event):
        tile_column = math.floor(event.x / self.tile_side_length)
        tile_row = math.floor(event.y / self.tile_side_length)
        tile = self.minefield[tile_row][tile_column]

        # Left click
        if event.num == 1 and not tile.has_flag:
            if tile.type == "blank" or tile.type == "near_mine":
                self._clear_tiles(tile)
                self.canvas.pack() # Reload visual changes
            elif tile.type == "mine":
                self._display_end_screen("loss")
        
        # Right click
        elif event.num == 3 and tile.type != "cleared":
            if tile.has_flag:
                tile.deflag()
            else:
                tile.flag()


    # Recursively clears tiles until reaching "near_mine" tiles
    def _clear_tiles(self, tile):
        # Tile type is saved before becoming "clear" type on tile.clear()
        tile_type = tile.type
        tile.clear()

        self.tiles_cleared += 1
        if self.tiles_cleared == self.board_tile_height * self.board_tile_width - self.mine_number:
            self._display_end_screen("win")
            return

        if tile_type != "near_mine":
            for neighbor in self._get_neighbors(tile):
                if neighbor.has_flag == False and (neighbor.type == "blank" or neighbor.type == "near_mine"):
                    self._clear_tiles(neighbor)


    def _display_end_screen(self, result):
        # playsound is async so program isn't held up by playing the entire sound
        # The end animation is asnyc because it has its own timings
        threading.Thread(target = playsound, args = ("boing.wav",), daemon = True).start()
        threading.Thread(target = self._end_animation, daemon = True).start()

        # Display FUNNY BUNNY
        self.canvas.create_image(
            self.board_pixel_width / 2, self.board_pixel_height / 2, 
            anchor = "center", 
            image = self.lose_screen if result == "loss" else self.win_screen)

        if result == "win":
            print("Final Score: %d seconds" % round(time.time() - self.start_time, 2))


    def _end_animation(self):
        time.sleep(2)
        # Faster animation on larger difficulties
        if self.mine_number == 10:
            sleep_amt = 0.005
        elif self.mine_number == 40:
            sleep_amt = 0.0005
        elif self.mine_number == 99:
            sleep_amt = 0.00005

        for row in self.minefield:
            for tile in row:
                self.canvas.itemconfig(tile.tile_id, tags = "")
                tile.bring_to_front()
                time.sleep(sleep_amt)

        # Press any mouse button to go back to start after anim
        self.root.bind("<Button>", self._start_menu)


class Tile(object):
    def __init__(self, canvas, height, color, tile_type, row, col):
        self.LIGHT_BROWN = "#E5C29F"
        self.DARK_BROWN = "#D7B899"
        self.LIGHT_GREEN = "#AAD751"

        self.canvas = canvas
        self.row = row
        self.col = col
        self.height = height
        self.x = self.col * self.height
        self.y = self.row * self.height

        self.type = tile_type
        self.mines_near = 0
        self.font = ('Helvetica',
        int(height / 2), 'bold')
        self.color = "light" if color == self.LIGHT_GREEN else "dark"

        self.has_flag = False
        self.flag_part_ids = []
        

        # Canvas widget constructors return an id used to manipulate that widget
        self.text_id = None
        self.tile_id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.height, self.y + self.height,
            fill = color,
            outline = "",
            tags = ["clickable", self.type])


    def clear(self):
        self.canvas.itemconfig(self.tile_id, fill = self.LIGHT_BROWN if self.color == "light" else self.DARK_BROWN)
        if self.type == "near_mine":
            self.text_id = self.canvas.create_text(
                self.x + self.height / 2, self.y + self.height / 2, 
                text = str(self.mines_near),
                fill = self._get_distance_color(),
                font = self.font)
        self.type = "cleared"


    # ALL NUMBERS ARE ARBITRARY & ACHIEVED THROUGH TRIAL/ERROR
    def flag(self):
        pole_x = self.x + self.height * 0.35
        pole_y = self.y + self.height * 0.20
        pole_width = self.height * 0.08
        pole_height = self.height * 0.55
        flag_pole = self.canvas.create_rectangle(
            pole_x, pole_y,
            pole_x + pole_width, pole_y + pole_height,
            fill = "red", outline = "")

        cloth_tip_x = pole_x + self.height * 0.4
        cloth_tip_y = pole_y + self.height * 0.1
        cloth_base_y = pole_y + self.height * 0.25
        cloth_points = [pole_x + pole_width, pole_y, 
        cloth_tip_x, cloth_tip_y, 
        pole_x + pole_width, cloth_base_y]
        flag_cloth = self.canvas.create_polygon(
            cloth_points,
            fill = "red", outline = "")

        base_x_offset = pole_width * 0.5
        base_y_offset = pole_height * 0.3
        flag_base = self.canvas.create_arc(
            pole_x - base_x_offset, pole_y + pole_height * 0.9,
            pole_x + pole_width + base_x_offset, pole_y + pole_height + base_y_offset,
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


    def bring_to_front(self):
        # Bring tile to front
        self.canvas.tag_raise(self.tile_id)

        if self.type == "mine":
            pass # Use SFX on mines
        elif self.text_id != None:
            # Bring tile text to front
            self.canvas.tag_raise(self.text_id)


if __name__ == "__main__":
    root = tk.Tk()

    # Game/window settings

    screen_height = root.winfo_screenheight() - 100 # 100px accounts for window title/taskbar

    minesweeper = Minesweeper(root, screen_height)
    minesweeper.pack(fill="both", expand=True)
    minesweeper.canvas.pack()

    width = minesweeper.board_pixel_width
    height = minesweeper.board_pixel_height
    # Center the window
    window_x = root.winfo_screenwidth() / 2 - (width / 2)
    window_y = 10
    root.geometry('%dx%d+%d+%d' % (width, height, window_x, window_y))
    root.title("Minesweeper!")
    root.resizable(False, False)

    root.mainloop()