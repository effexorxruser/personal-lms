(function () {
  function updateWorldClocks() {
    var nodes = document.querySelectorAll("[data-clock-zone]");

    nodes.forEach(function (node) {
      var zone = node.getAttribute("data-clock-zone");
      var time = node.querySelector("[data-clock-time]");
      var date = node.querySelector("[data-clock-date]");

      if (!zone || !time) return;

      var now = new Date();
      time.textContent = new Intl.DateTimeFormat("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: zone,
      }).format(now);
      if (date) {
        date.textContent = new Intl.DateTimeFormat("ru-RU", {
          day: "2-digit",
          month: "2-digit",
          timeZone: zone,
        }).format(now);
      }
    });
  }

  function setupSingleAccordions() {
    document.querySelectorAll('[data-accordion="single"]').forEach(function (accordion) {
      accordion.querySelectorAll('details').forEach(function (details) {
        details.addEventListener('toggle', function () {
          if (!details.open) return;
          accordion.querySelectorAll('details[open]').forEach(function (other) {
            if (other !== details) other.open = false;
          });
        });
      });
    });
  }

  function setupTabs() {
    document.querySelectorAll('[data-tabs]').forEach(function (tabList) {
      var buttons = Array.prototype.slice.call(tabList.querySelectorAll('[data-tab-target]'));

      function activate(targetId) {
        buttons.forEach(function (button) {
          var isActive = button.getAttribute('data-tab-target') === targetId;
          button.classList.toggle('is-active', isActive);
          button.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });

        document.querySelectorAll('[data-tab-panel]').forEach(function (panel) {
          panel.hidden = panel.id !== targetId;
        });
      }

      buttons.forEach(function (button) {
        button.setAttribute('role', 'tab');
        button.addEventListener('click', function () {
          activate(button.getAttribute('data-tab-target'));
        });
      });

      var active = buttons.find(function (button) { return button.classList.contains('is-active'); }) || buttons[0];
      if (active) activate(active.getAttribute('data-tab-target'));
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.dataset.appReady = "true";
    updateWorldClocks();
    setupSingleAccordions();
    setupTabs();
    window.setInterval(updateWorldClocks, 30000);
  });
})();
