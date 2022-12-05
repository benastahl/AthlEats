let profile_button = document.querySelector(".profile-details")
let profile_dropdown = document.querySelector(".profile-dropdown")
let profile_chevron = document.querySelector(".profile-details .arrow")
let profile_dropdown_activated = false;
let profile_dropdown_options = document.querySelectorAll(".home-section nav .profile-dropdown ul li")

window.addEventListener('load', function() {
  for (let i = 0; i < profile_dropdown_options.length; i++) {
      console.log("Set size of options.")
      profile_dropdown_options[i].style.width = profile_button.getBoundingClientRect().width + "px";
  }
})


let hide_profile_dropdown = function () {
  profile_button.style.borderRadius = "25px";
  profile_button.style.border = "2px solid black"
  profile_dropdown.style.visibility = "hidden"
  profile_chevron.className = "arrow bx bx-chevron-down"
  profile_dropdown_activated = false;

  document.querySelector(".home-content").removeEventListener('click', hide_profile_dropdown)

}

let show_profile_dropdown = function () {
  profile_button.style.borderRadius = "25px 25px 0px 0px";
  profile_button.style.borderBottom = "0px"
  profile_dropdown.style.visibility = "visible"
  profile_chevron.className = "arrow bx bx-chevron-up"
  profile_dropdown_activated = true;

  document.querySelector(".home-content").addEventListener('click', hide_profile_dropdown)

}

profile_button.onclick = function () {
  if (!profile_dropdown_activated) {
        show_profile_dropdown()
  } else {
      hide_profile_dropdown()
  }
}

