from components.ai import HostileEnemy
from components import consumable,equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

# Player Entity uses the Actor Class
player = Actor(
    char = "@",
    color = (255,255,255),
    name = "Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30,base_defense=1,base_power=2),
    inventory=Inventory(capacity = 26),
    level = Level(level_up_base = 200),
)
# Orc Entity uses the Actor Class
orc = Actor(
    char='o',
    color=(23,127,63),
    name = "Orc",
    ai_cls = HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp = 10, base_defense = 0, base_power=3),
    inventory=Inventory(capacity = 0),
    level= Level(xp_given=35),
)
# Troll Entity uses the Actor Class
troll = Actor(
    char = "T",
    color = (0,127,0),
    name= "Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16,base_defense=1,base_power=4),
    inventory=Inventory(capacity = 0),
    level = Level(xp_given=100)
)

# Confusion uses the Item Class
confusion_scroll = Item(
    char = "~",
    color = (207,63,255),
    name = "Confussion Scroll",
    consumable = consumable.ConfusionConsumable(number_of_turns=10),
)


fireball_scroll = Item(
    char = "~",
    color = (255,0,0),
    name = "Fireball Scroll",
    consumable= consumable.FireballDamageConsumable(damage=12,radius=3),
)


#Health Entity uses the Item Class

health_potion = Item(
    char = "!",
    color = (127,0,255),
    name = "Health Potion",
    consumable = consumable.HealingConsumable(amount = 8),
)

# Lightning Entity uses the Item Class

lightning_scroll = Item(
    char = "~",
    color = (255,255,0),
    name = "Lightning Scroll",
    consumable = consumable.LightningDamageConsumable(damage=20, maximum_range=5)

)

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)