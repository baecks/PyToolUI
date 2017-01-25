
function render_dashboard_pane (data) {
    $("#dashboardpane").html(data);
}

function load_dashboard (dashboard) {
    $.ajax({url: "/dashboard/" + dashboard, success: render_dashboard_pane});
}