
function activate_tooltips(){
    $('[data-toggle="tooltip"]').tooltip({delay: { show: 200 }});
}

function setup_tables(){
    $(".dashboard-table").DataTable( {"order": [[ 1, "desc" ]]} );
}

function load_loggedout_page(){
    window.location.assign("/loggedout");
}

function logout(){
    window.location.assign("/logoutaction");
}

function render_dashboard_pane (data) {
    $('[data-toggle="tooltip"]').tooltip('hide');
    $('#navbarCollapse').collapse('hide')
    $('#dashboardpane').fadeOut('fast', function() {
        $('#dashboardpane').html(data);
        activate_tooltips();
        setup_tables();
        $('#dashboardpane').fadeIn('fast');
        // Adds a JAVASCRIPT handler for any form submit button
        $('#dashboardpane form').on( "submit", function( event ) {
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

function setup_page(){
    activate_tooltips();
    $('#confirm-modal').on('show.bs.modal', function(e) {
        var data = $(e.relatedTarget).data();
        $('#confirmModalLabel', this).text(data.confirmTitle);
        $('#confirmModalBody', this).text(data.confirmQuestion);
        var $modalDiv = $(e.delegateTarget);
        $modalDiv.on('click', '#confirmModalButtonYes', function(e) {
            var $modalDiv = $(e.delegateTarget);
            $modalDiv.modal('hide');
            eval(data.confirmAction);
            });
        });
    }

/*
function adjust_graph_dashboard(){
    var top = $("#FullPageChart").position().top;
    var winheight = $(window).height();
    $("FullPageChart").css({'height' : winheight-top + "px"});
}

function setup_graph_dashboard(){
    $(window).resize( adjust_graph_dashboard() );
    adjust_graph_dashboard();

}*/