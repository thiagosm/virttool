$(document).ready(function(){               

    jQuery("#ajax-indicator").ajaxStart(function() {  $(this).show(); });
    jQuery("#ajax-indicator").ajaxStop(function() { $(this).hide(); });

});