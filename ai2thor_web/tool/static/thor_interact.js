// This is the script for the Ai2Thor interaction area in the webpage.

// Stores the currently allowed object interactions
var objectInteractions = {};  // maps from object id to {bbox, interactions}

var handledInteractions = new Set(["OpenObject", "CloseObject",
                                   "PickupObject", "DropObject"])
var interactionSynonyms = {"OpenObject": "Open",
                           "CloseObject": "Close",
                           "PickupObject": "Pickup",
                           "DropObject": "Drop"}

function thorActParams(action) {
    return { action: action,
             guestRole: guestRole,  // global variable
             timestamp: getTimeNowUnix(),
             phase: phase, // global variable
             roundNum: roundNum } // global variable
}

$(document).ready(function() {

    // Note that because the buttons are added as a result of ajax,
    // need to bind the event callback to the parent element of the
    // buttons
    $("#thor-interactions").on("click", ".movement-btn", function() {
        $.ajax({
            method: "POST",
            url: queryURL, // Assumed to be set (global variable)
            data: thorActParams($(this).val()),
            dataType: "json", // what response data type to expect
            beforeSend: function() {
                $(".movement-btn").prop("disabled", true);
            }
        })
         .done(function(response) {
             // The response is automatically a json object
             // prevent browser caching
             $(".movement-btn").prop("disabled", false);
             refreshThorInterface(response);
         });
    });

});

// Sends ajax request to server to get initial screen
function loadAi2ThorInstance(onLoadCb) {
    $.ajax({
        method: "POST",
        url: queryURL, // Assumed to be set //"/thor/act",
        data: thorActParams("StartUp"),
        // train or test phase
        dataType: "json",
        beforeSend: function() {
            showAlert("<b>Starting Ai2Thor instance. Waiting for Response...</b>");
        }
    })
     .done(function(response) {
         console.log(response)
         clearAlert();

         let movements = response["controls"]["movements"];
         movements.forEach(function(m) {
             console.log(m);
             addMovementBtn($("#thor-interactions .btn-group"), m);
         });

         refreshThorInterface(response);

         // display time when loading finished
         $("#time").html(getTimeStringNow());
         $("#time").addClass("yellow-box");

         if (onLoadCb !== undefined) {
             onLoadCb(response);
         }
     });
}

// This function should be called every time an ajax call
// that involves (1) loading the page; (2) performing action
// is returend to refresh the interfact.
function refreshThorInterface(response) {
    // Refresh objectInteractions every time we get a response
    if (response["msg_type"] == "error") {
        showAlert(`<b>${response["msg"]}</b>`);
        return
    }

    // If there is a timestamp in the response, add that too.
    if ("timestr" in response) {
        $("#server-time").html(response["timestr"]);
    }

    objectInteractions = {};
    boxCache = {};
    let bboxes2D = response["controls"]["bboxes2D"];
    let interactions = response["controls"]["interactions"];
    for (var objectId of Object.keys(bboxes2D)) {
        let bbox = bboxes2D[objectId];
        objectInteractions[objectId] = {"bbox": bbox,
                                        "interactions": null};
    }
    for (var objectId of Object.keys(interactions)) {
        if (! (objectId in objectInteractions) ) {
            objectInteractions[objectId] = {"bbox": null,
                                            "interactions": null};
        }
        objectInteractions[objectId]["interactions"] = interactions[objectId];
    }

    // setting the image and canvas
    $("#thor-img").attr("src", response["img_path"]).on("load", function() {
        $("#thor-canvas").attr("width", $(this).width());
        $("#thor-canvas").attr("height", $(this).height());
    });
}


function addMovementBtn(parent, movement) {
    let htmlStr =
        `<button name="movement"`
        + `class="movement-btn btn btn-secondary"`
        + `value=${movement}>${movement}</button>`;
    parent.append(htmlStr)
}


// ajax request to stop ai2thor instance, along with the declared found object id
function stopThorInstance(onStopCb, declaredTargetId) {
    let reqData = thorActParams("StopInstance");
    reqData["declaredTargetId"] = declaredTargetId

    $.ajax({
        method: "POST",
        url: queryURL,
        data: reqData,
        dataType: "json"
    })
     .done(function(response) {
         if (onStopCb !== undefined) {
             onStopCb(response);
         }
     });
}

function getTimeStringNow() {
    const now = new Date();
    const hr = now.getHours();
    const min = now.getMinutes();
    const sec = now.getSeconds();
    const ms = now.getMilliseconds();
    const day = now.getDate();  // month's day
    const weekday = now.getDay(); // week's day
    const month = now.getMonth() + 1;  // getMonth startswith 0
    const year = now.getFullYear();

    const timeZone = now.toString().match(/[A-Z]+-[0-9]+/).pop();
    const timeZoneNickName = now.toString().match(/\((.*)\)/).pop();

    return `${year}/${month}/${day}, ${hr}:${min}:${sec}:${ms}, ${timeZone}, ${timeZoneNickName}`
}

function getTimeNowUnix() {
    return new Date().getTime();
}



//////// Canvas related
var canvas = document.getElementById("thor-canvas");
var ctx = canvas.getContext("2d");  // drawing context on the canvas
$(document).ready(function() {

    // Interact with object
    canvas.addEventListener("mousedown", interactWithObject);

    canvas.addEventListener("mousemove", focusOnObject);
});

// function called when mouse clicks on the canvas
function interactWithObject(event) {
    let [canvas_x, canvas_y] = getThorImgCoord(event);
    console.log(`${canvas_x}, ${canvas_y}`);

    let interactingObjects = getInteractingObjectsAt([canvas_x, canvas_y]);
    let focusedObjectId = getObjectIdWithSmallestBbox(interactingObjects);
    if (focusedObjectId != null) {
        let interaction = objectInteractions[focusedObjectId]["interactions"][0]

        // ask ai2thor to perform the action
        let interactData = thorActParams(interaction);
        interactData["objectId"] = focusedObjectId;
        $.ajax({
            method: "POST",
            url: queryURL, // Assumed to be set (global variable)
            data: interactData,
            beforeSend: function() {
                $(".movement-btn").prop("disabled", true);
            }
        })
         .done(function(response) {
             // The response is automatically a json object
             // prevent browser caching
             $(".movement-btn").prop("disabled", false);
             refreshThorInterface(response);
         });
    }
}

// function called when moving across the canvas
function focusOnObject(event) {
    // First clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // check if the canvas event coordinate falls within
    // any object bounding box
    let [canvas_x, canvas_y] = getThorImgCoord(event);
    let interactingObjects = getInteractingObjectsAt([canvas_x, canvas_y]);
    if (interactingObjects.length > 0) {
        drawFocusInteraction(interactingObjects);
        /* console.log(`${canvas_x}, ${canvas_y}`);
         * console.log(interactions); */
    }
}

// given event that contains mouse coordinates w.r.t. browser,
// return coordinates relative to the thor image itself,
// that is, (0,0) will be the top-left pixel of the thor image.
function getThorImgCoord(event) {
    let offset = $("#thor-canvas").offset();
    let canvas_x = event.pageX - offset['left'];
    let canvas_y = event.pageY - offset['top'];
    return [canvas_x, canvas_y];
}

// Returns True if point is within bounding box `bbox`,
// which is [topleft_x, topleft_y, bottomright_x, bottomright_y]
var boxCache = {};  // maps from "big pixel" to object or null
var granularity = 10;  // number of pixels per side length of "big pixel" in each entry in the cache

function getInteractingObjectsAt(point) {
    let big_point = [Math.round(point[0] / granularity),
                     Math.round(point[1] / granularity)];
    if (big_point in boxCache) {
        return boxCache[big_point];
    }

    let objectsAtPoint = [];
    for (var objectId of Object.keys(objectInteractions)) {
        let bbox = objectInteractions[objectId]["bbox"];
        if (bbox != null) {
            if (withinBbox(bbox, point)) {
                objectsAtPoint.push(objectId);
            }
        }
    }
    boxCache[big_point] = objectsAtPoint;
    return objectsAtPoint;
}

function withinBbox(bbox, point) {
    let [topleft_x, topleft_y, bottomright_x, bottomright_y] = bbox;
    if ((point[0] >= topleft_x && point[0] < bottomright_x)
        && (point[1] >= topleft_y && point[1] < bottomright_y)) {
        return true;
    } else {
        return false;
    }
}

function getBboxDims(bbox) {
    let [topleft_x, topleft_y, bottomright_x, bottomright_y] = bbox;
    let width = bottomright_x - topleft_x;
    let height = bottomright_y - topleft_y;
    return [width, height];
}

function drawBbox(bbox) {
    let [topleft_x, topleft_y, bottomright_x, bottomright_y] = bbox;
    let [width, height] = getBboxDims(bbox);
    ctx.rect(topleft_x, topleft_y, width, height);
}

// Given a list of objects, returns the one with the smallest boudning box.
function getObjectIdWithSmallestBbox(objects) {
    let smallestObjectId = null;
    let smallestBboxArea = Infinity;
    objects.forEach(function(objectId) {
        let bbox = objectInteractions[objectId]["bbox"];
        if (objectInteractions[objectId]["interactions"].length > 0) {
            let [width, height] = getBboxDims(bbox);
            if (width * height < smallestBboxArea) {
                smallestObjectId = objectId;
                smallestBboxArea = width * height;
            }
        }
    });
    return smallestObjectId;
}

// Draws interaction (i.e. boundingbox, with textlabel)
function drawFocusInteraction(interactingObjects) {
    // Given multiple interacting objects based on mouse pixel,
    // Only one interaction candidate will be drawn -- the one with smallest
    // bounding box.
    var focusedObjectId = getObjectIdWithSmallestBbox(interactingObjects);
    if (focusedObjectId == null) {
        return;
    }

    // Draw bounding box
    let bbox = objectInteractions[focusedObjectId]["bbox"];
    ctx.lineWidth = 3.0;
    ctx.strokeStyle = "#007BFF";
    ctx.beginPath();
    drawBbox(bbox);
    ctx.stroke();

    // Draw text label for interaction
    let interactions = objectInteractions[focusedObjectId]["interactions"];
    let [topleft_x, topleft_y, bottomright_x, bottomright_y] = bbox;
    let [width, height] = getBboxDims(bbox);
    interactions.forEach(function(actionName, index) {
        if (handledInteractions.has(actionName)) {
            ctx.font = "18px Arial";
            let verb = interactionSynonyms[actionName];
            let objclass = focusedObjectId.split("|")[0];
            ctx.fillStyle = "#f5e642";
            ctx.fillText(`${verb} ${objclass}`, topleft_x - 10, topleft_y - 10 - 20*index);
        }
    });
}

function showAlert(msg) {
    $("alert").removeClass("d-none");
    $("#alert").html(msg);
}

function clearAlert() {
    $("alert").addClass("d-none");
    $("#alert").html("");
}
