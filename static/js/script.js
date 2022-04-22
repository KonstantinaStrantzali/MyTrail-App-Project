/* Form Validation, code taken  and modified from Bootstrap Documentation; https://getbootstrap.com/docs/5.0/forms/validation/ */

(function () {
  const forms = document.querySelectorAll('.requires-validation');
  Array.from(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
})();

/* form input validation */
    function checkInput(input) {
      const value = input.value;
      if (value.length < 1) {
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