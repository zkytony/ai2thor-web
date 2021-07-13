// Scripts for the session_testing.fhtml template
var targetObjectId = undefined;

$(document).ready(function() {

    // When clicking the 'i found it' button, stop the timer,
    // Ajax the server to inform this.
    $(document).on("click", "#found-btn", function() {
        clearInterval(countDown);  // global variable
        $(this).prop("disabled", true);

        // give an instruction
        $("#count-down").addClass("d-none");
        $("#after-count-down-complete").removeClass("d-none")
                                       .html("Please click on the target object");

        // disable movement buttons
        $(".movement-btn").prop("disabled", false);

        // disable interact with object event that sends action to server,
        // then add a few other listeners
        canvas.removeEventListener("mousedown", interactWithObject);
        canvas.removeEventListener("mousemove", focusOnObject);
        canvas.addEventListener("mousemove", focusOnTarget);
        canvas.addEventListener("mousedown", selectTarget);
    });

});

function focusOnTarget(event) {
    // First clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // check if the canvas event coordinate falls within
    // any object bounding box
    let bbox = undefined
    if (targetObjectId == undefined) {
        let [canvas_x, canvas_y] = getThorImgCoord(event);
        let interactingObjects = getInteractingObjectsAt([canvas_x, canvas_y]);
        if (interactingObjects.length > 0) {
            var focusedObjectId = getObjectIdWithSmallestBbox(interactingObjects);
            if (focusedObjectId == null) {
                return;
            }

            // Draw bounding box
            bbox = objectInteractions[focusedObjectId]["bbox"];
        } else {
            return;
        }

    } else {
        bbox = objectInteractions[targetObjectId]["bbox"];
    }

    // draw bounding box
    ctx.lineWidth = 3.0;
    ctx.strokeStyle = "#2dd100";
    ctx.beginPath();
    drawBbox(bbox);
    ctx.stroke();
}


function selectTarget(event) {
    if (targetObjectId != undefined) {
        return;  // target already chosen
    }

    let [canvas_x, canvas_y] = getThorImgCoord(event);
    console.log(`${canvas_x}, ${canvas_y}`);

    let interactingObjects = getInteractingObjectsAt([canvas_x, canvas_y]);
    let focusedObjectId = getObjectIdWithSmallestBbox(interactingObjects);
    if (focusedObjectId != null) {
        targetObjectId = focusedObjectId;

        // now, ajax
        $("#after-count-down-complete").html("Submitting target object...");
        stopThorInstance(function(){
            // when stopped, put up the overlay
            $("#thor-area .overlay").css("display", "block");
            $("#next-form button[type='submit']").prop("disabled", false);
            $("#after-count-down-complete").html("Target object submitted. Click <b>Next</b>.");
        }, targetObjectId);
    }
}
