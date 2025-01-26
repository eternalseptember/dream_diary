// This toggles dark and light modes and saves it into localstorage.
function light_mode() {
    $("html").attr("data-theme", "light");

    if (localStorage.getItem("dark_mode") != null) {
        localStorage.removeItem("dark_mode");
    }
}

function dark_mode() {
    $("html").attr("data-theme", "dark");
    localStorage.setItem("dark_mode", "true");
}

(localStorage.getItem("dark_mode") == null) ? light_mode() : dark_mode();

$(document).ready(function() {
    $("#color_mode_switcher").click(function() {
        (localStorage.getItem("dark_mode") == null) ? dark_mode() : light_mode();
    });
});