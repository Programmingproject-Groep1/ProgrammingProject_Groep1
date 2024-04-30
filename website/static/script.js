import { Input, Ripple, initMDB } from "mdb-ui-kit";

initMDB({ Input, Ripple });

flatpickr("input[type=datetime-local]", {
  mode: "range",
  minDate: "today",
  locale: { firstDayOfWeek: 1 },
});
