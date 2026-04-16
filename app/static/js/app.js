(function () {
  var storageKey = "personal-lms-theme";
  var root = document.documentElement;

  function applyTheme(themeName) {
    var allowed = ["dark", "light"];
    var normalized = allowed.indexOf(themeName) >= 0 ? themeName : "dark";
    root.setAttribute("data-theme", normalized);
    localStorage.setItem(storageKey, normalized);

    var switcher = document.getElementById("theme-switcher");
    if (switcher) {
      switcher.value = normalized;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var switcher = document.getElementById("theme-switcher");
    var savedTheme = localStorage.getItem(storageKey) || root.getAttribute("data-theme") || "dark";
    applyTheme(savedTheme);

    if (switcher) {
      switcher.addEventListener("change", function (event) {
        applyTheme(event.target.value);
      });
    }

    root.dataset.appReady = "true";
  });
})();
