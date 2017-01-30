
active_tooltip = null

function render_dashboard_pane (data) {
    $('#dashboardpane').fadeOut('fast', function() {
        $('#dashboardpane').html(data);
        $('[data-toggle="tooltip"]').tooltip({delay: { show: 200 }});
        //$('[data-toggle="tooltip"]').hover(function(){ $(this).tooltip('show'); }, function(){ $(this).tooltip('hide'); });

        $('#dashboardpane').fadeIn('fast');
    });
}

function load_dashboard (dashboard) {
    $('[data-toggle="tooltip"]').tooltip('hide');
    $("#dashboardpane").fadeOut(750);
    $.ajax({url: "/dashboard/" + dashboard, success: render_dashboard_pane});
}