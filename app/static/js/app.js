(function () {
  var storageKey = "personal-lms-theme";
  var root = document.documentElement;

  function applyTheme(themeName) {
    var allowed = ["default", "wired"];
    var normalized = allowed.indexOf(themeName) >= 0 ? themeName : "default";
    root.setAttribute("data-theme", normalized);
    localStorage.setItem(storageKey, normalized);

    var switcher = document.getElementById("theme-switcher");
    if (switcher) {
      switcher.value = normalized;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var switcher = document.getElementById("theme-switcher");
    var savedTheme = localStorage.getItem(storageKey) || root.getAttribute("data-theme") || "default";
    applyTheme(savedTheme);

    if (switcher) {
      switcher.addEventListener("change", function (event) {
        applyTheme(event.target.value);
      });
    }

    root.dataset.appReady = "true";
  });
})();
