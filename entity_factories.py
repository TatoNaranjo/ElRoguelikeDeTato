from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

# Player Entity uses the Actor Class
player = Actor(
    char = "@",
    color = (255,255,255),
    name = "Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30,defense=2,power=5),
)
# Orc Entity uses the Actor Class
orc = Actor(
    char='o',
    color=(23,127,63),
    name = "Orc",
    ai_cls = HostileEnemy,
    fighter=Fighter(hp = 10, defense = 0, power=3),
)
# Troll Entity uses the Actor Class
troll = Actor(
    char = "T",
    color = (0,127,0),
    name= "Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16,defense=1,power=4),
)