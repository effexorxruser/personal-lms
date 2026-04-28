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



  function openLessonTerminal(panel) {
    if (!panel) return;
    if (panel.tagName && panel.tagName.toLowerCase() === 'details') {
      panel.open = true;
    } else {
      panel.hidden = false;
    }
    var launch = document.querySelector('[data-terminal-launch="' + panel.id + '"]');
    if (launch) launch.classList.add('is-open');
    var input = panel.querySelector('[data-terminal-input]');
    window.setTimeout(function () {
      panel.scrollIntoView({ behavior: "smooth", block: "start" });
      if (input && !input.readOnly) input.focus({ preventScroll: true });
    }, 20);
  }

  function setupTerminalLaunchers() {
    document.querySelectorAll('[data-terminal-open]').forEach(function (button) {
      button.addEventListener('click', function () {
        openLessonTerminal(document.getElementById(button.getAttribute('data-terminal-open')));
      });
    });

    document.querySelectorAll('[data-terminal]').forEach(function (panel) {
      if (panel.hidden) {
        var launch = document.querySelector('[data-terminal-launch="' + panel.id + '"]');
        if (launch) launch.classList.remove('is-open');
      }
      if (!(panel.tagName && panel.tagName.toLowerCase() === 'details')) return;
      panel.addEventListener('toggle', function () {
        var launch = document.querySelector('[data-terminal-launch="' + panel.id + '"]');
        if (launch) launch.classList.toggle('is-open', panel.open);
      });
    });

    document.addEventListener('keydown', function (event) {
      if (!event.ctrlKey || event.key !== 'Enter') return;
      var target = event.target;
      var tagName = target && target.tagName ? target.tagName.toLowerCase() : '';
      if (tagName === 'textarea' || tagName === 'input' || tagName === 'select' || (target && target.isContentEditable)) return;
      var terminal = document.querySelector('[data-terminal]');
      if (!terminal) return;
      event.preventDefault();
      openLessonTerminal(terminal);
    });
  }

  function formatTerminalRun(run) {
    var header = "$ " + (run.normalized_command || run.command_text || "");
    var output = run.stdout_text || "";
    var error = run.stderr_text || "";
    var footer = run.exit_code !== null && run.exit_code !== undefined ? "[exit " + run.exit_code + "]" : "";
    return [header, output, error ? "stderr:\n" + error : "", footer].filter(Boolean).join("\n");
  }

  function renderTerminalHistory(output, runs) {
    if (!output) return;
    if (!runs || !runs.length) {
      output.textContent = "";
      return;
    }
    output.textContent = runs.map(formatTerminalRun).join("\n\n");
    output.scrollTop = output.scrollHeight;
  }

  function setupLessonTerminals() {
    document.querySelectorAll("[data-terminal]").forEach(function (panel) {
      var lessonKey = panel.getAttribute("data-terminal-lesson");
      var input = panel.querySelector("[data-terminal-input]");
      var form = panel.querySelector("[data-terminal-form]");
      var output = panel.querySelector("[data-terminal-output]");
      var status = panel.querySelector("[data-terminal-status]");
      if (!lessonKey || !input || !form || !output) return;
      var visibleRuns = [];

      function setStatus(value) {
        if (status) status.textContent = value;
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
              visibleRuns.push(data.run);
              renderTerminalHistory(output, visibleRuns);
              setStatus(data.run.status || "completed");
            } else {
              setStatus("error");
            }
          })
          .catch(function () { setStatus("network error"); });
      }

      var presetSelector = '[data-terminal-command][data-terminal-target="' + panel.id + '"], #' + panel.id + ' [data-terminal-command]:not([data-terminal-target])';
      document.querySelectorAll(presetSelector).forEach(function (button) {
        button.addEventListener("click", function () {
          if (panel.hidden) openLessonTerminal(panel);
          runCommand(button.getAttribute("data-terminal-command"));
        });
      });

      form.addEventListener("submit", function (event) {
        event.preventDefault();
        runCommand();
      });

      renderTerminalHistory(output, visibleRuns);
    });
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function setupMotionPolish() {
    var disableMotion = prefersReducedMotion() || window.innerWidth < 980;
    if (disableMotion) return;

    var interactiveCards = document.querySelectorAll(
      ".dashboard-context-strip, .lms-summary-card, .module-card, .lesson-page__task-stack .task-panel, .lesson-page--simple .lesson-side-panel, .lesson-page--simple .lesson-nav-panel--main"
    );

    interactiveCards.forEach(function (card) {
      card.addEventListener("mousemove", function (event) {
        var rect = card.getBoundingClientRect();
        var relativeX = (event.clientX - rect.left) / rect.width - 0.5;
        var relativeY = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--mx", relativeX.toFixed(3));
        card.style.setProperty("--my", relativeY.toFixed(3));
        card.style.transform = "translateY(-1px)";
      });

      card.addEventListener("mouseleave", function () {
        card.style.transform = "";
        card.style.removeProperty("--mx");
        card.style.removeProperty("--my");
      });
    });
  }

  function setupAmbientCanvas() {
    if (prefersReducedMotion() || window.innerWidth < 1100) return;
    if (!window.HTMLCanvasElement) return;

    var host =
      document.querySelector(".course-pane") ||
      document.querySelector(".lesson-page__main") ||
      document.querySelector(".recap-pane");

    if (!host) return;

    var canvas = document.createElement("canvas");
    canvas.className = "ambient-canvas";
    canvas.setAttribute("aria-hidden", "true");
    host.prepend(canvas);

    var context = canvas.getContext("2d", { alpha: true });
    if (!context) {
      canvas.remove();
      return;
    }

    var particles = [];
    var maxParticles = 16;
    var rafId = null;
    var resizeObserver = null;
    var running = true;

    function makeParticle(width, height) {
      var speed = 0.04 + Math.random() * 0.14;
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        r: 36 + Math.random() * 78,
        dx: speed,
        dy: speed * (Math.random() > 0.5 ? 1 : -1) * 0.35,
        alpha: 0.02 + Math.random() * 0.05,
      };
    }

    function syncSize() {
      var rect = host.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 1.7);
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
      canvas.style.width = Math.floor(rect.width) + "px";
      canvas.style.height = Math.floor(rect.height) + "px";
      context.setTransform(dpr, 0, 0, dpr, 0, 0);

      particles = [];
      var areaFactor = Math.max(1, Math.floor((rect.width * rect.height) / 180000));
      var count = Math.min(maxParticles, 8 + areaFactor * 2);
      for (var i = 0; i < count; i += 1) {
        particles.push(makeParticle(rect.width, rect.height));
      }
    }

    function draw() {
      if (!running) return;
      var width = canvas.width / Math.min(window.devicePixelRatio || 1, 1.7);
      var height = canvas.height / Math.min(window.devicePixelRatio || 1, 1.7);
      context.clearRect(0, 0, width, height);

      particles.forEach(function (particle) {
        particle.x += particle.dx;
        particle.y += particle.dy;

        if (particle.x > width + particle.r) particle.x = -particle.r;
        if (particle.y > height + particle.r) particle.y = -particle.r;
        if (particle.y < -particle.r) particle.y = height + particle.r;

        var gradient = context.createRadialGradient(
          particle.x,
          particle.y,
          0,
          particle.x,
          particle.y,
          particle.r
        );
        gradient.addColorStop(0, "rgba(198, 228, 255, " + particle.alpha.toFixed(3) + ")");
        gradient.addColorStop(1, "rgba(198, 228, 255, 0)");

        context.fillStyle = gradient;
        context.beginPath();
        context.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
        context.fill();
      });

      rafId = window.requestAnimationFrame(draw);
    }

    function teardown() {
      running = false;
      if (rafId) window.cancelAnimationFrame(rafId);
      if (resizeObserver) resizeObserver.disconnect();
      window.removeEventListener("beforeunload", teardown);
    }

    if (window.ResizeObserver) {
      resizeObserver = new ResizeObserver(syncSize);
      resizeObserver.observe(host);
    } else {
      window.addEventListener("resize", syncSize);
    }

    window.addEventListener("beforeunload", teardown);
    syncSize();
    draw();
  }

  function setupThemeCustomizer() {
    var panel = document.querySelector("[data-theme-panel]");
    var openButton = document.querySelector("[data-theme-open]");
    var closeButton = document.querySelector("[data-theme-close]");
    var themeSelect = document.querySelector("[data-theme-select]");
    var glassToggle = document.querySelector("[data-glass-toggle]");
    var resetButton = document.querySelector("[data-theme-reset]");
    if (!panel || !openButton || !themeSelect || !glassToggle || !resetButton) return;

    var storageKeys = {
      theme: "personalLms.ui.theme",
      glass: "personalLms.ui.glass",
    };
    var allowedThemes = ["vanilla-dark", "vanilla-light", "lain"];

    function applyState(state) {
      var root = document.documentElement;
      root.dataset.theme = allowedThemes.indexOf(state.theme) >= 0 ? state.theme : "vanilla-dark";
      root.dataset.glass = state.glass ? "on" : "off";
    }

    function loadState() {
      var storedTheme = localStorage.getItem(storageKeys.theme) || "vanilla-dark";
      return {
        theme: allowedThemes.indexOf(storedTheme) >= 0 ? storedTheme : "vanilla-dark",
        glass: (localStorage.getItem(storageKeys.glass) || "on") === "on",
      };
    }

    function saveState(state) {
      localStorage.setItem(storageKeys.theme, state.theme);
      localStorage.setItem(storageKeys.glass, state.glass ? "on" : "off");
    }

    function syncControls(state) {
      themeSelect.value = state.theme;
      glassToggle.checked = state.glass;
      glassToggle.nextElementSibling.textContent = state.glass ? "Glass: включен" : "Glass: выключен";
    }

    var state = loadState();
    applyState(state);
    syncControls(state);

    function persistAndApply() {
      applyState(state);
      saveState(state);
      syncControls(state);
    }

    openButton.addEventListener("click", function () {
      panel.hidden = false;
      panel.classList.add("is-open");
    });

    closeButton.addEventListener("click", function () {
      panel.classList.remove("is-open");
      panel.hidden = true;
    });

    themeSelect.addEventListener("change", function () {
      state.theme = themeSelect.value;
      persistAndApply();
    });

    glassToggle.addEventListener("change", function () {
      state.glass = glassToggle.checked;
      persistAndApply();
    });

    resetButton.addEventListener("click", function () {
      state = {
        theme: "vanilla-dark",
        glass: true,
      };
      persistAndApply();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || panel.hidden) return;
      panel.classList.remove("is-open");
      panel.hidden = true;
    });
  }

  function setupAIHelper() {
    var root = document.querySelector("[data-ai-helper]");
    if (!root) return;
    var launcher = root.querySelector("[data-ai-launcher]");
    var panel = root.querySelector("[data-ai-panel]");
    var closeButton = root.querySelector("[data-ai-close]");
    var clearButton = root.querySelector("[data-ai-clear]");
    var statusNode = root.querySelector("[data-ai-status]");
    var dotNode = root.querySelector("[data-ai-dot]");
    var contextNode = root.querySelector("[data-ai-context]");
    var historyNode = root.querySelector("[data-ai-history]");
    var form = root.querySelector("[data-ai-form]");
    var textarea = form ? form.querySelector("textarea[name='message']") : null;
    var socraticToggle = root.querySelector("[data-ai-socratic]");
    var quickActions = root.querySelectorAll("[data-ai-quick]");
    var path = root.getAttribute("data-ai-path") || window.location.pathname;

    if (!launcher || !panel || !closeButton || !historyNode || !form || !textarea) return;
    panel.hidden = true;
    launcher.setAttribute("aria-expanded", "false");

    function setStatus(value) {
      if (!statusNode) return;
      statusNode.textContent = value;
      if (dotNode) dotNode.classList.toggle("is-thinking", value === "thinking");
      launcher.classList.toggle("is-thinking", value === "thinking");
    }

    function renderMessages(messages) {
      historyNode.innerHTML = "";
      if (!messages || !messages.length) {
        historyNode.innerHTML = "<p class='lain-helper__empty'>История пуста для этого контекста.</p>";
        return;
      }
      messages.forEach(function (message) {
        var node = document.createElement("article");
        node.className = "lain-helper__msg lain-helper__msg--" + message.role;
        node.textContent = message.text || "";
        historyNode.appendChild(node);
      });
      historyNode.scrollTop = historyNode.scrollHeight;
    }

    function loadHistory() {
      fetch("/api/ai-helper/history", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ path: path })
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          if (contextNode && data.context_label) contextNode.textContent = data.context_label;
          setStatus(data.online ? "online" : "offline");
          renderMessages(data.messages || []);
        })
        .catch(function () {
          setStatus("offline");
        });
    }

    var closeTimer = null;

    function openPanel() {
      if (closeTimer) {
        window.clearTimeout(closeTimer);
        closeTimer = null;
      }
      panel.hidden = false;
      window.requestAnimationFrame(function () {
        panel.classList.add("is-open");
      });
      launcher.setAttribute("aria-expanded", "true");
      loadHistory();
    }

    function closePanel() {
      panel.classList.remove("is-open");
      closeTimer = window.setTimeout(function () {
        panel.hidden = true;
      }, 160);
      launcher.setAttribute("aria-expanded", "false");
    }

    launcher.addEventListener("click", function () {
      if (panel.hidden) openPanel();
      else closePanel();
    });
    closeButton.addEventListener("click", closePanel);

    clearButton.addEventListener("click", function () {
      fetch("/api/ai-helper/clear", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ path: path })
      }).then(function () {
        renderMessages([]);
      });
    });

    quickActions.forEach(function (button) {
      button.addEventListener("click", function () {
        textarea.value = button.getAttribute("data-ai-quick") || "";
        textarea.focus();
      });
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var message = textarea.value.trim();
      if (!message) return;
      setStatus("thinking");
      fetch("/api/ai-helper/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({
          path: path,
          message: message,
          socratic_mode: !!(socraticToggle && socraticToggle.checked)
        })
      })
        .then(function (response) { return response.json(); })
        .then(function () {
          textarea.value = "";
          loadHistory();
        })
        .catch(function () {
          setStatus("offline");
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.dataset.appReady = "true";
    updateWorldClocks();
    setupSingleAccordions();
    setupTabs();
    setupTerminalLaunchers();
    setupLessonTerminals();
    setupMotionPolish();
    setupAmbientCanvas();
    setupThemeCustomizer();
    setupAIHelper();
    window.setInterval(updateWorldClocks, 30000);
  });
})();
