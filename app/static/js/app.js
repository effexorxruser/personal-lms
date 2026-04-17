(function () {
  function updateWorldClocks() {
    var nodes = document.querySelectorAll("[data-clock-zone]");

    nodes.forEach(function (node) {
      var zone = node.getAttribute("data-clock-zone");
      var time = node.querySelector("[data-clock-time]");
      var date = node.querySelector("[data-clock-date]");

      if (!zone || !time || !date) return;

      var now = new Date();
      time.textContent = new Intl.DateTimeFormat("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: zone,
      }).format(now);
      date.textContent = new Intl.DateTimeFormat("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        timeZone: zone,
      }).format(now);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.dataset.appReady = "true";
    updateWorldClocks();
    window.setInterval(updateWorldClocks, 30000);
  });
})();
