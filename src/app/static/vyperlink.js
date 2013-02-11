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
    console.log(el);
    console.log(el.parent().parent().html());

    // identify some key elements
    top = $(el).parent().parent();
    editdiv = top; // @todo dive down
    //textbox = editdiv.find(".textbox");

    // only edit if not already editing...
    //...
    // ajax-get "raw" content, then enable editing
}



/* "main" */

$(function() {
    $(".editbutton").on("click",vOnEdit);
    $(".savebutton").on("click",vOnSave);
});
