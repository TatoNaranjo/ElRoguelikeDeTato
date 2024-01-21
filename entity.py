from typing import Tuple

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    # Initializer takes four arguments: x,y,char,color
    """
    x and y: Entity's coordinates on the map.
    char: character used to represent the entity.
    color: color we'll use when drawing the entity, represented on a RGB Tuple of three integers.
    """
    def __init__(self,x:int,y:int, char:str, color:Tuple[int,int,int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    #This method takes dx and dy as arguments, and uses them to modify the entity's position.
    def move(self,dx:int,dy:int)->None:
        # Move the entity by a given amount
        self.x +=dx
        self.y +=dy





