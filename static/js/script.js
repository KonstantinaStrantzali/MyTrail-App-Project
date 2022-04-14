(function () {
  'use strict'
  const forms = document.querySelectorAll('.requires-validation')
  Array.from(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
      }, false)
    })
})()

    function checkInput(input) {
      //const input = document.getElementById("title")
      const value = input.value;
      
      
      if (value.length < 5) {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
      } 
      else if (input.type == "password" && value.length < 8)  {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
      }
      
      else {
        input.classList.add("is-valid");
        input.classList.remove("is-invalid");
      }
      
    }

   
