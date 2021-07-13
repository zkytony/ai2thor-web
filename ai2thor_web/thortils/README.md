## Thor utility tools
This directory contains some code used in the correlational object search
project that may be useful for us here too.

The code here contains:
  * utility functions (like launching controller, getting agent pose) for thor

  * A function to convert the thor scene to a 2D grid map such that the poses
    in the thor scene can be mapped to the 2D grid map.

    The utility functions in `thor.py` contains conversion between thor coordinates and grid coordinates.

  * A script to plot the object distribution scatter plots

  * A script to save the scene information. This is useful if we pre-generated the scenes,
    and just want to access the scene information WITHOUT launching a controller which
    is very slow.


### How to


to plot the object distribution scatter plots
```
python process_scenes.py
# Do option 2 "plot_object_dist_ithor"
```

to save the scene information. This is useful if we pre-generated the scenes,
and just want to access the scene information WITHOUT launching a controller which
is very slow.
```
python process_scenes.py
# Do option 1 "process_ithor"
```


to convert an ai2thor scene to a (0,0)-indexed grid map:
```python
# Example in in test.py

from dls.thortils import *

floor_plan = "FloorPlan1"
scene_info = load_scene_info(floor_plan)
controller = launch_controller({"scene_name":floor_plan})
grid_map =convert_scene_to_grid_map(controller, scene_info, 0.25)

print(floor_plan)
for y in range(grid_map.length):
    row = []
    for x in range(grid_map.width):
        if (x,y) in grid_map.free_locations:
            row.append(".")
        else:
            assert (x,y) in grid_map.obstacles
            row.append("x")
    print("".join(row))

### Expected output
xxxxxxxxx......
x..............
x..............
x..............
x..xxxxx.x.....
x..xxxxxxxx....
x..xxxxxxxx....
x..xxxxxxx.....
x..xxxxx.......
x..xxxxxxxx....
x..xxxxxxxx....
x..xxxxxxxx....
x..xxxxx.x.....
x..............
x..............
...............
...............
xxxxx..xxxxxxxx
```
