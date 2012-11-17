(function ($) {
    "use strict";
    
    $(document).ready(function() {
        var previous_structure = $("#previous_structure").text();
        if (previous_structure == "None") {
            $("#prev_questions").detach();
        } else {
            $("#non_prev_questions").detach();
        }
        $("form input[type=submit]").click(function() {
            $("input[type=submit]", $(this).parents("form")).removeAttr("clicked");
            $(this).attr("clicked", "true");
        });
        $("#form").submit(function(e) {
            var submit_name = $("input[type=submit][clicked=true]").attr("name");
            if (submit_name == "sameasprev") {
                $("#staff-sequence").val(previous_structure);
            }
        });
       
    });
})(jQuery);
