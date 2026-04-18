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

  function setupAIHelper() {
    var root = document.querySelector("[data-ai-helper]");
    if (!root) return;

    var launcher = root.querySelector("[data-ai-launcher]");
    var panel = root.querySelector("[data-ai-panel]");
    var closeButton = root.querySelector("[data-ai-close]");
    var messages = root.querySelector("[data-ai-messages]");
    var emptyState = root.querySelector("[data-ai-empty]");
    var form = root.querySelector("[data-ai-form]");
    var input = root.querySelector("[data-ai-input]");
    var quickActions = root.querySelector("[data-ai-quick-actions]");
    var endpoint = root.getAttribute("data-ai-endpoint") || "/api/ai/helper";
    var historyEndpoint = root.getAttribute("data-ai-history-endpoint") || "";
    var lessonKey = (root.getAttribute("data-ai-lesson") || "").trim();
    if (!launcher || !panel || !messages || !form || !input) return;

    var isBusy = false;
    var isHistoryLoading = false;
    var loadedHistoryForLesson = "";
    var renderedInteractionIds = {};

    var actionMessages = {
      explain_lesson: "Объясни текущий урок: что важно понять перед практикой?",
      help_start: "Помоги начать: какой первый маленький шаг сделать прямо сейчас?",
      stuck_help: "Я застрял. Помоги выбрать следующий шаг, чтобы вернуться к выполнению.",
      submission_hint: "Проверь мой ответ и подскажи, что улучшить перед отправкой."
    };

    function readSubmissionDraft() {
      var textDraft = document.getElementById("content_text");
      var linkDraft = document.getElementById("content_link");
      if (textDraft && textDraft.value && textDraft.value.trim()) return textDraft.value.trim();
      if (linkDraft && linkDraft.value && linkDraft.value.trim()) return linkDraft.value.trim();
      return "";
    }

    function readStuckDraft() {
      var stuckDraft = document.getElementById("stuck_note");
      if (!stuckDraft || !stuckDraft.value) return "";
      return stuckDraft.value.trim();
    }

    function normalizeInteractionId(value) {
      var parsed = Number(value);
      if (!parsed || parsed <= 0) return "";
      return String(parsed);
    }

    function rememberInteraction(interactionId) {
      var normalized = normalizeInteractionId(interactionId);
      if (!normalized) return;
      renderedInteractionIds[normalized] = true;
    }

    function hasInteraction(interactionId) {
      var normalized = normalizeInteractionId(interactionId);
      if (!normalized) return false;
      return renderedInteractionIds[normalized] === true;
    }

    function setEmptyState(visible) {
      if (!emptyState) return;
      emptyState.hidden = !visible;
    }

    function refreshEmptyState() {
      setEmptyState(messages.querySelectorAll(".lain-chat__message").length === 0);
    }

    function setBusy(nextBusy) {
      isBusy = nextBusy;
      root.classList.toggle("is-loading", nextBusy);
      form.querySelectorAll("input, button").forEach(function (node) {
        node.disabled = nextBusy;
      });
      if (quickActions) {
        quickActions.querySelectorAll("button").forEach(function (node) {
          node.disabled = nextBusy;
        });
      }
    }

    function appendMessage(role, text, className, interactionId) {
      if (!text) return null;
      var node = document.createElement("article");
      node.className = "lain-chat__message lain-chat__message--" + role + (className ? " " + className : "");
      node.textContent = text;
      if (interactionId) {
        node.setAttribute("data-ai-interaction-id", String(interactionId));
      }
      messages.appendChild(node);
      refreshEmptyState();
      messages.scrollTop = messages.scrollHeight;
      return node;
    }

    function removeNode(node) {
      if (!node || !node.parentNode) return;
      node.parentNode.removeChild(node);
      refreshEmptyState();
    }

    function openPanel() {
      panel.hidden = false;
      root.classList.add("is-open");
      loadHistory();
      window.setTimeout(function () {
        input.focus({ preventScroll: true });
      }, 20);
    }

    function closePanel() {
      panel.hidden = true;
      root.classList.remove("is-open");
    }

    function appendHistoryItem(item) {
      if (!item || hasInteraction(item.id)) return;

      var normalizedId = normalizeInteractionId(item.id);
      var userMessage = item.user_message ? String(item.user_message).trim() : "";
      var assistantMessage = item.assistant_message ? String(item.assistant_message).trim() : "";

      if (userMessage) appendMessage("user", userMessage, "", normalizedId);
      if (assistantMessage) appendMessage("assistant", assistantMessage, "", normalizedId);
      rememberInteraction(normalizedId);
    }

    function loadHistory() {
      if (!historyEndpoint || !lessonKey || isHistoryLoading || loadedHistoryForLesson === lessonKey) return;

      isHistoryLoading = true;
      var loading = appendMessage("assistant", "Загружаю недавнюю историю...", "lain-chat__message--loading");

      fetch(
        historyEndpoint + "?lesson_key=" + encodeURIComponent(lessonKey) + "&limit=12",
        { headers: { "Accept": "application/json" } }
      )
        .then(function (response) {
          if (!response.ok) throw new Error("History request failed");
          return response.json();
        })
        .then(function (payload) {
          removeNode(loading);
          var items = payload && Array.isArray(payload.items) ? payload.items : [];
          items.forEach(function (item) {
            appendHistoryItem(item);
          });
          loadedHistoryForLesson = lessonKey;
        })
        .catch(function () {
          removeNode(loading);
          appendMessage("assistant", "Не удалось загрузить историю Lain. Можно продолжить без нее.");
        })
        .finally(function () {
          isHistoryLoading = false;
        });
    }

    function sendRequest(mode, messageText, submissionDraft) {
      if (isBusy) return;

      var trimmedMessage = (messageText || "").trim();
      if (mode === "free_question" && !trimmedMessage) return;
      if (!lessonKey) {
        appendMessage("assistant", "Сначала открой урок, чтобы я могла помочь в контексте шага.");
        return;
      }

      var userNode = trimmedMessage ? appendMessage("user", trimmedMessage) : null;
      var loading = appendMessage("assistant", "Lain анализирует текущий шаг...", "lain-chat__message--loading");
      setBusy(true);

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({
          lesson_key: lessonKey,
          mode: mode,
          message: trimmedMessage,
          submission_draft: (submissionDraft || "").trim() || null
        })
      })
        .then(function (response) {
          if (!response.ok) {
            return response.json().then(function (payload) {
              var detail = payload && payload.detail ? String(payload.detail) : "AI helper request failed";
              throw new Error(detail);
            });
          }
          return response.json();
        })
        .then(function (data) {
          var assistantText = data.assistant_message || "Сейчас не смогла ответить по этому шагу.";
          var interactionId = normalizeInteractionId(data.interaction_id);
          if (loading) {
            loading.textContent = assistantText;
            loading.classList.remove("lain-chat__message--loading");
            if (interactionId) loading.setAttribute("data-ai-interaction-id", interactionId);
          } else {
            appendMessage("assistant", assistantText, "", interactionId);
          }
          if (interactionId) {
            rememberInteraction(interactionId);
            if (userNode) userNode.setAttribute("data-ai-interaction-id", interactionId);
          }
        })
        .catch(function () {
          if (loading) {
            loading.textContent = "Ошибка соединения с Lain. Попробуй еще раз через минуту.";
            loading.classList.remove("lain-chat__message--loading");
          } else {
            appendMessage("assistant", "Ошибка соединения с Lain. Попробуй еще раз через минуту.");
          }
        })
        .finally(function () {
          setBusy(false);
          input.focus({ preventScroll: true });
        });
    }

    launcher.addEventListener("click", function () {
      if (panel.hidden) {
        openPanel();
      } else {
        closePanel();
      }
    });

    if (closeButton) {
      closeButton.addEventListener("click", function () {
        closePanel();
      });
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var outgoing = input.value || "";
      input.value = "";
      sendRequest("free_question", outgoing, "");
    });

    if (quickActions) {
      quickActions.querySelectorAll("[data-ai-mode]").forEach(function (button) {
        button.addEventListener("click", function () {
          openPanel();
          var mode = button.getAttribute("data-ai-mode");
          var message = actionMessages[mode] || "";
          if (mode === "stuck_help") {
            var stuckDraft = readStuckDraft();
            if (stuckDraft) message = message + "\nКонтекст блокера: " + stuckDraft;
          }
          var draft = mode === "submission_hint" ? readSubmissionDraft() : "";
          sendRequest(mode, message, draft);
        });
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) closePanel();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.documentElement.dataset.appReady = "true";
    updateWorldClocks();
    setupSingleAccordions();
    setupTabs();
    setupTerminalLaunchers();
    setupLessonTerminals();
    setupAIHelper();
    window.setInterval(updateWorldClocks, 30000);
  });
})();
