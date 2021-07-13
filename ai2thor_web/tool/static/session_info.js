// Script for the session_admin.fhtml page (URL /session/<id>/admin)
function setUpEventListener_GuestJoin(session_id) {
    var source = new EventSource(`/session/${session_id}/admin/stream`);
    source.addEventListener("guest_join", function(event) {
        let roles = event.data.split(",");
        roles.forEach(function(role) {
            $(`#${role}-joining`).addClass("bg-success").addClass("text-light");
        });
    }, false)
}
