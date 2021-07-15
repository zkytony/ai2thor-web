# Configuration specific to the app
import thortils.constants as constants

#-------------------------------------------------------------------------------
# objects farther away than this cannot be interacted with.
INTERACTION_DISTANCE = 1.5

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
MOVEMENT_PARAMS = {"MoveAhead"  :  {"moveMagnitude": constants.MOVE_STEP_SIZE},
                   "LookUp"     :  {"degrees": constants.V_ROTATION},
                   "LookDown"   :  {"degrees": constants.V_ROTATION},
                   "RotateLeft" :  {"degrees": constants.H_ROTATION},
                   "RotateRight":  {"degrees": constants.H_ROTATION}}
MOVEMENTS = list(MOVEMENT_PARAMS.keys())


def get_acceptable_thor_actions():
    return MOVEMENTS + INTERACTIONS

#------------------------------------------------------------------------------
# Logistics of data collection
TRAIN_TIME = 90  # 90 seconds to play around in the home
TEST_TIME = 180   # 180 seconds to search for the object

# File paths
SESSION_DATA_PATH = "../sessions"  # the root for all data collected from the sessions.
SCENES_DATA_PATH = "../../../thortils/scenes"

# THOR configs
THOR_CONFIG = dict(

    # Please use these parameters throughout
    controller_config = dict(
        agentMode  = constants.AGENT_MODE,
        width      = constants.IMAGE_WIDTH,
        height     = constants.IMAGE_WIDTH,
        visibilityDistance  = constants.VISIBILITY_DISTANCE,
        fov        = constants.FOV,
        gridSize   = constants.GRID_SIZE,
        renderDepth  = True,
        renderClass  = True,
        renderObject = True,
        continuous = constants.CONTINUOUS,
        snapToGrid = constants.SNAP_TO_GRID
    ),

    img_dir = "tmp/",  # Should not include 'static' because it'll go there by convention.
    cur_img_file = "current.png"
)

#-------------------------
# site setttings
ADMIN_ID=100
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="password"
SECRET_KEY="secret-dls"
DB_URI = 'sqlite:///../tmp-db.db'
