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
// let date = new Date();

// document.getElementById("date").innerText = date.toDateString();

// document.getElementById("prev").addEventListener("click", () => {
//   date.setDate(date.getDate() - 1);
//   document.getElementById("date").innerText = date.toDateString();
//   getItems();
// });

// document.getElementById("next").addEventListener("click", () => {
//   date.setDate(date.getDate() + 1);
//   document.getElementById("date").innerText = date.toDateString();
//   getItems();
// });

// function getItems() {
//   fetch(`/items-for-date?date=${date.toISOString().split("T")[0]}`)
//     .then((response) => response.json())
//     .then((data) => {
//       // Get the container for the items
//       const container = document.querySelector(".ophaal");

//       // Clear the current items
//       container.innerHTML = "";

//       // Add the new items
//       data.forEach((item) => {
//         const itemElement = document.createElement("div");
//         itemElement.className = "card";

//         const img = document.createElement("img");
//         img.className = "card-img-top";
//         img.src = `/static/images/${item.afbeelding}`;

//         itemElement.appendChild(img);
//         container.appendChild(itemElement);
//       });
//     });
// }
