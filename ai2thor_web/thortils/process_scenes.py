"""
Process every scene. Assigns an integer to every object
in the scene.
"""
import os
import pickle
import yaml
import numpy as np
import matplotlib.pyplot as plt
from .thor import robothor_scene_names,\
    ithor_scene_names, ThorSceneInfo

def shared_objects_in_scenes(scenes):
    objects = None
    for scene in scenes:
        scene_info = load_scene_info(scene)
        if objects is None:
            objects = scene_info.obj_types()
        else:
            objects = objects.intersection(scene_info.obj_types())
    return objects

def plot_object_dist(scenes):
    fig, ax = plt.subplots(figsize=(15,12))
    dirpath = os.path.join("data", "plots")
    os.makedirs(dirpath, exist_ok=True)
    for scene in scenes:
        print(scene)
        scene_info = ThorSceneInfo.load(scene)
        x = []
        z = []
        t = []
        for objid in scene_info.objects:
            thor_x, thor_z = scene_info.thor_obj_pose2d(objid)
            x.append(thor_x)
            z.append(thor_z)
            t.append(scene_info.obj_type(objid))
        ax.scatter(x, z)
        for i, label in enumerate(t):
            ax.annotate(label, (x[i], z[i]))
        ax.set_title(scene)
        plt.savefig(os.path.join(dirpath, "{}-objects.png".format(scene)))
        ax.clear()

def main(do_what):
    os.makedirs("data", exist_ok=True)

    if do_what == "process_robothor":
        scenes = robothor_scene_names("Train")
    elif do_what == "process_ithor":
        for scene_type in ["kitchen", "living_room", "bedroom", "bathroom"]:
            print(scene_type)
            for scene in ithor_scene_names(scene_type):
                print(scene)
                mapping = ThorSceneInfo.extract_objects_info(scene)
                with open(os.path.join("data", "{}-objects.pkl".format(scene)), "wb") as f:
                    pickle.dump(mapping, f)
    elif do_what == "plot_object_dist_ithor":
        plot_object_dist(ithor_scene_names("kitchen"))
        plot_object_dist(ithor_scene_names("living_room"))
        plot_object_dist(ithor_scene_names("bedroom"))
        plot_object_dist(ithor_scene_names("bathroom"))
    else:
        print("Unknown command: ", do_what)

if __name__ == "__main__":
    OPTIONS = {
        0: "process_robothor",
        1: "process_ithor",
        2: "plot_object_dist_ithor"
    }
    for num, txt in sorted(OPTIONS.items()):
        print(num, ":", txt)
    main(OPTIONS[int(input("option: "))])
