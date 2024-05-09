//Code voor datepicker
fetch("/reserved_dates")
  .then((response) => response.json())
  .then((reservedDates) => {
    $("input[type=datetime-local]").each(function () {
      var itemId = $(this).data("item-id");
      var userId = $(this).data("user-id");
      var itemReservedDates = reservedDates[itemId] || [];
      var disabledDates = itemReservedDates.map((dateStr) => new Date(dateStr));
      let binnen2weken = new Date();
      let restDagen = 5 - binnen2weken.getDay();
      binnen2weken.setDate(binnen2weken.getDate() + 14 + restDagen);
      let weekends = [];
      if (userId == 2) {
        let vandaag = new Date();
        for (let i = 0; i < 14; i++) {
          vandaag.setDate(vandaag.getDate() + 1);
          if (vandaag.getDay() == 0 || vandaag.getDay() == 6) {
            weekends.push(new Date(vandaag));
          }
        }
      }

      flatpickr(this, {
        mode: "range",
        minDate: "today",
        maxDate: userId == 2 ? binnen2weken : null,
        locale: { firstDayOfWeek: 1 },
        disable: [...disabledDates, ...weekends],
        onDayCreate: function (dObj, dStr, fp, dayElem) {
          // format the date as a string
          var dateStr = fp.formatDate(dayElem.dateObj, "Y-m-d");

          // if the date is in the item's reservedDates array, add the "reserved-date" class
          if (itemReservedDates.indexOf(dateStr) > -1) {
            dayElem.classList.add("reserved-date");
          }
        },
      });
    });
  });

//Code om info over artikel te tonen in modal
$(document).ready(function () {
  $(".myModal").on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var title = button.data("title"); // Extract info from data-* attributes
    var img = button.data("img");
    var desc = button.data("desc");
    var brand = button.data("brand");
    // Update the modal's content.
    var modal = $(this);
    modal.find(".modal-title").text(title);
    modal.find(".modal-img").attr("src", img);
    modal.find(".modal-desc").text(desc);
    modal.find(".modal-brand").text(brand);
  });
});

//Zorgt ervoor dat de modal niet geopend word als je op 1 van de buttons klikt in de card
$(document).ready(function () {
  $(".card-button").click(function (event) {
    event.stopPropagation();
  });
});

// Get all elements that should trigger the modal
var triggerElements = document.querySelectorAll(".trigger-class");

// Add click event listener to each trigger element
triggerElements.forEach(function (element) {
  element.addEventListener("click", function (event) {
    // Check if the clicked element or its parent is a carousel button
    if (!event.target.matches(".carouselBtn, .carouselBtn *")) {
      // Trigger the modal
    }
  });
});

// Code voor admin dashboard
document.getElementById("option1").addEventListener("click", function () {
  document.getElementById("uitleentekst").textContent =
    "Het artikel is opgehaald";
  let form_name = document.getElementById("form_name");
  form_name.value = "ophalen";
  let div = document.getElementById("uitleeninputs");
  div.innerHTML = "";
});
document.getElementById("option2").addEventListener("click", function () {
  document.getElementById("uitleentekst").textContent =
    "Het artikel is teruggebracht";
  let form_name = document.getElementById("form_name");
  form_name.value = "inleveren";

  let div = document.getElementById("uitleeninputs");

  if (!document.getElementById("schadeSelect")) {
    let select = document.createElement("select");
    select.name = "schade";
    select.id = "schadeSelect";
    select.classList.add("form-select");
    select.ariaLabel = "Default select example";
    let optionNee = document.createElement("option");
    let optionJa = document.createElement("option");
    optionNee.value = "nee";
    optionNee.selected = true;
    optionNee.textContent = "Nee";
    optionJa.value = "ja";
    optionJa.textContent = "Ja";
    select.appendChild(optionNee);
    select.appendChild(optionJa);
    let schadelabel = document.createElement("label");
    schadelabel.textContent = "Schade aan artikel?";
    schadelabel.htmlFor = "schade";
    div.appendChild(schadelabel);
    div.appendChild(select);

    select.addEventListener("change", function () {
      if (optionJa.selected == true) {
        let textarea = document.createElement("textarea");
        textarea.classList.add("form-control");
        textarea.id = "schadeBeschrijving";
        textarea.name = "schadeBeschrijving";
        textarea.rows = "3";
        textarea.placeholder = "Beschrijf de schade";
        let beschrijvingLabel = document.createElement("label");
        beschrijvingLabel.textContent = "Beschrijving van de schade: ";
        beschrijvingLabel.htmlFor = "schadeBeschrijving";
        div.appendChild(beschrijvingLabel);
        div.appendChild(textarea);

        let fotoUpload = document.createElement("input");
        fotoUpload.type = "file";
        fotoUpload.id = "fotoUpload";
        fotoUpload.name = "fotoUpload";
        let fotoLabel = document.createElement("label");
        fotoLabel.textContent = "Upload foto van de schade: ";
        fotoLabel.htmlFor = "fotoUpload";
        div.appendChild(fotoLabel);
        div.appendChild(fotoUpload);
      } else {
        let textarea = document.getElementById("schadeBeschrijving");
        let fotoUpload = document.getElementById("fotoUpload");
        let beschrijvingLabel = document.querySelector(
          "label[for='schadeBeschrijving']"
        );
        let fotoLabel = document.querySelector("label[for='fotoUpload']");
        if (textarea) {
          textarea.remove();
          beschrijvingLabel.remove();
        }
        if (fotoUpload) {
          fotoUpload.remove();
          fotoLabel.remove();
        }
      }
    });
  }
});

document
  .getElementById("artikelIdInput")
  .addEventListener("change", function () {
    let id = this.value;
    let div = document.getElementById("uitleenextra");
    div.innerHTML = "";
    if (!id) {
      // If the input is empty, don't make a fetch request
      return;
    }
    fetch(`/get-artikel?id=${id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Geen artikel gevonden met dit ID");
        }
        return response.json();
      })
      .then((data) => {
        // Assuming the response data has `title` and `afbeelding` properties
        let title = document.createElement("h3");
        let img = document.createElement("img");

        title.textContent = data.title;
        img.src = data.afbeelding;

        div.appendChild(title);
        div.appendChild(img);

        let div2 = document.getElementById("uitleeninputs");
      })
      .catch((error) => {
        console.error(error);
      });
  });
