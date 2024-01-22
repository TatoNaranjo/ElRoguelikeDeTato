from typing import Tuple

import numpy as np #Type: ignore

#Tile graphics structured type compatible with Console.tiles_rgb.
"""
dtype creates a datatype which numpy can use, which behaves similarity to a struct in a language
like c.
"""

"""
Our data type is made up of three parts:
ch: The character represented in integer format, we'll translate it from the integer into Unicode
fg: The foreground color: "3B" means 3 unsigned bytes which can be used for RGB color codes.
bg: The Background Color. Symilar to fg.

We're taking this data and using it in the next bit.
"""
graphic_dt = np.dtype(
    [
        
        ("ch",np.int32), #Unicode codepoint,
        ("fg","3B"), # 3 unsigned bytes, for RGB colors
        ("bg","3B",)
    ]
)
# Tile struct used for statically defined tile data.

"""
Another dtype which we'll use in the actual tile itself. It's also made up of three parts:
walkable: a boolean that describes if the player can walk across this tile.
transparent: a boolean that describes if this file does or does not block the
             fiel of view.

dark: this uses our previously defined dtype which holds the character to print, the foreground
      color, and the background color. It's called dark because later on we'll want to 
      differenciate between tiles that are and aren't in the field of view. Dark will represent
      tiles that are not in the current field of view.

light: Will hold the information about what our tile looks like when it's in the Field of View
"""
tile_dt = np.dtype(
    [
        ("walkable",bool), # True if this tile can be walked over.
        ("transparent",bool), # True if this tile doesn't block FOV
        ("dark", graphic_dt), # Graphics for when this tile is not in FOV.
        ("light",graphic_dt) #Graphics for when the tile is in FOV
    ]
)

# Helper function tha takes the parameters walkable, transparent and dark, it creates a
# numpy array of just the one tile_dt element and returns it.
def new_tile(
        *,
        walkable:int,
        transparent:int,
        dark:Tuple[int,Tuple[int,int,int],Tuple[int,int,int]],
        light: Tuple[int, Tuple[int,int,int], Tuple[int,int,int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable,transparent,dark,light),dtype = tile_dt)

#SHROUD represents unexplored, unseen tiles.
SHROUD = np.array((ord(" "),(255,255,255),(0,0,0)), dtype=graphic_dt)

# There are two tile types. We've got two, floor and wall.

# Floor is both walkable and transparent. It's dark attribute consists of the space character.
# (Maybe i'll change it), and defines its foreground color as white(won't matter since it's an empty space),
# and a background color.

floor = new_tile(
    walkable=True, 
    transparent=True, 
    dark=(ord(" "),(255,255,255),(50,50,150)),
    light = (ord(" "),(255,255,255),(200,180,50)),
)
# Wall is neither walkable nor transparent, and it's dark attribute differs from floor slightly in
# its background.
wall = new_tile(
    walkable=False, 
    transparent=False, 
    dark = (ord(" "),(255,255,255),(0,0,100)),
    light = (ord(" "),(255,255,255),(130,110,50)),
)