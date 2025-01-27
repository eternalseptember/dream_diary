// This toggles the title and the search form, and saves it into a localstorage
// cookie, so that the state is kept when navigating search results.
function show_search() {
    $("#advanced_search_title").html("Advanced Search ⇈");
    $("#advanced_search_form_container").show();
    
    if (localStorage.getItem("search_hidden") != null) {
        localStorage.removeItem("search_hidden");
    }
}

function hide_search() {
    $("#advanced_search_title").html("Advanced Search ⇊");
    $("#advanced_search_form_container").hide();
    localStorage.setItem("search_hidden", "true");
}

(localStorage.getItem("search_hidden") == null) ? show_search() : hide_search();

$(document).ready(function() {
    // Toggles the title and search form.
    $("#advanced_search_title").click(function() {
        (localStorage.getItem("search_hidden") == null) ? hide_search() : show_search();
    });

    // Clears the multiselect field.
    $("#clear_multi_choices").click(function() {
        $('select[multiple]').val('');
    });
});




