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

/* Retrieve the ID of the currently displayed document. */
function findDocumentId() {
    id = $(".docid").html();
    return id;
}

/* Given any descendant of a HTML "element" object, find the
   master (root) node of that element.*/
function findRootOfCurrentElement(domel)
{
    return $(domel).parents(".element");
}

/* Given a DOM entry, find the Vyperlink Element-ID it relates to.
   Traverse DOM tree upwards as necessary.
*/
function getElementId(el)
{
    var rootelement = findRootOfCurrentElement(el);
    var id = rootelement.find(".vid").html();
    return id;
}


/* ================================================================ */
/* UI callbacks                                                     */
/* ================================================================ */

function vOnEdit() {
    vEditOrSaveElement("edit",findRootOfCurrentElement(this));
}

function vOnSave() {
    vEditOrSaveElement("save",findRootOfCurrentElement(this));
}

function vOnInsertBelow() {
    vDoInsertAboveOrBelow(findRootOfCurrentElement(this),"below");
}

function vOnInsertAbove() {
    vDoInsertAboveOrBelow(findRootOfCurrentElement(this),"above");
}

function vOnRemoveFromContainer() {
    vDoRemoveFromContainer(findRootOfCurrentElement(this));
}

function vOnDeleteElement() {
    vDoDeleteElement(findRootOfCurrentElement(this));
}


/* ================================================================ */
/* Actual Workers                                                   */
/* ================================================================ */

function vDoRemoveFromContainer(ref)
{
    var id = ref.find(".vid").html();  // @todo maybe put into separate method
    $.ajax({
	method: "post",
	url: "/removeelementfromcontainer",
	data: { "id":id,
		"parentid":findDocumentId() },
	success: function(data,textStatus,xhr) {
	    // remove from DOM tree, as a more pleasing alternative to window.location.reload();
	    ref.remove();
	    //alert("success");
	},
	error: function() {
	    alert("error");
	}
    });
}


/* Insert a new element above (where=="above") or below (where=="below")
   the DOM element specified by ref */
function vDoInsertAboveOrBelow(ref,where,bEditRightAway=false)
{
    // find the ID of the element we're dealing with (implementation might change)
    var id = ref.find(".vid").html();  // @todo maybe put into separate method
    // (1) duplicate default element template and insert below current one
    // (2) asynchronously request insertion server-side, resulting in 
    //     a) a final id to replace the temporary self-assigned one, and 
    //     b) the initial timestamp required for validating our submission
    
    // (1) jquery.js magic to duplicate template element
    //     (assuming template element is always first element in document)
    template_element = $(".element")[0];
    clone = $(template_element).clone(true);
    // modify the clone's data where necessary
    // ...
    clone.find(".vid").html("retrieving...");
    clone.find(".debuginfo").html("retrieving...");
    clone.find(".itempresenter").html("empty<br/>2.<br/>3.");

    var url="/undefined1";
    if(where=="below") {
	ref.after(clone);
	url = "/insertbelow";
    } else if(where=="above") {
	ref.before(clone);
	url = "/insertabove";
    } else {
	alert("Unknown 'where': "+where);
    }

    // (2) asynchronous insertion request. Wails and woe if it fails.
    $.ajax({
	url: url,
	data: { "id":id, "parentid":findDocumentId() },
	// @todo unique element path (starting from root, 
	// allowing for multiple element instances)
	type: "post",
	success: function(data,textStatus,xhr) {
	    vInsertionConfirmed(clone,data);
	    if(bEditRightAway) {
		vEditOrSaveElement("edit",clone);
	    }
	},
	error: function() {
	    alert("error during vDoInsertAboveOrBelow(ref,where="+where+").");
	}
    });
}

/* "insertbelow"/"insertabove" server call returned successfully. 
   Fill the corresponding GUI
   element with the returned values. */
function vInsertionConfirmed(ref,data) {
    //alert("insertion confirmed"+data.id);
    ref.find(".vid").html(data.id);
    ref.find(".debuginfo").html(data.ts);
}
    
function vOnNewDoc() {
    //alert("so you would like to create a new document, huh?");
    
    return(false);
}

/* capture common functionality of the two.
     in action: "edit" or "save"
    in el:     jquery element pointing to the clicked button? el root!!
*/
function vEditOrSaveElement( action, el ) {
    var ref = el; //.parent().parent();
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

	// Remove all callbacks, ready for next editing action.
	// ** IMPORTANT!! Really should be done "on-exit" from editing. **
	textarea.off();

	//alert(rawtext);
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
    var previous_keyup_event; // to detect double-ENTER
    //alert(editbox.html());
    displaybox.hide("fast");
    textarea.val(data.r);
    editbox.show("fast",function() { textarea.focus(); } );

    // insert callbacks so we can react to special keys
    // @bug - right now this gets attached over and over again! do this onLoad. Or make sure
    // we remove the callbacks again when we exit edit mode.
    textarea.on("keydown", function(a) {
	// (this) is the textarea object
	if(a.which==13 && a.shiftKey) {  // SHIFT+ENTER
	    a.preventDefault();
	    vEditOrSaveElement("save",$(this).parents(".element")); 
	    console.log("save triggered: "+$(this).parent().toString());
//	    console.dir($(this).parent());
	    console.log("object: %o",$(this).parents(".element"));
	    alert("Save triggered!");
	}
	if(a.which == 40) { // down arrow - store caret position
	    savedCaretPos = $(this).prop("selectionStart");
	}
	if(a.which == 38) { // up arrow - store caret position
	    savedCaretPos = $(this).prop("selectionStart");
	}
    });
    textarea.on("keyup", function(a) {
	if(a.which == 40) { // down arrow released - has caret position changed?
	    var newCaretPos = $(this).prop("selectionStart");
	    if(newCaretPos==savedCaretPos) {
		vSaveCurrentAndProceedUpOrDown($(this).parents(".element"),"down");
	    }
	}
	if(a.which == 38) { // up arrow released - has caret position changed?
	    var newCaretPos = $(this).prop("selectionStart");
	    if(newCaretPos==savedCaretPos) {
		vSaveCurrentAndProceedUpOrDown($(this).parents(".element"),"up");
	    }
	}
	if(a.which == 13) { // Hitting ENTER twice will create a new element,
                            // splitting the current element at the caret position.
	    if(previous_keyup_event.which == 13) {
		// split
		//alert("splitting");
		// (1) (Trigger) save(ing) current element
		vEditOrSaveElement("save",$(this).parents(".element")); 
		// (2) Insert a new element below, and start editing it right away
		vDoInsertAboveOrBelow(ref,"below",true);

	    }
	}
	previous_keyup_event = a;
    });
    //alert(data.r);
}

function vSaveCurrentAndProceedUpOrDown(el,dir)
{
    console.log("I'm going to save this element, and proceed to editing the element '"+dir+"' from me!");
    console.log("aE: %o",el);
    if(dir=="up") {
	var nextElement = el.prev(".element");
    } else {
	var nextElement = el.next(".element");
    }
    console.log("next/previous one along: %o",nextElement);
    if(nextElement.length>0) {
	console.log("there is a next/previous sibling. let's do it!");
	vEditOrSaveElement("save",el);
	vEditOrSaveElement("edit",nextElement);
    } else {
	console.log("sorry, no more sibling in this direction. staying put.");
    }
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

/* Given a DOM entry, find the Vyperlink Element-ID it relates to.
   Traverse DOM tree upwards as necessary.
*/
function getElementId(el)
{
    var rootelement = findRootOfCurrentElement(el);
    var id = rootelement.find(".vid").html();
    return id;
}

function vOnConvertToTextElement()
{
    //vEditOrSaveElement("save",$(this).parents(".element"));
}

function vOnConvertToQueryElement()
{
    var id = getElementId(this);
    $.ajax({
	method: "post",
	url: "/converttoqueryelement",
	data: { "id":id },
	success: function(data,textStatus,xhr) {
	    window.location.reload();
	    //alert("success");
	},
	error: function() {
	    alert("error");
	}
    });
}


/* More... button was mouseovered - display submenu */
function vOnElementMore()
{
    el = $(this);
    var popup = $('<div class="morepopup" onmouseleave="$(this).remove();">' +
		  '<ul><li><a class="converttoqueryelementbutton" href="#">convert to QueryElement</a></li>' +
		  '<li><a class="converttotextelementbutton" href="#">convert to TextElement</a></li>' +
		  '<li><a class="insertbelowbutton" href="#">insert Element below</a></li>' +
		  '<li><a class="removefromcontainerbutton" href="#">remove Element from container</a></li>' +
		  '<li><a class="deleteelementbutton" href="#">delete Element</a></li>' +
		  '</ul></div>');
    el.after(popup);
    $("li a.insertbelowbutton").on("click",vOnInsertBelow);
    $(".converttotextelementbutton").on("click",vOnConvertToTextElement);
    $(".converttoqueryelementbutton").on("click",vOnConvertToQueryElement);
    $(".removefromcontainerbutton").on("click",vOnRemoveFromContainer);
    $(".deleteelementbutton").on("click",vOnDeleteElement);
}

/* "main" */

$(function() {
    $(".editbutton").on("click",vOnEdit);
    $(".savebutton").on("click",vOnSave);
    $(".insertbelowbutton").on("click",vOnInsertBelow);
    $(".insertabovebutton").on("click",vOnInsertAbove);
    $(".newdocbutton").on("click",vOnNewDoc);
    $(".morebutton").on("mouseover",vOnElementMore);
});
