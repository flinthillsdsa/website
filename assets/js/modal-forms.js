document.addEventListener("DOMContentLoaded", function() {
  // list all the form IDs in your modals
  [ "contactUsForm", "discordForm" ].forEach(function(id) {
    var form = document.getElementById(id);
    if (!form) return;

    form.addEventListener("submit", function(e) {
      e.preventDefault();               // stop the normal POST+redirect
      var data = new FormData(form);

      fetch(form.action, {
        method: "POST",
        body: data,
        headers: { "Accept": "application/json" }
      })
      .then(function(response) {
        if (response.ok) {
          // on success, replace the form with a message
          form.innerHTML = `
            <div class="alert alert-success">
              Thanks! Your request has been sent.
            </div>`;
        } else {
          // on server‐side error, show an error
          return response.json().then(function(err) {
            throw err;
          });
        }
      })
      .catch(function() {
        var errBox = form.querySelector(".help-block.text-danger");
        if (errBox) errBox.textContent = "Oops — something went wrong. Please try again.";
      });
    });
  });
});
