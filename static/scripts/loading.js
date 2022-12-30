console.log("Activated loading screen!")
let loading_screen_activated = false;
let loading_overlay = document.querySelector(".loading-overlay")
loading_overlay.classList.toggle("active")
document.addEventListener("DOMContentLoaded",
    function () {
        loading_overlay.classList.toggle("active")
    }
)
function activateLoadingScreen(button_id) {
    loading_overlay.classList.toggle("active")
    if (button_id) {
        disableButton(button_id)
    }
}
function disableButton(id) {
    document.getElementById(id).disabled = true;
}

