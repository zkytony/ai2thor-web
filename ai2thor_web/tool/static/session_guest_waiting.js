// Script to handle redirection in the waiting page for the guests
function setUpEventListener(session_id, event_waiting, on_receive_func) {
    var uri_args = $.param({"event_waiting": event_waiting});
    var source = new EventSource(`/session/${session_id}/guest/stream?${uri_args}`);

    source.addEventListener(event_waiting, function(event) {
        on_receive_func(event);
    }, false);
}
