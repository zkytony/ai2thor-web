from flask import url_for
import cv2
import os, sys
import time
import re
import pickle
import tarfile
import shutil
from datetime import timezone, datetime, timedelta

from thortils import (launch_controller, get_object_interactions,
                      get_object_bboxes2D)
from thortils.interactions import *
from thortils.scene import SceneDataset, ThorSceneInfo
from .myconfig import (THOR_CONFIG,
                       INTERACTION_DISTANCE,
                       INTERACTION_PROPERTIES,
                       MOVEMENTS, MOVEMENT_PARAMS,
                       TRAIN_TIME, TEST_TIME,
                       get_acceptable_thor_actions,
                       SESSION_DATA_PATH, SCENES_DATA_PATH)


# Maps from (session id, guest_role) to ai2thor controller.
# At any time, there should only be one ai2thor instance per (session, role) pair running.
THOR_CONTROLLERS = {}
ACCEPTABLE_THOR_ACTIONS = set(get_acceptable_thor_actions())

sys.stdout.write("Loading scene dataset...")
SCENE_DATASET = SceneDataset.load(SCENES_DATA_PATH)
sys.stdout.write("Done.\n")
sys.stdout.flush()

# Stores data; maps from session_id to round_num to list of events and timestamp
SESSION_DATA = {}

# Maps from (session id, guest_role) to an action (sent to session_thor_act) currently being processed
THOR_ACTIONS_PENDING = {}

def start_ai2thor(session, guest_role, stop_old=True):
    """Loads a controller"""
    if session.id in THOR_CONTROLLERS:
        if stop_old:
            THOR_CONTROLLERS[(session.id, guest_role)].stop()
        else:
            # If there is already a thor_controller and we don't stop it then just
            # keep using it
            return

    config = dict(THOR_CONFIG['controller_config'])
    config["scene"] = session.scene_name
    thor_controller = launch_controller(config)
    THOR_CONTROLLERS[(session.id, guest_role)] = thor_controller

def thor_img_dirpath(session_id):
    """Returns the directory where images related to current session will be
    generated, relative to the 'static' directory.
    """
    img_dirpath = os.path.join(THOR_CONFIG['img_dir'], "session_{}".format(session_id))
    return img_dirpath

def show_interaction(session_id, guest_role):
    """Save the current image from the FOV; return the URL path to the image,
    as well as controls possible for this current state"""
    # Save an image; return controls possible for this current state
    img_dirpath = thor_img_dirpath(session_id)
    img_full_dirpath = os.path.join("static", img_dirpath)
    img_filename = "{}?{:.0f}".format(THOR_CONFIG['cur_img_file'], time.time())
    os.makedirs(img_full_dirpath, exist_ok=True)

    event = apply_action(session_id, guest_role, "Pass")
    img = event.cv2img
    cv2.imwrite(os.path.join(img_full_dirpath, img_filename), img)
    return url_for("static", filename=os.path.join(img_dirpath, img_filename)),\
                   get_controls(session_id, guest_role)

def apply_action(session_id, guest_role, action, objectId=None, **kwargs):
    """Take action in the controller"""
    if objectId is not None:
        # This is an object interaction action
        assert not action.startswith("Move")
        return eval(action)(THOR_CONTROLLERS[(session_id, guest_role)], objectId, **kwargs)
    else:
        if action in MOVEMENT_PARAMS:
            return THOR_CONTROLLERS[(session_id, guest_role)].step(action, **MOVEMENT_PARAMS[action])
        else:
            return THOR_CONTROLLERS[(session_id, guest_role)].step(action)


def get_controls(session_id, guest_role, movements=MOVEMENTS):
    # Returns controls that are possible for the current state.
    event = THOR_CONTROLLERS[(session_id, guest_role)].step(action="Pass")
    objects, interactions = get_object_interactions(THOR_CONTROLLERS[(session_id, guest_role)],
                                                    properties=INTERACTION_PROPERTIES,
                                                    interaction_distance=INTERACTION_DISTANCE)
    bboxes2D = get_object_bboxes2D(event, objects=objects, center_only=False)
    return {"movements": movements,
            "interactions": interactions,
            "bboxes2D": bboxes2D}


def get_current_scene(session_id, guest_role):
    """get scene name from controller running"""
    scene_name = THOR_CONTROLLERS[(session_id, guest_role)].scene
    # The returned scene is actually something like FloorPlan1_physics, so need
    # to match pattern.
    match = re.match(r"^FloorPlan[0-9]+$", scene)  # exactly the same way
                                                   # Ai2thor matches scene name
    if match:
        return match.group()
    else:
        raise ValueError("Unable to get scene name for ({}, {})"\
                         .format(session_id, guest_role))


def get_invalid_targets(scene_name, target_objects):
    """
    Args:
        scene_name (str): FloorPlanXX-<random_seed(int) | default>
        target_objects (list): List of object types
    """
    scene_info = SCENE_DATASET.scene_info(scene_name)
    invalid = []
    for objtype in target_objects:
        if not scene_info.has_object_type(objtype.strip()):
            invalid.append(objtype)
    return invalid


def remove_objects(session, guest_role, phase, round_num):
    """
    Removes the appropriate objects, depends on the phase and round
    Args:
        session (Session): the session object
        phase (str): "train" or "test"
        round_num (int): refers to a round of object search
            (i.e. index of in the list of target objects)
    """
    scene_info = SCENE_DATASET.scene_info(session.scene_name)
    controller = THOR_CONTROLLERS.get((session.id, guest_role))
    if phase == "train":
        # Remove all target objects during training
        for objtype in session.target_object_types():
            for objid in scene_info.objects_of_type(objtype):
                RemoveFromScene(controller, objid)

    else:
        # Remove all objects starting round_num+1
        types_to_remove = session.target_object_types()[round_num+1:]
        for objtype in types_to_remove:
            for objid in scene_info.objects_of_type(objtype):
                RemoveFromScene(controller, objid)


def log_step(session, guest_role, round_num, action, timestamp, **kwargs):
    """
    Adds the following object to the list
    SESSION_DATA[session_id][${round_num}_${target object}]
    {
        "timestamp": timestamp,
        "action": action
        "event": event object after action execution (basically stores environment state),
        **kwargs  # anything else
    }

    Note that the passed in timestamp is the Unix Epoch time.
    """
    if session.id not in SESSION_DATA:
        SESSION_DATA[session.id] = {}

    target_key = "{}_{}".format(round_num, session.target_object(round_num))
    if target_key not in SESSION_DATA[session.id]:
        SESSION_DATA[session.id][target_key] = []

    controller = THOR_CONTROLLERS.get((session.id, guest_role))
    event = controller.step(action="Pass")
    SESSION_DATA[session.id][target_key].append({"timestamp": timestamp,
                                                 "action": action,
                                                 "event": event,
                                                 **kwargs})

def destroy_session_log(session_id):
    SESSION_DATA.pop(session_id, None)


def destroy_round_log(session, round_num):
    target_key = "{}_{}".format(round_num, session.target_object(round_num))
    SESSION_DATA[session.id].pop(target_key, None)

def get_session_start_timestr(session):
    start_timestr = session.start_time.astimezone(timezone.utc)\
                                      .strftime("%Y-%m-%d-%H-%M-%S") + "-UTC"
    return start_timestr

def save_round_log(session, round_num, rootdir=SESSION_DATA_PATH):
    """
    Saves round log in an organized way; the root of the dataset
    directory is `rootdir`.
    """
    # get the UTC start time
    start_timestr = get_session_start_timestr(session)
    session_path = os.path.join(rootdir, "Session_{}_{}".format(session.id, start_timestr))
    os.makedirs(session_path, exist_ok=True)
    target_key = "{}_{}".format(round_num, session.target_object(round_num))
    log_file_path = os.path.join(session_path, "{}-log.pkl".format(target_key))
    with open(log_file_path, "wb") as f:
        log = SESSION_DATA[session.id][target_key]
        pickle.dump(log, f)

    # Compress the log file
    compressed_file_path = os.path.join(session_path, "{}-log.pkl.tar.gz".format(target_key))
    print("Compressing log file. Output path: {}".format(compressed_file_path))
    with tarfile.open(compressed_file_path, "w:gz") as tar:
        tar.add(log_file_path, arcname="{}-log.pkl".format(target_key))

    # Remove temporary log file
    os.remove(log_file_path)

def compress_session_log(session, rootdir=SESSION_DATA_PATH):
    """
    Compresses the Session_{session_id}_{start_time} directory
    and removes the folder, to save space.
    """
    # get the UTC start time
    start_timestr = get_session_start_timestr(session)
    session_str = "Session_{}_{}".format(session.id, start_timestr)
    session_path = os.path.join(rootdir, session_str)

    # compress the folder
    compressed_file_path = os.path.join(session_path + ".tar.gz")
    print("Compressing session log. Output path: {}".format(compressed_file_path))
    with tarfile.open(compressed_file_path, "w:gz") as tar:
        tar.add(session_path, arcname=session_str)

    # Remove the session directory
    shutil.rmtree(session_path)


# These functions are used to deal with concurrent requests
def action_is_pending(session_id, guest_role):
    return pending_action(session_id, guest_role) is not None

def pending_action(session_id, guest_role):
    return THOR_ACTIONS_PENDING.get((session_id, guest_role))

def add_action(session_id, guest_role, action):
    THOR_ACTIONS_PENDING[(session_id, guest_role)] = action

def clear_action(session_id, guest_role):
    THOR_ACTIONS_PENDING[(session_id, guest_role)] = None
