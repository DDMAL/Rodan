(function ($) {
    "use strict";
    /*
    TODO:
    Fix Div membership code. Remove show/hide for the moment. Reintegrate show/hide when div structure is appropriate.
    CSS backgrounds for questionnaire div, each complex system div, and each subgroup div
    Save complex system structure in cSystems array
    
    */
    var divId = 0;
    var currentDiv = 0;
    var fields = [];
    var nStaves = 1;
    var nCSystems = 0;
    var cSystems = [];
    var q1 = "How many staves are there on the page?";
    var q2 = "How many multi-staff systems are there on the page? Enter 0 if there are none.";
    var q3 = "What is the number of the first staff in the system?";
    var q4 = "Does this system have the same structure as a previous system?";
    var q5 = "Which system?";
    var q6 = "How many staves are there in this system?";
    var q7 = "Do bar lines span the whole system?";
    var q8 = "How many subgroups are there in this system? Enter 0 if there are none."
    var q9 = "What is the number of the first staff in this subgroup?";
    var q10 = "How many staves are there in this subgroup?";
    var q11 = "Do bar lines span the entire subgroup?";
    
    function showNextField() {
        if (currentDiv < fields.length) {
            fields[currentDiv].show('slow');
            currentDiv++;
        }
    }
    
    function submitNumberField(pDiv, id1, id2, callback, zeroCallback) {
        var sectVal = $("#" + id1).val();
        var intRegex = /^\d+$/;
        if (intRegex.test(sectVal)) {
           if (sectVal > 0) {
               callback(pDiv, sectVal);
               showNextField();
               $("#" + id1).attr("disabled", true);
               $("#" + id2).detach();
           } else if (zeroCallback != null) {
               if (sectVal == 0) {
                   zeroCallback(pDiv);
                   showNextField();
                   $("#" + id1).attr("disabled", true);
                   $("#" + id2).detach();
               } else {
                   alert("Must enter a value if at least 0.");
                   return;
               }
           } else {
               alert("Must enter a value greater than 0.");
               return;
           }
        } else {
            alert("Invalid entry.");
            return;
        }
    }
    
    function submitBooleanField(pDiv, idYes, idNo, callback) {
        $("#" + idYes).detach();
        $("#" + idNo).detach();
        callback(pDiv);
        showNextField();
    }
    
    function addNumberField(div, question, id1, id2, firstDiv, callback, zeroCallback) {
        div.append("<div id=\"" + divId + "\"></div>");
        var nDiv = $("#" + divId);
        nDiv.append("<p>" + question + "</p>");
        nDiv.append("<input id=\"" + id1 + "\" type=\"text\" maxlength=3 size=3/>");
        nDiv.append("<button id=\"" + id2 + "\" type=\"button\">Submit</button>");
        
        if (firstDiv === false) {
            nDiv.hide();
            var divLoc = jQuery.inArray(div, fields);
            if (divLoc == -1) {
                fields.push(nDiv);
            } else {
                fields.splice(divLoc + nDiv.index() + 1, 0, nDiv);
            }
        }
        
        divId++;
        
        $("#" + id1).keypress(function(e) {
            if (e.keyCode == 13) {
                e.preventDefault();
                submitNumberField(nDiv, id1, id2, callback, zeroCallback)
            }
        });
        $("#" + id2).click(function(e) {
            submitNumberField(nDiv, id1, id2, callback, zeroCallback);
        });
    }
    
    function addBooleanField(div, question, idYes, idNo, firstDiv, callbackYes, callbackNo) {
        div.append("<div id=\"" + divId + "\"></div>");
        var nDiv = $("#" + divId);
        nDiv.append("<p>" + question + "</p>");
        nDiv.append("<button id=\"" + idYes + "\" type=\"button\">Yes</button>");
        nDiv.append("<button id=\"" + idNo + "\" type=\"button\">No</button>");
        
        if (firstDiv === false) {
            nDiv.hide();
            var divLoc = jQuery.inArray(div, fields);
            if (divLoc == -1) {
                fields.push(nDiv);
            } else {
                fields.splice(divLoc + nDiv.index() + 1, 0, nDiv);
            }
        }
        
        divId++;
        
        $("#" + idYes).click(function(e) {
            submitBooleanField(nDiv, idYes, idNo, callbackYes);
        });
        $("#" + idNo).click(function(e) {
            submitBooleanField(nDiv, idYes, idNo, callbackNo);
        });
    }
    
    function addSelectField(div, question, id1, id2, firstDiv, callback) {
        div.append("<div id=\"" + divId + "\"></div>");
        var nDiv = $("#" + divId);
        nDiv.append("<p>" + question + "</p>");
        nDiv.append("<select id=\"sel" + divId + "\"></select>");
        var selElement = $("#sel" + divId);
        var i;
        for (i = 0; i < nCSystems; i++) {
            selElement.append("<option value=\"" + (i + 1) + "\">" + (i + 1) + "</option>");
        }
    }
    
    var yesPrev = function(pDiv, val) {
        addSelectField(pDiv, q5, "wsystem" + divId, "wsystemsubmit" + divId, false, function(){});
    }
    
    var noPrev = function(pDiv, val) {
        addNumberField(pDiv, q6, "nstaves" + divId, "nstavessubmit" + divId, false, function(){}, null);
    }
    
    function addCSystemQuestions(q, index) {
        q.append("<div id=\"systemquestions\"></div>");
        var qDiv = $("#systemquestions");
        qDiv.append("<p>Complex System " + (index + 1) + ":</p>");
        addNumberField(qDiv, q3, "system" + divId, "systemsubmit" + divId, false, function(){}, null);
        if (index > 0) {
            addBooleanField(qDiv, q4, "prev" + divId, "prevsubmit" + divId, false, yesPrev, noPrev);
        } else {
            noPrev(qDiv);
        }
    }
    
    $(document).ready(function() {
        var q = $("#questionnaire");
        var staffCallback = function(pDiv, val) {
            nStaves = val;
        }
        var mStaffCallback = function(pDiv, val) {
            nCSystems = val;
            var i;
            for (i = 0; i < nCSystems; i++) {
                addCSystemQuestions(pDiv, i);
            }
        }
        var noMStaffCallback = function() {
            console.log("Make a whole page of single staves!");
        }
        
        addNumberField(q, q1, "staff" + divId, "staffsubmit" + divId, true, staffCallback, null);
        addNumberField(q, q2, "mstaff" + divId, "mstaffsubmit" + divId, false, mStaffCallback, noMStaffCallback);
        
        $('#form').submit(function () {
            
        });
    });
    
})(jQuery);
