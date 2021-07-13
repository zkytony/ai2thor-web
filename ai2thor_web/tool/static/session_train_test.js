// Mainly for the count down clock.

// Set countdown of `timeLimit` seconds.
function setCountDown(timeLimit, callback) {
    var [minutes, seconds] = breakdownMiliseconds(timeLimit*1000);
    $("#count-down").html(`${minutes}:${seconds}`);

    var startTime = new Date().getTime();
    var countDown = setInterval(function() {
        var now = new Date().getTime();
        var distance = timeLimit*1000 - (now - startTime);
        var [minutes, seconds] = breakdownMiliseconds(distance);

        // Display
        if (distance >= 0) {
            $("#count-down").html(`${minutes}:${seconds}`);
        } else {
            // done!
            if (callback !== undefined) {
                callback();
            }
        }

    }, 1000);
    return countDown;
}

// given seconds, return minutes:seconds
function breakdownMiliseconds(miliseconds) {
    // because JS works in miliseconds we need to multiply it by 1000
    var minutes = Math.floor((miliseconds % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.round((miliseconds % (1000 * 60)) / 1000);
    if (seconds < 10) {
        seconds = `0${seconds}`;
    }
    return [minutes, seconds];
}
