from __future__ import annotations
import random

from typing import Iterator,Tuple, TYPE_CHECKING

import tcod

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from entity import Entity

class RectangularRoom:
    # Takes the x and y coordinates of the top left corner, and computes the bottom right
    # Corner based on the w and h parameters(width and height).
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x+width
        self.y2 = y+height
    
    # Is a property that acts like a read-only variable for RectangularRoom class.
    # Describes the x and y coordinates of the center of a room.
    @property
    def center(self)->Tuple[int,int]:
        center_x = int((self.x1+self.x2)/2)
        center_y = int((self.y1 + self.y2)/2)

        return center_x, center_y
    
    # Returns two slices which represents the inner portion of the room.
    # The principal part to dig out for a room in a dungeon generator.
    @property


    def inner(self)->Tuple[slice,slice]:
        """Return the inner area of this room as a 2D array index"""
        # This return operation ensures that we'll always have at least a one tile wide wall 
        # Between the room adding +1 to x1 and y1.
        return slice(self.x1+1,self.x2),slice(self.y1+1,self.y2)
    
    # Checks if the room and another room intersects or not.
    # Return True or it they do, or False if they not.
    def intersects(self,other:RectangularRoom)-> bool:
        """Return True if this room overlaps with another rectangular room"""
        return(
            self.x1<=self.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


# Takes two arguments, both Tuples consisting of two integers. It should return an iterator of
# A tuple of two ints. All the Tuples[int,int] will be cordinates in the map.    
def tunnel_between(
        start:Tuple[int,int],end:Tuple[int,int]
) -> Iterator[Tuple[int,int]]:
    """Return an L-shaped tunnel between these two points."""
    # We grab the coordinates out of the Tuples.
    x1, y1 = start
    x2, y2 = end
    

    # Now we randomly pick two options: Moving horizontally, then vertically or the opposite.
    # Based on whats chosen, set the corner_x and corner_y values to diferent points.
    if(random.random()<0.5):#50% chance
        
        # Move horizontally, then vertically
        corner_x, corner_y = x2,y1
    else:
        # Move vertically, then horizontally
        corner_x,corner_y=x1,y2
    
    
    # Generate the cordinates for the tunnel

    # Special Annotation by Tato: Study about the Bresenham Algorithm.
    # tcod includes a function to draw bresenham line, and this function let us
    # to get a line from one point to another. In this case, we get one line, then 
    # Another to create an L shaped tunnel. Tolist converts the points to a list.
        
    # Yield returns a generator. We return the values but keep the local state.    
    for x, y in tcod.los.bresenham((x1,y1),(corner_x,corner_y)).tolist():
        yield x,y
    for x,y in tcod.los.bresenham((corner_x,corner_y),(x2,y2)).tolist():
        yield x,y

# We pass it fewer arguments:
"""
max_rooms: The maximum number of rooms alowwed in the dungeon. Used to control our iteration.
room_min_size: The minimum size of the room
room_max_size: The maximum size of the room
room_min_size: For both the width and the height of one room to carve out.
map_width and map_height: The width and height of the GameMap to create.
player: The player Entity, needed to know where to place the player.
"""
def generate_dungeon(
        max_rooms: int,
        room_min_size:int,
        room_max_size:int,
        map_width:int,
        map_height:int,
        player: Entity,
) -> GameMap:
    """Generate a new Dungeon Map"""
    # Creating the initial GameMap.
    dungeon = GameMap(map_width,map_height)

    # Creating a running list of the game rooms.
    rooms: list[RectangularRoom]=[]

    # We iterate from 0 to max_rooms. This algorithm may or may not place a room depending on
    # If it intersects with another, so we won't know how many rooms we're going to end up with,
    # But at least that number can't exceed a certain amount.
    for r in range(max_rooms):

        # We use the given minimum and maximum size of the room to set the room's width and height.
        # Then we get a random pair of x,y coordinates to try and place the room down.
        # The coordinates must be between 0 and the map's width and heights.
        room_width = random.randint(room_min_size,room_max_size)
        room_height = random.randint(room_min_size,room_max_size)

        x = random.randint(0,dungeon.width-room_width-1)
        y = random.randint(0,dungeon.height - room_height-1)

        #"RectangularRoom class makes rectangle easier to work with"
        new_room = RectangularRoom(x,y,room_width,room_height)

        # Run Through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue
        # if there are no intersections then the room is valid

        #Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.x, player.y = new_room.center

        else: #All rooms after the first
            #Dig out a tunnel between this room and the previous one

            # Similar to how the tunnel was dug before, but except this time, we're using
            # a negative index with rooms to grab the previous room and connecting the new
            # room to it.
            for x,y in tunnel_between(rooms[-1].center,new_room.center):
                dungeon.tiles[x,y] = tile_types.floor
        
        # Finally, append the new room to the list.
        rooms.append(new_room)
    return dungeon
