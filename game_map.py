import numpy as np #type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    # The initializer takes width and height integers and assigns them in one line.
    def __init__(self,width:int,height:int):
        # We create a 2D array filled with the same values, which in this case is the
        # tile_types.floor that we created. This will fill self.tiles with floor tiles.
        self.width,self.height = width,height
        self.tiles = np.full((width,height),fill_value=tile_types.wall,order="F")
        self.visible = np.full((width,height),fill_value=False, order="F") # Tiles the player can currently see.
        self.explored = np.full((width,height),fill_value=False,order="F") # Tiles the player has seen before

        # Creates a small, three tile wide wall at the specified location.
        self.tiles[30:33,22] = tile_types.wall

    # This method returns true if the given x and y values are within the map's boundaries.
    # Used to ensure the player doesn't move beyond the map into the void.
    def in_bounds(self,x:int,y:int) ->bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0<=x<self.width and 0<=y<self.height
    
    # Using the console class's tiles_rgb method, now we render the entire map.
    # Much faster than console.print.
    def render(self,console:Console)->None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "Explored" array, then draw it with the "dark" colors.
        Otherwise the default is "SHROUD".
        
        """
        console.tiles_rgb[0:self.width,0:self.height] = np.select(
            condlist = [self.visible,self.explored],
            choicelist = [self.tiles["light"],self.tiles["dark"]],
            default = tile_types.SHROUD
        )
        