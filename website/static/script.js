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
