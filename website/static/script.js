//Code voor datepicker
fetch("/reserved_dates")
  .then((response) => response.json())
  .then((reservedDates) => {
    $("input[type=datetime-local]").each(function () {
      var itemId = $(this).data("item-id");
      var userId = $(this).data("user-id");
      var isMultiple = $(this).data("is-multiple");
      var amount = $(this).data("amount");
      var itemReservedDates = reservedDates[itemId] || [];
      var disabledDates = itemReservedDates.map(
        (dateStr) => new Date(dateStr).toISOString().split("T")[0]
      );

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
        onChange: function (selectedDates, dateStr, instance) {
          if (userId == 2 && selectedDates.length === 1) { // Student: restrict to Monday-Friday
            let startDate = selectedDates[0];
            let endDate = new Date(startDate);
            let day = startDate.getDay();
            if (day !== 1) {
              startDate.setDate(startDate.getDate() - (day - 1)); // Move to Monday
            }
            endDate.setDate(startDate.getDate() + (5 - startDate.getDay())); // Set to Friday
            instance.setDate([startDate, endDate], true);
          }
        },
        onDayCreate: function (dObj, dStr, fp, dayElem) {
          var dateStr = fp.formatDate(dayElem.dateObj, "Y-m-d");
          if (disabledDates.includes(dateStr)) {
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
    var startDatum = button.data("startDatum");
    startDatum = new Date(startDatum).toLocaleDateString();
    var eindDatum = button.data("eindDatum");
    eindDatum = new Date(eindDatum).toLocaleDateString("nl-NL");

    // Update the modal's content.
    var modal = $(this);
    modal.find(".modal-title").text(title);
    modal.find(".modal-img").attr("src", img);
    modal.find(".modal-desc").text(desc);
    modal.find(".modal-brand").text(brand);
    modal.find(".modal-startDatum").text(startDatum);
    modal.find(".modal-eindDatum").text(eindDatum);
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

let option1 = document.getElementById("option1");
if (option1) {
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
      schadelabel.textContent = "Schade aan artikel? ";
      schadelabel.htmlFor = "schade";
      let p = document.createElement("p");
      p.id = "schadeP";
      p.appendChild(schadelabel);
      p.appendChild(select);
      div.appendChild(p);

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
          let fotoLabel = document.createElement("label");
          fotoLabel.textContent = "Upload een foto van de schade: ";
          fotoLabel.htmlFor = "fotoUpload";
          let fotoUpload = document.createElement("input");
          fotoUpload.type = "file";
          fotoUpload.id = "fotoUpload";
          fotoUpload.name = "file";
          fotoUpload.accept = "image/*";
          let gebruikP = document.createElement("p");
          gebruikP.textContent = "Kan het artikel nog gebruikt worden? ";
          let gebruikSelect = document.createElement("select");
          gebruikSelect.name = "gebruik";
          let gebruikJa = document.createElement("option");
          let gebruikNee = document.createElement("option");
          gebruikJa.value = "ja";
          gebruikJa.textContent = "Ja";
          gebruikNee.value = "nee";
          gebruikNee.textContent = "Nee";
          gebruikSelect.appendChild(gebruikJa);
          gebruikSelect.appendChild(gebruikNee);
          gebruikP.appendChild(gebruikSelect);

          div.appendChild(fotoLabel);
          div.appendChild(fotoUpload);
          div.appendChild(beschrijvingLabel);
          div.appendChild(textarea);
          div.appendChild(gebruikP);
        } else {
          let textarea = document.getElementById("schadeBeschrijving");

          let beschrijvingLabel = document.querySelector(
            "label[for='schadeBeschrijving']"
          );
          let fotoLabel = document.querySelector("label[for='fotoUpload']");
          let fotoUpload = document.getElementById("fotoUpload");
          if (textarea) {
            textarea.remove();
            beschrijvingLabel.remove();
            fotoUpload.remove();
            fotoLabel.remove();
          }
        }
      });
    }
  });
}

let artikelIdInput = document.getElementById("artikelIdInput");

if (artikelIdInput) {
  document
    .getElementById("artikelIdInput")
    .addEventListener("change", function () {
      let id = this.value;
      let div = document.getElementById("artikelExtra");
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
        })
        .catch((error) => {
          console.error(error);
        });
    });
  document
    .getElementById("userIdInput")
    .addEventListener("change", function () {
      let id = this.value;
      let div = document.getElementById("userExtra");
      let tekst = div.querySelector("h4");
      if (!tekst) {
        tekst = document.createElement("h4");
      } else {
        tekst.textContent = "";
      }

      if (!id) {
        return;
      }
      fetch(`/get-user?id=${id}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Geen gebruiker gevonden met dit ID");
          }
          return response.json();
        })
        .then((data) => {
          // Assuming the response data has `title` and `afbeelding` properties

          tekst.textContent = data.user;

          div.appendChild(tekst);
        })
        .catch((error) => {
          console.error(error);
        });
    });
}

//Zorgen dat als je klikt op item, gegevens artikel terechtkomen bij terugbrengen/ophalen

document.addEventListener("DOMContentLoaded", function () {
  let terugcards = document.querySelectorAll(".terugcard");
  let ophaalcards = document.querySelectorAll(".ophaalcard");
  let option1 = document.getElementById("option1");
  let option2 = document.getElementById("option2");

  terugcards.forEach((card) => {
    card.addEventListener("click", function () {
      let artikelid = card.getAttribute("data-artikelid");
      let userid = card.getAttribute("data-userid");
      option2.click();
      let artikelIdInput = document.getElementById("artikelIdInput");
      artikelIdInput.value = artikelid;
      artikelIdInput.dispatchEvent(new Event("change"));
      let userIdInput = document.getElementById("userIdInput");
      userIdInput.value = userid;
      userIdInput.dispatchEvent(new Event("change"));
    });
  });

  ophaalcards.forEach((card) => {
    card.addEventListener("click", function () {
      let artikelid = card.getAttribute("data-artikelid");
      let userid = card.getAttribute("data-userid");
      option1.click();
      let artikelIdInput = document.getElementById("artikelIdInput");
      artikelIdInput.value = artikelid;
      artikelIdInput.dispatchEvent(new Event("change"));
      let userIdInput = document.getElementById("userIdInput");
      userIdInput.value = userid;
      userIdInput.dispatchEvent(new Event("change"));
    });
  });
});

//Code voor confirmatie bij verwijderen artikel

document.addEventListener("DOMContentLoaded", function () {
  var deleteButtons = document.querySelectorAll("[data-confirm]");

  for (let deletebutton of deleteButtons) {
    deletebutton.addEventListener("click", function (event) {
      var confirmationMessage = this.getAttribute("data-confirm");
      if (!confirm(confirmationMessage)) {
        event.preventDefault();
      }
    });
  }

  window.onload = function () {
    const form = document.getElementById("filterForm");
    if (form) {
      const checkboxes = form.querySelectorAll('input[type="checkbox"]');
      let timeout;

      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
          clearTimeout(timeout);
          timeout = setTimeout(() => {
            form.submit();
          }, 1000);
        });
      });
    }
  };
});

//Code voor Artikelbeheer actief button

let actiefButtons = document.querySelectorAll(".actiefButton");

if (actiefButtons) {
  actiefButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var icon = this.querySelector("i");
      var isActiefInput = document.querySelector("#isActief");

      if (icon.classList.contains("fa-eye")) {
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
        isActiefInput.value = "false";
      } else {
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
        isActiefInput.value = "true";
      }
    });
  });
}
