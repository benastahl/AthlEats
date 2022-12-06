  let hide_form = function (id_name) {
      document.getElementById(id_name).style.display = "none"
      if (document.location.pathname === "/")
      document.querySelector(".home-content-buttons").style.display = "flex"
  }
  let show_form = function (id_name) {
      // BLUR
      let form = document.getElementById(id_name);
      form.style.filter = "none"

      console.log("Showing form: " + id_name)
      if (document.location.pathname === "/")
          document.querySelector(".home-content-buttons").style.display = "none"
      // Hide all other forms besides id_name form
      let all_form_elements = document.querySelectorAll(".access-form")
      for (let i = 0; i < all_form_elements.length; i++) {
          let form = all_form_elements[i];
          if (form.id !== id_name) {
              form.style.display = "none"
              continue;
          }
          if (form.id === "settings-form")
              hide_profile_dropdown()
          form.style.display = "flex";
      }
  }

  // If message return in render_template (flask)
  let message = null;
  if ("{{message_type}}") {
      message = document.querySelector("#{{ message_type }}-form .error-occurrence")
      message.style.display = "block";
      message.innerHTML =  "{{ message }}"
      show_form("{{message_type}}-form")
  }