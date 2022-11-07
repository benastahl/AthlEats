function adapt_size_listening() {

    let home_section = document.querySelector(".home-section");



    //
    if (home_section.className.includes("mobile"))
        return false;

    home_section.classList.toggle("mobile");

    window.addEventListener('resize', function() {
      if (window.outerWidth < 650) {
          adapt_mobile()
      } else if (window.outerWidth >= 650) {
        default_home_visual()
      }
    })

    if (window.outerWidth < 650) {
      adapt_mobile()
    } else if (window.outerWidth >= 650) {
      default_home_visual()
    }

}

function adaptive_home_visual() {
          if (document.querySelector(".process-visual").className.includes("mobile")) {
              return false;
          }
          document.querySelector(".process-visual").classList.toggle("mobile")

      }
function default_home_visual() {
  if (!document.querySelector(".process-visual").className.includes("mobile")) {
      return false;
  }

  document.querySelector(".reserve-pickup-button .front").style.fontSize = "40px"
  document.querySelector(".process-visual").classList.remove("mobile")

}

function adapt_mobile() {
  document.querySelector(".popular-restaurants").classList.toggle("mobile")
  document.querySelector(".popular-restaurants.mobile").style.width = window.outerWidth - 40 + "px";
  document.querySelector(".popular-restaurants.mobile .restaurant-visual").style.width = window.outerWidth - 40 - 40 + "px";

  let popular_website_images = document.querySelectorAll(".popular-restaurants.mobile img")
  for (let i = 0; i < popular_website_images.length; i++) {
      popular_website_images[i].style.width = window.outerWidth - 40 - 40 + "px";

  }
}