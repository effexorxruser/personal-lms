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


  function formatTerminalRun(run) {
    var status = run.status || "completed";
    var header = "$ " + (run.normalized_command || run.command_text || "");
    var meta = "status: " + status + (run.exit_code !== null && run.exit_code !== undefined ? " / exit: " + run.exit_code : "");
    var output = run.stdout_text || "";
    var error = run.stderr_text || "";
    return [header, meta, output, error ? "stderr:\n" + error : ""].filter(Boolean).join("\n");
  }

  function renderTerminalHistory(output, runs) {
    if (!output) return;
    if (!runs || !runs.length) {
      output.textContent = "История запусков появится здесь.";
      return;
    }
    output.textContent = runs.map(formatTerminalRun).join("\n\n---\n\n");
    output.scrollTop = 0;
  }

  function setupLessonTerminals() {
    document.querySelectorAll("[data-terminal]").forEach(function (panel) {
      var lessonKey = panel.getAttribute("data-terminal-lesson");
      var input = panel.querySelector("[data-terminal-input]");
      var form = panel.querySelector("[data-terminal-form]");
      var output = panel.querySelector("[data-terminal-output]");
      var status = panel.querySelector("[data-terminal-status]");
      if (!lessonKey || !input || !form || !output) return;

      function setStatus(value) {
        if (status) status.textContent = value;
      }

      function loadHistory() {
        fetch("/api/terminal/lessons/" + encodeURIComponent(lessonKey) + "/history", {
          headers: { "Accept": "application/json" }
        })
          .then(function (response) { return response.ok ? response.json() : { runs: [] }; })
          .then(function (data) { renderTerminalHistory(output, data.runs); })
          .catch(function () { setStatus("history error"); });
      }

      function runCommand(command) {
        var value = (command || input.value || "").trim();
        if (!value) return;
        input.value = value;
        setStatus("running");
        fetch("/api/terminal/lessons/" + encodeURIComponent(lessonKey) + "/run", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify({ command: value })
        })
          .then(function (response) { return response.json(); })
          .then(function (data) {
            if (data.run) {
              renderTerminalHistory(output, [data.run]);
              setStatus(data.run.status || "completed");
              loadHistory();
            } else {
              setStatus("error");
            }
          })
          .catch(function () { setStatus("network error"); });
      }

      panel.querySelectorAll("[data-terminal-command]").forEach(function (button) {
        button.addEventListener("click", function () {
          runCommand(button.getAttribute("data-terminal-command"));
        });
      });

      form.addEventListener("submit", function (event) {
        event.preventDefault();
        runCommand();
      });

      loadHistory();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.dataset.appReady = "true";
    updateWorldClocks();
    setupSingleAccordions();
    setupTabs();
    setupLessonTerminals();
    window.setInterval(updateWorldClocks, 30000);
  });
})();
