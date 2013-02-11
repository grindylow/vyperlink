/* Main Vyperlink Client-side Processing */

/* (C) 2013 by Martin Grill
   GNU GPL applies: http://www.gnu.org/licenses/gpl.txt
*/

/* Generic useful functions */

/* Make the given Vyperlink ID HTML-safe (so it can be used
   as id attribute inside the DOM). */
function escapeID( id ) {
    // @todo: avoid illegal characters such as dot, etc.
    return id;
}




/* UI callbacks */

function vOnEdit() {
    vEditOrSaveElement("edit",$(this));
}

function vOnSave() {
    vEditOrSaveElement("save",$(this));
}


/* capture common functionality of the two.
     in action: "edit" or "save"
    in el:     jquery element pointing to the clicked button
*/
function vEditOrSaveElement( action, el ) {
    var ref = el.parent().parent();
    // find the ID of the element we're dealing with (implementation might change)
    var id = ref.find(".vid").html();  // @todo maybe put into separate method
    
    var savebutton = ref.find(".savebutton");
    var editbutton = ref.find(".editbutton");

    //alert("I am about to "+action+" element "+id+"!");

    // only edit if not already editing...
    if(action=="edit") {
	// ajax-get "raw" content, then enable editing
	el.attr("disabled","disabled"); // visual feedback
	$.ajax({
	    url: "/getrawforediting",
	    data: { "id":id },
	    success: function(data,textStatus,xhr) {
		vDoEditElement(ref,data);
		//alert("success");
	    },
	    error: function() {
		alert("error");
		el.removeAttr("disabled");
	    }
	});
    }

    if(action=="save") {
	// ajax-write "raw" content, then ajax-read parsed content
	//el.attr("disabled","disabled"); // visual feedback
	var editbox = ref.find(".itemeditor");
	var textarea = editbox.find("textarea");
	var rawtext = textarea.val();
	alert(rawtext);
	$.ajax({
	    url: "/putrawafterediting",
	    data: { "id":id,
		    "rawtext":rawtext },
	    type: "post",
	    success: function(data,textStatus,xhr) {
		editbutton.removeAttr("disabled");
		vDoSaveElementPart1(ref,data);
		//alert("success");
	    },
	    error: function() {
		alert("error");
	    }
	});
    }
}

// Unhide the text field, load it with the raw contents as retrieved
// from the server, and let the user edit to her heart's content.
function vDoEditElement(ref,data) {
    var editbox = ref.find(".itemeditor");
    var textarea = editbox.find("textarea");
    var displaybox = ref.find(".itempresenter");
    //alert(editbox.html());
    displaybox.hide();
    textarea.val(data.r);
    editbox.show();
    //alert(data.r);
}

// Write raw text back to server. Show parsed HTML (again).
// Conveniently, AJAX-storing the new raw text will return
// the parsed HTML version, which we procede to display right away.
function vDoSaveElementPart1(ref,data) {
    var editbox = ref.find(".itemeditor");
    var textarea = editbox.find("textarea");
    var displaybox = ref.find(".itempresenter");
    //alert(editbox.html());
    textarea.val("text removed for safety");
    displaybox.html(data.r);
    editbox.hide();
    displaybox.show();
    //alert(data.r);

    // re-enable "edit" button
    
}



/* "main" */

$(function() {
    $(".editbutton").on("click",vOnEdit);
    $(".savebutton").on("click",vOnSave);
});
