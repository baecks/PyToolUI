
function activate_tooltips(){
    $('[data-toggle="tooltip"]').tooltip({delay: { show: 200 }});
}

function load_loggedout_page(){
    window.location.assign("/loggedout");
}

function render_dashboard_pane (data) {
    $('[data-toggle="tooltip"]').tooltip('hide');
    $('#navbarCollapse').collapse('hide')
    $('#dashboardpane').fadeOut('fast', function() {
        $('#dashboardpane').html(data);
        activate_tooltips();
        $('#dashboardpane').fadeIn('fast');

        // Adds a JAVASCRIPT handler for any form submit button
        $('form').on( "submit", function( event ) {
            event.preventDefault();
            $.ajax({ type: "POST",
                      url: $(this).attr('action'),
                      data: $(this).serialize(),
                      success: render_dashboard_pane,
                      statusCode: { 403: function() { load_loggedout_page(); }}});
            });
    });
}

function raise_event(url) {
    //$('#navbarCollapse').collapse('hide')
    //$('[data-toggle="tooltip"]').tooltip('hide');
    //$("#dashboardpane").fadeOut(750);
    $.ajax({url: url,
            success: render_dashboard_pane,
            statusCode: { 403: function() { load_loggedout_page(); }}
            });
}

// Used by the main navbar to load dashboard instances
function load_dashboard (dashboard) {
    raise_event("/dashboard/" + dashboard)
}
