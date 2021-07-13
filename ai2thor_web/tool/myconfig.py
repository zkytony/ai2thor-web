import dls.constants as constants

# File paths
DATA_PATH = "../sessions"  # the root for all data

# THOR configs
THOR_CONFIG = dict(

    # Please use these parameters throughout
    controller_config = dict(
        agentMode = constants.AGENT_MODE,
        width      = constants.IMAGE_WIDTH,
        height     = constants.IMAGE_WIDTH,
        visibilityDistance  = constants.VISIBILITY_DISTANCE,
        fov        = constants.FOV,
        gridSize  = constants.GRID_SIZE,
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
