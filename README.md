# ai2thor-web

Ai2-THOR in browser. This is a useful tool if you would like to build a user study or data collection platform that let **remote, non-technical** people participate in the control of an embodied agent in Ai2-THOR over a Zoom call. Pairs of participants can be assigned two different roles to perform a session of some task (by default, object search) in Ai2-THOR, and a staff (from the research team)
can adminstor the progress of the session.

The idea of this system is illustrated by the figure below:

![image](https://user-images.githubusercontent.com/7720184/167217337-3a9ac76e-88af-49fe-912c-a2c7f6f2937b.png)


## Setup

1. Clone the repository.

2. Clone and install [thortils](https://github.com/zkytony/thortils)

   ```
   git clone https://github.com/zkytony/thortils
   cd thortils
   git checkout v3.3.4  # Switch to the branch with the correct ai2thor version.
   ```
   Then, follow the [instruction steps on README](https://github.com/zkytony/thortils/tree/v3.3.4).


3. Download (you may have already done this for the last step) [scene_scatter_plots.zip](https://drive.google.com/file/d/1d3PRWkqjH6YaBvw39MFWtmUB722-DYIQ/view?usp=sharing). This contains sparse scatter plots. If you would like complete scatter plots, download [scene_scatter_plots_full.zip](https://drive.google.com/file/d/1PrKVLENWZKUDgl9ErTcid2wzvgeCUIzg/view?usp=sharing)

   Decompress this file under `ai2thor-web/ai2thor_web/tool/static/image`


4. Install the package:

    ```
    # When you are in ai2thor-web repository,
    pip install -e .
    ```

    Resolve any dependency issue, if arise.
    
5. Change configuration in [myconfig.py](https://github.com/zkytony/ai2thor-web/blob/master/ai2thor_web/tool/myconfig.py).
   In particular:
   ```python
   SCENES_DATA_PATH = "../../../thortils/scenes"   # set this to the correct path to the scenes dataset
   DB_URI = 'sqlite:///../tmp-db.db'   # set this to the desired path where you want to store the flask server data.
   ```
   

6. Run the app

    ```
    cd ai2thor-web/ai2thor_web/tool
    ./run.sh
    ```

   Example output:
   ```
   $ ./run.sh
    * Serving Flask app "app.py" (lazy loading)
    * Environment: development
    * Debug mode: on
   INFO:werkzeug: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   INFO:werkzeug: * Restarting with stat
   /home/kaiyuzh/pyenv/py37/lib/python3.7/site-packages/flask_sqlalchemy/__init__.py:873: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
     'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
   WARNING:werkzeug: * Debugger is active!
   INFO:werkzeug: * Debugger PIN: 330-526-617
   /home/kaiyuzh/pyenv/py37/lib/python3.7/site-packages/flask_sqlalchemy/__init__.py:873: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
     'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
   ```

7. Visit `http://127.0.0.1:5000/`.

8. For tool usage, refer to [this Google Doc](https://docs.google.com/document/d/1ic2vo6WtHM4kuFavjcvv94tg9oihaTD8ROWrxmO421s/edit?usp=sharing)

## Citation
Please cite [_Dialogue Object Search_](https://arxiv.org/pdf/2107.10653.pdf), presented at
Robotics: Science and Systems (RSS) Workshop on Robotics for People (R4P): Perspectives on Interaction, Learning and Safety, 2021
```
@inproceedings{dlgobjsearch-2021,
  title = {{D}ialogue {O}bject {S}earch},
  author = {Roy, Monica and Zheng, Kaiyu and Liu and Jason and Stefanie Tellex},
  booktitle = {RSS Workshop on Robotics for People (R4P): Perspectives on Interaction, Learning and Safety},
  year = {2021},
  url = {https://arxiv.org/pdf/2107.10653.pdf},
  note = {Extended Abstract}
}
```


## Contact
Kaiyu Zheng (kaiyu_zheng@brown.edu)
