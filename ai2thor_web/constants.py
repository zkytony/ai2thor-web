#-------------------------------------------------------------------------------
# Overall Ai2Thor parameters (v2.7.2)
GRID_SIZE = 0.25
MOVE_STEP_SIZE = GRID_SIZE

H_ROTATION = 45   # Only 90 won't stuck
V_ROTATION = 30

FOV = 90   # from official doc: The default field of view when agentMode="default" is 90 degrees.

VISIBILITY_DISTANCE = 1.5
INTERACTION_DISTANCE = 1.5   # objects farther away than this cannot be interacted with.
AGENT_MODE = "default"   # from official doc: For iTHOR, it is often safest to stick with the default agent.

IMAGE_WIDTH = 600
IMAGE_HEIGHT = 600

# Need in order to not stuck the agent for sub-90 degree rotation.
# BUT, it actually DOES NOT WORK
CONTINUOUS = True
SNAP_TO_GRID = not CONTINUOUS

#------------------------------------------------------------------------------
# Ai2Thor spawning

# When enabled, the scene will attempt to randomize all moveable objects outside
# of receptacles in plain view. Use this if you want to avoid objects spawning
# out of view inside closed drawers, cabinets, etc.
FORCE_VISIBLE = False

# Determines if spawned objects will be settled completely static and unmoving,
# or if non-determenistic physics resolve their final position. Setting this to
# False will allow physics to resolve final positions, which can be used to
# spawn an object on a sloped receptacle but have it end up rolling off.
PLACE_STATIONARY = True

# Used to specify how many objects of a certain type will attempt to be
# duplicated somewhere in the scene. It does not guarantee this number of
# duplicated objects, only the number of attempted spawned objects, so this is
# the max it will be. This will only create copies of objects already in the
# scene, so if you request an object which is not in the scene upon reset, it
# will not work.
NUM_DUPLICATES_OF_TYPE = []  # not actually used

# A list of receptacle object types to exclude from valid receptacles that can
# be randomly chosen as a spawn location. An example use case is excluding all
# CounterTop receptacles to allow for a scene configuration that has more free
# space on CounterTops in case you need free space for interaction. Note that
# this will not guarantee all listed receptacles as being completely clear of
# objects, as any objects that failed to reposition will remain in their default
# position, which might have been on the excluded receptacle type. Check the
# Actionable Properties section of the Objects documentation for a full list of
# Receptacle objects.  **Note**: Receptacle objects allow other objects to be
# placed on or in them if the other object can physically fit the receptacle.
EXCLUDED_RECEPTACLES=[]   # not actually used


#-------------------------------------------------------------------------------
# What scenes are we using
LEVELS = {
    "kitchen": [i for i in range(1, 31)],
    "living_room": [i for i in range(1, 31)],
    "bedroom": [i for i in range(1, 31)],
    "bathroom": [i for i in range(1, 31)],
}


#-------------------------------------------------------------------------------
# Defines what objects the agent is able to interact with, and the corresponding
# actions to interact with those objects.
INTERACTION_PROPERTIES = [

    # can interact with pickupable objects
    ("pickupable",
     lambda obj: ["PickupObject"] if not obj["isPickedUp"] else ["DropObject"]),

    # can interact with openable objects
    ("openable",
     lambda obj: ["OpenObject"] if not obj["isOpen"] else ["CloseObject"])

]

# Interactions allowed; Note that you need to change thor_interact.js too.
INTERACTIONS = ["PickupObject",
                "DropObject",
                "OpenObject",
                "CloseObject"]

# Defines navigation actions, with parameters
MOVEMENT_PARAMS = {"MoveAhead"  :  {"moveMagnitude": MOVE_STEP_SIZE},
                   "LookUp"     :  {"degrees": V_ROTATION},
                   "LookDown"   :  {"degrees": V_ROTATION},
                   "RotateLeft" :  {"degrees": H_ROTATION},
                   "RotateRight":  {"degrees": H_ROTATION}}
MOVEMENTS = list(MOVEMENT_PARAMS.keys())


def get_acceptable_thor_actions():
    return MOVEMENTS + INTERACTIONS


#------------------------------------------------------------------------------
# Object types that can appear on scatter plot
OBJTYPES_ON_PLOT = {
    "AlarmClock",
    "AluminumFoil",
    # "Apple",
    "AppleSliced*",
    "ArmChair",
    "BaseballBat",
    "BasketBall",
    "Bathtub",
    "BathtubBasin",
    "Bed",
    "Blinds",
    "Book",
    "Boots",
    "Bottle",
    "Bowl",
    "Box",
    "Bread",
    "BreadSliced*",
    "ButterKnife",
    "Cabinet",
    "Candle",
    "CD",
    "CellPhone",
    "Chair",
    "Cloth",
    "CoffeeMachine",
    "CoffeeTable",
    "CounterTop",
    "CreditCard",
    "Cup",
    "Curtains",
    "Desk",
    "DeskLamp",
    "Desktop",
    "DiningTable",
    "DishSponge",
    "DogBed",
    "Drawer",
    "Dresser",
    "Dumbbell",
    "Egg",
    "EggCracked*",
    "Faucet",
    "FloorLamp",
    "Footstool",
    "Fork",
    "Fridge",
    "GarbageBag",
    "GarbageCan",
    "HandTowel",
    "HandTowelHolder",
    "HousePlant",
    "Kettle",
    "KeyChain",
    "Knife",
    "Ladle",
    "Laptop",
    "LaundryHamper",
    # "Lettuce",
    "LettuceSliced*",
    "LightSwitch",
    "Microwave",
    "Mirror",
    "Mug",
    "Newspaper",
    "Ottoman",
    "Painting",
    "Pan",
    "PaperTowelRoll",
    "Pen",
    "Pencil",
    "PepperShaker",
    "Pillow",
    "Plate",
    "Plunger",
    "Poster",
    "Pot",
    "Potato",
    "PotatoSliced*",
    "RemoteControl",
    "RoomDecor",
    "Safe",
    "SaltShaker",
    "ScrubBrush",
    "Shelf",
    "ShelvingUnit",
    "ShowerCurtain",
    "ShowerDoor",
    "ShowerGlass",
    "ShowerHead",
    "SideTable",
    "Sink",
    "SinkBasin",
    "SoapBar",
    "SoapBottle",
    "Sofa",
    "Spatula",
    "Spoon",
    "SprayBottle",
    "Statue",
    "Stool",
    "StoveBurner",
    "StoveKnob",
    "TableTopDecor",
    "TargetCircle",
    "TeddyBear",
    "Television",
    "TennisRacket",
    "TissueBox",
    "Toaster",
    "Toilet",
    "ToiletPaper",
    "ToiletPaperHanger",
    "Tomato",
    "TomatoSliced*",
    "Towel",
    "TowelHolder",
    "TVStand",
    "VacuumCleaner",
    "Vase",
    "Watch",
    "WateringCan",
    "Window",
    "WineBottle"
}

# These objects will be bolded on the scatter plot
LARGE_RECEPTABLES = {
    "Bathtub",
    "BathtubBasin",
    "Bed",
    "Cabinet",
    "CoffeeTable",
    "CounterTop",
    "Desk",
    "DiningTable",
    "Dresser",
    "Fridge",
    "Shelf",
    "SideTable",
    "SinkBasin",
    "Sofa",
    "Toilet",
    "TVStand"
}

SCATTER_GRANULARITY = GRID_SIZE*2


#------------------------------------------------------------------------------
# Logistics of data collection
TRAIN_TIME = 90  # 90 seconds to play around in the home
TEST_TIME = 180   # 180 seconds to search for the object
