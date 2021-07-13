# ai2thor-web

Ai2-THOR in browser.


## Setup

1. Clone the repository.


2. Download the following files from Google Drive:

   * [scenes.zip](https://drive.google.com/file/d/1WcIfUusWBfrGeDw-tVQqlcdnQiRKQyE4/view?usp=sharing)
   * [scene_scatter_plots.zip](https://drive.google.com/file/d/1d3PRWkqjH6YaBvw39MFWtmUB722-DYIQ/view?usp=sharing)

    Decompress them under `ai2thor-web/ai2thor_web`.


3. Install the package:

    ```
    # When you are in ai2thor-web repository,
    pip install -e .
    ```

    Resolve any dependency issue, if arise.

4. Run the app

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

5. Visit `http://127.0.0.1:5000/`.

6. For tool usage, refer to [this Google Doc](https://docs.google.com/document/d/1ic2vo6WtHM4kuFavjcvv94tg9oihaTD8ROWrxmO421s/edit?usp=sharing)
