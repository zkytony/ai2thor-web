# Copyright 2022 Kaiyu Zheng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Handles routes related to session
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, Response
from flask import session as browserSession
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time

from ..utils import nice_timestr
from .thor import *
from .models import db, Session, Admin, Guest, add_admin
from .myconfig import TRAIN_TIME, TEST_TIME

DEBUG_LEVEL = 1

sessmgr = Blueprint("sessmgr", __name__, template_folder="templates", static_folder="static")

### Keywords
class State:
    # guest
    ROLEINTRO = "roleintro"
    WAITING = "waiting"
    TRAINING_INTRO = "training-intro"
    TRAINING = "training"
    TESTING_INTRO = "testing-intro"
    TESTING = "testing"
    TESTING_FINISHED = "testing-finished"
    ALL_DONE = "all-done"
    # admin
    STATUS = "status"
    STARTED = "started"

class Event:
    SESSION_STARTED = "session_started"
    TRAINING_INTRO_FINISHED = "training_intro_finished"
    TRAINING_FINISHED = "training_finished"
    TESTING_INTRO_FINISHED = "testing_intro_finished"
    TESTING_FINISHED = "testing_finished"
    ALL_DONE = "all_done"

class MsgType:
    ERROR = "error"
    INFO = "info"


@sessmgr.route('/session', methods=["GET"])
def session_visit():
    """Responsible for handling visits to /session?id=<session_id> URLs.
    If session_id does not exist, redirect to the creation page;
    Otherwise, visit the session.
    """
    session_id = request.args.get("id")
    if session_id is None or len(session_id) <= 0:
        return redirect(url_for("landing"))

    else:
        session = Session.query.filter_by(id=int(session_id)).first()
        if session is None:
            return render_template("session_create.fhtml", session_id=session_id)
        else:
            # redirect to url for session id
            return redirect(url_for("sessmgr.session_core", id=session_id))


@sessmgr.route('/session/<id>/create', methods=["POST"])
def session_create(id):
    """Responsible for showing a form for creating a session,
    which requires admin credentials. """
    session_id = int(id)
    if Session.query.filter_by(id=session_id).first() is not None:
        return redirect(url_for("sessmgr.session_core", id=session_id))

    # Check admin credential
    username = request.form.get("username")
    password_entered = request.form.get("password")
    admin = Admin.query.filter_by(username=username).first()
    if admin is None\
       or not check_password_hash(admin.password, password_entered):
        flash("Incorrect Username/Password")
        return redirect(url_for("sessmgr.session_visit", id=session_id))

    target_object_types = request.form.get("target_objects").split(",")
    floor_plan = request.form.get("floor_plan")  # the scene name
    if not SCENE_DATASET.has_scene(floor_plan):
        flash("Scene name {} is not valid. Note: it's case sensitive".format(floor_plan))
        return redirect(url_for("sessmgr.session_visit", id=session_id))

    scene_info = SCENE_DATASET.scene_info(floor_plan)  # using default initial object poses.

    invalid_objtypes = get_invalid_targets(floor_plan, target_object_types)
    if len(invalid_objtypes) > 0:
        flash("Target object types {} are not valid<br><br>"\
              "Valid ones are {}".format(invalid_objtypes, scene_info.all_object_types()))
        return redirect(url_for("sessmgr.session_visit", id=session_id))

    create_time = datetime.now()
    session = Session(id=session_id,
                      create_time=datetime.now(),
                      start_time=None,
                      end_time=None,
                      controller=request.form.get("controller"),
                      assistant=request.form.get("assistant"),
                      monitor=request.form.get("monitor"),
                      floor_plan=request.form.get("floor_plan"),
                      target_objects=request.form.get("target_objects"))
    db.session.add(session)
    db.session.commit()
    return redirect(url_for("sessmgr.session_core", id=session_id))


@sessmgr.route('/session/<id>', methods=["GET"])
def session_core(id):
    """Responsible for the MAIN interactions within the session: i.e.
    the data collection process; If the session is not created,
    redirect to the session creation service; If the session is finished,
    display a summary."""
    session_id = int(str(id))  # make sure we have an int
    session = Session.query.filter_by(id=int(session_id)).first()
    if session is None:
        return render_template("session_create.fhtml", session_id=session_id)
    if session.finished:
        return render_template("session_summary.fhtml", session_id=session_id)
    else:
        # If the admin has logged in, then just direct to the admin page and skip this step.
        # this AVOIDS a "Method Not Allowed" issue I cannot reproduce!
        if "username" in browserSession:
            if session.start_time is not None:
                state = State.STARTED
            else:
                state = State.STATUS

            return redirect(url_for("sessmgr.session_admin",
                                    id=session_id, state=state))
        else:
            return render_template("session_greeting.fhtml", session=session)

@sessmgr.route('/session/<id>/admin/login', methods=["POST"])
def session_admin_login(id):
    session_id = int(str(id))  # make sure we have an int
    session = get_session(session_id)
    if session is None:
        return redirect_404()

    if "username" not in browserSession:
        username = request.form.get("username")
        password_entered = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin is None\
           or not check_password_hash(admin.password, password_entered):
            flash("Incorrect Username/Password")
            return redirect(url_for("sessmgr.session_core", id=session_id))
        browserSession["username"] = username

    # Logged in. Now redirect to temporary which changes method to GET
    return render_template("temporary.fhtml",
                           target=url_for("sessmgr.session_admin", id=session_id),
                           args=dict(state=State.STATUS),
                           method="get")


@sessmgr.route('/session/<id>/admin', methods=["GET"])
def session_admin(id):
    """Responsible for the admin views. The control flow is:

    1. Admin visits session status page, waits for two guests to join (state = status)
    2. Admin clicks begin (state = started)
    TODO: Revise/correct"""
    session_id = int(str(id))  # make sure we have an int
    session = get_session(session_id)
    if session is None:
        return redirect_404()

    if "username" not in browserSession:
        flash("You must log in first.")
        return redirect(url_for("sessmgr.session_core", id=session_id))

    state = request.args.get("state")
    if state is None:
        state = State.STATUS


    if state == State.STATUS:
        return render_template("session_admin.fhtml", session=session,
                               next_state=State.STARTED,
                               state=state)

    elif state == State.STARTED:
        prev_state = request.args.get("prev_state")
        if prev_state == State.STATUS:
            # The admin was previously viewing the session info. Then he submitted the form.
            if request.args.get("action") == "start":
                # If the admin just clicked Start, update start time, if it's not already set
                if session.start_time is None:
                    session.start_time = datetime.now()
                    db.session.commit()

        elif prev_state == State.STARTED:
            # Previously was in 'started' too.
            if request.args.get("action") == "end":
                # If the admin just clicked "End", update end time, if it's not already set
                if session.end_time is None:
                    session.end_time = datetime.now()
                    db.session.commit()

        return render_template("session_admin.fhtml", session=session,
                               next_state=State.STARTED,  # stay in "started" state
                               state=state)

    else:
        return redirect_400()



@sessmgr.route('/session/<id>/admin/stream', methods=["GET"])
def session_admin_stream(id):
    """Pushing events to the session_admin page to notify
    guest joining."""
    session_id = int(str(id))  # make sure we have an int
    session = get_session(session_id)
    if session is None:
        return redirect_404()

    stream_open = True
    while stream_open:
        controller_id = make_guest_id(session_id, "controller")
        assistant_id = make_guest_id(session_id, "assistant")
        guests_joined = []
        if Guest.query.filter_by(id=int(controller_id)).first() is not None:
            guests_joined.append("controller")
        if Guest.query.filter_by(id=int(assistant_id)).first() is not None:
            guests_joined.append("assistant")

        if len(guests_joined) > 0:
            message = "event: guest_join\ndata: {}\n\n".format(",".join(guests_joined))
            if len(guests_joined) == 2:
                stream_open = False
            return Response(message, mimetype="text/event-stream")
        time.sleep(1)




@sessmgr.route('/session/<id>/guest', methods=["GET"])
def session_guest(id):
    """Responsible for the guest views.  The control flow is:

    1. Guest visits roleintro page (state = roleintro)
    2. Guest waits for the other guest to agree (state = waiting)
    3. Guest enters training intro page, watch a video (state = training-intro)
    4. Guest done with intro, waits for the other guest to be done (state = waiting)
    5. Guest enters training page, waits for the other guest to enter (state = training)
    6. Guest completes training, waits the other guest to complete training (state = waiting)
    7. Guest enters testing page, waits for the other guest to enter (state = testing)
    8. Guest completes testing, waits for the other guest to go on to the next stage (stat = waiting)
    TODO: Revise/correct
    """
    session_id = int(str(id))  # make sure we have an int
    session = get_session(session_id)
    if session is None:
        return redirect_404()

    # Obtain guest role and guest id
    guest_role = request.args.get("guest_role")
    if guest_role is None:
        return redirect(url_for("sessmgr.session_core", id=session_id))
    guest_id = make_guest_id(session_id, guest_role)
    if guest_id is None:
        return redirect_400()
    guest = Guest.query.filter_by(id=int(guest_id)).first()
    if guest is not None and guest.role != guest_role:
        return redirect_400()   # something went wrong.

    # The guest can be in several states: "roleintro", "waiting",
    # "training-intro", "training", "testing-intro", "testing"
    state = request.args.get("state")
    if state is None:
        state = State.ROLEINTRO

    prev_state = request.args.get("prev_state")
    if state == State.ROLEINTRO\
       or (state == State.WAITING and prev_state == State.ROLEINTRO):
        return handle_roleintro_state(state, session, guest, guest_role)

    elif state == State.TRAINING_INTRO\
         or (state == State.WAITING and prev_state == State.TRAINING_INTRO):
        return handle_training_intro_state(state, session, guest)

    elif state == State.TRAINING\
         or (state == State.WAITING and prev_state == State.TRAINING):
        return handle_training_state(state, session, guest)

    elif state == State.TESTING_INTRO\
         or (state == State.WAITING and prev_state == State.TESTING_INTRO):
        round_num = request.args.get("round_num")
        return handle_testing_intro_state(state, session, guest, round_num)

    elif state == State.TESTING\
         or (state == State.WAITING and prev_state == State.TESTING):
        round_num = request.args.get("round_num")
        return handle_testing_state(state, session, guest, round_num)

    elif state == State.ALL_DONE:
        return handle_all_done_state(state, session, guest)

    else:
        return redirect_400()



@sessmgr.route('/session/<id>/guest/stream', methods=["GET"])
def session_guest_stream(id):
    """Push events to the session_guest page to notify e.g. waiting is over"""
    session_id = int(str(id))  # make sure we have an int
    session = get_session(session_id)
    if session is None:
        return redirect_404()
    controller_id = make_guest_id(session_id, "controller")
    assistant_id = make_guest_id(session_id, "assistant")

    stream_open = True
    while stream_open:
        # what's the event the client is waiting for?
        event_waiting = request.args.get("event_waiting")
        db.session.commit()  # in order to get updated model data

        if event_waiting == Event.SESSION_STARTED:
            # check if session has started
            session = Session.query.filter_by(id=int(session_id)).first()
            if session.start_time is not None:
                stream_open = False
                message = "event: {}\ndata: {}\n\n".format(Event.SESSION_STARTED, "Yes")
                return Response(message, mimetype="text/event-stream")

        else:
            controller = Guest.query.filter_by(id=controller_id).first()
            assistant = Guest.query.filter_by(id=assistant_id).first()

            if controller.event_waiting == assistant.event_waiting == event_waiting:
                # both controller and assistant are waiting for the same event.
                # that means they are in the same state and we can move forward
                stream_open = False
                message = "event: {}\ndata: {}\n\n".format(event_waiting, "Yes")
                return Response(message, mimetype="text/event-stream")

        time.sleep(1)


@sessmgr.route('/session/<id>/guest/thor-act', methods=['POST'])
def session_thor_act(id):
    """
    TODO: refactor
    This was used to handle Thor UI interaction AJAX requests.
    """
    start_time = time.time()
    session_id = int(str(id))  # make sure we have an int

    guest_role = request.form.get("guestRole")
    round_num = int(request.form.get("roundNum"))   # index of target object
    phase = request.form.get("phase")   # "train" or "test"
    js_timestamp_unix = int(request.form.get("timestamp"))
    # We use the UTC time, to be consistent.
    timestamp = datetime.utcfromtimestamp(js_timestamp_unix/1000.0)

    action = request.form.get("action")
    if action is None:
        return dict(msg="Action must be specified",
                    msg_type="error")

    # Process action; start processing it if no other action is pending.
    print_debug("ACTION {} RECEIVED".format(action))
    while action_is_pending(session_id, guest_role):
        print_debug("{} WAITING for {}".format(action, pending_action(session_id, guest_role)))
        time.sleep(0.1)
    add_action(session_id, guest_role, action)

    session = get_session(session_id)

    ## Starting up instance
    if action == "StartUp":
        if phase is None:
            return action_failed("Phase must be specified to start up Thor instance.",
                                 session_id, guest_role)

        # start controller only if it is not already started.
        if THOR_CONTROLLERS.get((session_id, guest_role)) is None:
            start_ai2thor(session, guest_role, stop_old=True)
            # We add or remove objects from the scene, depending on the phase
            remove_objects(session, guest_role, request.form["phase"], round_num)

        # log event, if it is test phase and if it's controller
        if phase == "test" and guest_role == "controller":
            log_step(session, guest_role, round_num, action, timestamp)

        # Return response; success
        return action_success("Thor action {} finished".format(action),
                              action, session_id, guest_role, round_num, with_controls=True)


    ## Object interaction
    elif action in ACCEPTABLE_THOR_ACTIONS:
        objectId = request.form.get("objectId")   # If None, then it's a movement.
        apply_action(session_id, guest_role, action, objectId=objectId)

        # log event, if it is test phase and if it's controller
        if phase == "test" and guest_role == "controller":
            log_step(session, guest_role, round_num, action, timestamp, objectId=objectId)

        # Return response; success
        return action_success("Thor action {} finished".format(action),
                              action, session_id, guest_role, round_num, with_controls=True)



    ## Stopping instance
    elif action == "StopInstance":
        thor_controller = THOR_CONTROLLERS.get((session_id, guest_role))
        if thor_controller is None:
            return action_failed("Cannot stop because instance is not started.",
                                 session_id, guest_role)

        # Get the found target object. Save this result.
        found_object = request.form.get("declaredTargetId")

        # log event, then save and destroy to free memory
        if phase == "test" and guest_role == "controller":
            log_step(session, guest_role, round_num, action, timestamp,
                     found_object=found_object)
            save_round_log(session, round_num)
            destroy_round_log(session, round_num)
            if at_last_round(session, round_num):
                compress_session_log(session)

        thor_controller.stop()
        THOR_CONTROLLERS[(session_id, guest_role)] = None

        return action_success("Stopped.", action, session_id, guest_role, round_num,
                              with_controls=False)

    ## Unrecognized
    else:
        return action_failed("Cannot interpret action {}".format(action),
                             session_id, guest_role)



@sessmgr.route("/404.fhtml", methods=["GET", "POST"])
def code_404():
    return render_template("404.fhtml"), 404

@sessmgr.route("/400.fhtml", methods=["GET", "POST"])
def code_400():
    return render_template("400.fhtml"), 400

def redirect_400():
    return redirect(url_for("sessmgr.code_400"))

def redirect_404():
    return redirect(url_for("sessmgr.code_404"))

def get_session(session_id):
    return Session.query.filter_by(id=int(session_id)).first()

def make_guest_id(session_id, guest_role):
    if guest_role not in {"controller", "assistant"}:
        return None
    role_code = "001" if guest_role == "controller" else "002"
    guest_id = int(str(session_id) + role_code)
    return guest_id


########################################
# State machine methods for guest view #
########################################
def handle_roleintro_state(state, session, guest, guest_role):
    """Going from ROLEINTRO to TRAINING_INTRO through a WAITING page for
    synchronization.

    Args:
        state (State): What state the client is in. Should be either ROLEINTRO or WAITING.
        session (Session): The current data collection session
        guest (Guest): The guest, The first time someone enters the ROLEINTRO state,
            they are not created so would be None."""
    if state not in {State.ROLEINTRO, State.WAITING}:
        raise ValueError("Unexpected to handle state {}".format(state))

    if state == State.ROLEINTRO:
        if guest is not None:
            # This guest has joined before (after session has started), but may
            # want to re-read the instructions. So we can skip waiting after
            # roleintro, and enter SESSION_STARTED
            next_state = State.TRAINING_INTRO
        else:
            # first time here; session has not started. So wait
            next_state = State.WAITING

        return render_template("session_guest_roleintro.fhtml",
                               action=url_for("sessmgr.session_guest", id=session.id),
                               guest_role=guest_role,
                               prev_state=state,
                               state=next_state)
    else:
        # state == WAITING; i.e. entering WAITING after
        # roleintro. Implicitly, the previous state is ROLEINTRO.
        assert state == State.WAITING
        first_time = request.args.get("newPlayer") == "new-yes"
        guest_id = make_guest_id(session.id, guest_role)
        now = datetime.now()
        if guest is None:
            # This guest has NOT been created. Create it
            guest = Guest(id=guest_id,
                          session_id=session.id,
                          role=guest_role,
                          name=getattr(session, guest_role),
                          create_time=now,
                          update_time=now,
                          event_waiting=Event.SESSION_STARTED)

            db.session.add(guest)
            db.session.commit()

        # Next, guest is waiting for the event of session starting; Once started, redirect
        # to this route again but with a new state of TRAINING_INTRO.
        return render_template("session_guest_waiting.fhtml",
                               session=session,
                               event_waiting=Event.SESSION_STARTED,
                               target=url_for("sessmgr.session_guest", id=session.id),
                               args=dict(prev_state=state,
                                         state=State.TRAINING_INTRO,
                                         guest_role=guest_role),
                               method="get")


def handle_training_intro_state(state, session, guest):
    if state not in {State.TRAINING_INTRO, State.WAITING}:
        raise ValueError("Unexpected to handle state {}".format(state))

    if state == State.TRAINING_INTRO:
        return render_template("session_training_intro.fhtml",
                               action=url_for("sessmgr.session_guest", id=session.id),
                               guest_role=guest.role,
                               prev_state=state,
                               state=State.WAITING)

    else:
        # Next, guest is waiting for the event that training intro is finished
        # for both participants; redirect to this route (i.e. session_guest)
        # again but with a new state of TRAINING.
        guest.event_waiting = Event.TRAINING_INTRO_FINISHED
        db.session.commit()
        return render_template("session_guest_waiting.fhtml",
                               session=session,
                               event_waiting=guest.event_waiting,
                               target=url_for("sessmgr.session_guest", id=session.id),
                               args=dict(prev_state=state,
                                         state=State.TRAINING,
                                         guest_role=guest.role),
                               method="get")


def handle_training_state(state, session, guest):
    if state not in {State.TRAINING, State.WAITING}:
        raise ValueError("Unexpected to handle state {}".format(state))

    if state == State.TRAINING:
        return render_template("session_training.fhtml",
                               action=url_for("sessmgr.session_guest", id=session.id),
                               guest_role=guest.role,
                               session=session,
                               round_num=0,
                               allowed_time=TRAIN_TIME,
                               prev_state=state,
                               state=State.WAITING)

    else:
        guest.event_waiting = Event.TRAINING_FINISHED
        db.session.commit()
        return render_template("session_guest_waiting.fhtml",
                               session=session,
                               event_waiting=guest.event_waiting,
                               target=url_for("sessmgr.session_guest", id=session.id),
                               args=dict(prev_state=state,
                                         state=State.TESTING_INTRO,
                                         guest_role=guest.role),
                               method="get")

def handle_testing_intro_state(state, session, guest, round_num):
    """
    Handles the TESTING_INTRO state in the guest's journey in our app.

    Args:
        state (State): state the guest is in
        session (Session): The Session that's going on
        guest (Guest): the guest that is visiting
        round_num (int): refers to a round of object search
            (i.e. index of in the list of target objects)
    """
    if state not in {State.TESTING_INTRO, State.WAITING}:
        raise ValueError("Unexpected to handle state {}".format(state))
    if round_num is None:
        round_num = 0

    if state == State.TESTING_INTRO:
        return render_template("session_testing_intro.fhtml",
                               action=url_for("sessmgr.session_guest", id=session.id),
                               guest_role=guest.role,
                               prev_state=state,
                               state=State.WAITING,
                               round_num=round_num)

    else:
        guest.event_waiting = Event.TESTING_INTRO_FINISHED
        db.session.commit()
        return render_template("session_guest_waiting.fhtml",
                               session=session,
                               event_waiting=guest.event_waiting,
                               target=url_for("sessmgr.session_guest", id=session.id),
                               args=dict(prev_state=state,
                                         state=State.TESTING,
                                         guest_role=guest.role,
                                         round_num=round_num),
                               method="get")

def handle_testing_state(state, session, guest, round_num):
    """TODO: Fix round_num"""
    if state not in {State.TESTING, State.WAITING}:
        raise ValueError("Unexpected to handle state {}".format(state))

    if round_num is None:
        round_num = 0
    round_num = int(round_num)

    if state == State.TESTING:
        return render_template("session_testing.fhtml",
                               action=url_for("sessmgr.session_guest", id=session.id),
                               scene_name=session.scene_name,
                               session=session,
                               guest_role=guest.role,
                               round_num=round_num,
                               allowed_time=TEST_TIME,
                               prev_state=state,
                               state=State.WAITING)

    else:
        # If current round_num points to the last target object, then wait for
        # the ALL_DONE event for both participants, with the new next state
        # ALL_DONE. Otherwise, the event to wait for is TESTING_FINISHED-{round_num],
        # with the new next state still TESTING, but with a bumped-by-1 round_num.
        scene_info = SCENE_DATASET.scene_info(session.scene_name)
        if at_last_round(session, round_num):
            # The guest has been to the last round; all target objects search done.
            guest.event_waiting = Event.ALL_DONE

            db.session.commit()
            return render_template("session_guest_waiting.fhtml",
                       session=session,
                       event_waiting=guest.event_waiting,
                       target=url_for("sessmgr.session_guest", id=session.id),
                       args=dict(prev_state=state,
                                 state=State.ALL_DONE,
                                 guest_role=guest.role),
                       method="get")


        else:
            # Because there are multiple rounds, we will make the guest wait for an
            # event specific to each round; done by simply appending the round_num.
            guest.event_waiting = "{}-{}".format(Event.TESTING_FINISHED, round_num)

            db.session.commit()
            return render_template("session_guest_waiting.fhtml",
                       session=session,
                       event_waiting=guest.event_waiting,
                       target=url_for("sessmgr.session_guest", id=session.id),
                       args=dict(prev_state=state,
                                 state=State.TESTING,
                                 guest_role=guest.role,
                                 round_num=round_num + 1),
                       method="get")



def handle_all_done_state(state, session, guest):
    if state not in {State.ALL_DONE}:
        raise ValueError("Unexpected to handle state {}".format(state))

    return render_template("session_testing_finished.fhtml",
                           session=session,
                           guest_role=guest.role)


##################################
# Utilities for session_thor_act #
##################################
def action_failed(msg, session_id, guest_role):
    """Returns a response (dict) with error message"""
    clear_action(session_id, guest_role)
    return dict(msg=msg,
                msg_type=MsgType.ERROR)

def action_success(msg, action, session_id, guest_role, round_num,
                   with_controls=True):
    """Returns a response (dict) with interaction, if specified"""
    response = dict(session_id=session_id,
                    round_num=round_num,
                    msg=msg, msg_type=MsgType.INFO)
    if with_controls:
        img_path, controls = show_interaction(session_id, guest_role)
        response.update(dict(img_path=img_path,
                             controls=controls))

    print_debug("ACTION {} DONE".format(action))

    clear_action(session_id, guest_role)
    return response

def at_last_round(session, round_num):
    target_object_types = session.target_object_types()
    return round_num == len(target_object_types) - 1


##################
# Utilities misc #
##################
def print_debug(msg, level=0):
    if DEBUG_LEVEL > level:
        print(msg)
