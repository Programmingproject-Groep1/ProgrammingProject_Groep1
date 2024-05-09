//Code voor datepicker
fetch("/reserved_dates")
  .then((response) => response.json())
  .then((reservedDates) => {
    flatpickr("input[type=datetime-local]", {
      mode: "range",
      minDate: "today",
      locale: { firstDayOfWeek: 1 },
      onDayCreate: function (dObj, dStr, fp, dayElem) {
        // get the current item ID from somewhere (e.g., the input's data attributes)
        var itemId = $(this.element).data("item-id");

        // get the reserved dates for this item
        var itemReservedDates = reservedDates[itemId] || [];

        // format the date as a string
        var dateStr = fp.formatDate(dayElem.dateObj, "Y-m-d");

        // if the date is in the item's reservedDates array, add the "reserved-date" class
        if (itemReservedDates.indexOf(dateStr) > -1) {
          dayElem.classList.add("reserved-date");
        }
      },
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
