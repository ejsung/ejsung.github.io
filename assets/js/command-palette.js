/* Fast, accessible command palette built on the website's EXISTING Lunr index.
 * No new browser libraries, services, or duplicate search index.
 */
(function () {
  "use strict";

  var root = document.getElementById("command-palette");
  var configElement = document.getElementById("command-palette-config");
  if (!root || !configElement) return;

  var config;
  try {
    config = JSON.parse(configElement.textContent);
  } catch (error) {
    console.warn("Command palette configuration is invalid", error);
    return;
  }

  var input = document.getElementById("command-palette-input");
  var results = document.getElementById("command-palette-results");
  var status = document.getElementById("command-palette-status");
  var closeButton = root.querySelector(".command-palette__close");
  var searchButton = document.querySelector(".search__toggle");
  var choices = [];
  var currentIndex = 0;
  var formerFocus = null;
  var debounceTimer = null;
  var lastQuery = "";
  var limit = 12;

  function normalize(value) {
    return String(value || "").normalize("NFKD").toLocaleLowerCase().trim();
  }

  function safeUrl(value) {
    try {
      var url = new URL(value, document.baseURI);
      return url.protocol === "http:" || url.protocol === "https:" ? url : null;
    } catch (error) {
      return null;
    }
  }

  function navigate(url) {
    var dest = safeUrl(url);
    if (!dest) return;
    if (dest.origin !== window.location.origin) {
      window.open(dest.href, "_blank", "noopener,noreferrer");
      close();
    } else {
      window.location.assign(dest.href);
    }
  }

  function say(message) {
    status.textContent = message;
  }

  function clipboardFallback(value) {
    var textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    var success = document.execCommand("copy");
    textarea.remove();
    if (!success) throw new Error("Copy was blocked");
  }

  function copyText(value, description) {
    var operation = navigator.clipboard && window.isSecureContext
      ? navigator.clipboard.writeText(value)
      : Promise.resolve().then(function () { clipboardFallback(value); });
    operation.then(function () {
      say(description + " copied to clipboard.");
      input.focus();
    }).catch(function () {
      try {
        clipboardFallback(value);
        say(description + " copied to clipboard.");
      } catch (error) {
        say("Clipboard unavailable. " + value);
      }
    });
  }

  function currentTheme() {
    return window.EJSungTheme && window.EJSungTheme.getPreference
      ? window.EJSungTheme.getPreference()
      : document.documentElement.getAttribute("data-theme-preference") || "system";
  }

  function setTheme(value) {
    if (window.EJSungTheme && window.EJSungTheme.setPreference) {
      window.EJSungTheme.setPreference(value);
      say("Appearance changed to " + value + ".");
      render();
    } else {
      say("Appearance switcher is not available on this page.");
    }
  }

  var actions = (config.pages || []).map(function (page) {
    return {
      title: page.title,
      detail: "Go to " + page.title,
      keywords: page.title + " page navigate go",
      type: "page",
      icon: "fa-file-alt",
      execute: function () { navigate(page.url); }
    };
  });

  actions = actions.concat([
    {
      title: "Copy page link",
      detail: "Copy the URL of this page",
      keywords: "copy current page link url share",
      type: "action", icon: "fa-link",
      execute: function () { copyText(window.location.href, "Page link"); }
    }
  ]);

  [
    { title: "Use System appearance", mode: "system", icon: "fa-desktop", keywords: "auto system preference theme appearance" },
    { title: "Switch to Light mode", mode: "light", icon: "fa-sun", keywords: "light theme day sun brightness appearance" },
    { title: "Switch to Dark mode", mode: "dark", icon: "fa-moon", keywords: "dark theme night moon appearance" }
  ].forEach(function (item) {
    actions.push({
      title: item.title,
      detail: "Appearance · " + item.mode,
      keywords: item.keywords,
      type: "action", icon: item.icon,
      mode: item.mode,
      execute: function () { setTheme(item.mode); }
    });
  });

  function scoreAction(action, query) {
    if (!query) return 1;
    var title = normalize(action.title);
    var haystack = normalize(action.title + " " + action.keywords + " " + action.detail);
    var terms = query.split(/\s+/).filter(Boolean);
    if (!terms.every(function (word) { return haystack.includes(word); })) return 0;
    return title === query ? 100 : title.startsWith(query) ? 50 : title.includes(query) ? 30 : 10;
  }

  function findActions(query, mode) {
    if (mode === "publication" || mode === "tag") return [];
    return actions.map(function (action) {
      return { action: action, score: scoreAction(action, query) };
    }).filter(function (match) {
      return match.score > 0;
    }).sort(function (a, b) {
      return b.score - a.score;
    }).map(function (match) { return match.action; });
  }

  function buildLunrResults(query, mode) {
    // 'idx' and 'store' are provided by the existing Minimal Mistakes Lunr scripts.
    if (typeof window.idx === "undefined" ||
        typeof window.store === "undefined" ||
        typeof window.lunr === "undefined" || !query) return [];

    var tokens = query.split(/\s+/).filter(Boolean).slice(0, 6);
    if (!tokens.length) return [];

    var matches;
    try {
      matches = window.idx.query(function (builder) {
        tokens.forEach(function (token) {
          builder.term(token, { fields: ["title"], boost: 50 });
          builder.term(token, { fields: ["tags"], boost: 30 });
          builder.term(token, { fields: ["excerpt"], boost: 4 });
          builder.term(token, {
            usePipeline: false,
            wildcard: window.lunr.Query.wildcard.TRAILING,
            boost: 12
          });
          if (token.length >= 4) {
            builder.term(token, { usePipeline: false, editDistance: 1, boost: 1 });
          }
        });
      });
    } catch (error) {
      return [];
    }

    var seen = new Set();
    var items = [];
    matches.slice(0, 100).forEach(function (match) {
      var doc = window.store[Number(match.ref)];
      if (!doc || !doc.title || !doc.url) return;
      var type = doc.palette_type === "publication" ? "publication" : "page";
      if (mode === "publication" && type !== "publication") return;
      if (mode === "tag") {
        var tags = Array.isArray(doc.tags) ? doc.tags : [];
        if (!tags.some(function (tag) { return normalize(tag).includes(query); })) return;
      }
      var unique = doc.url + "|" + doc.title;
      if (seen.has(unique)) return;
      seen.add(unique);
      items.push({
        title: doc.title,
        detail: type === "publication" ?
          String(doc.year || "Publication") + " · " + String(doc.excerpt || "").slice(0, 115) :
          String(doc.excerpt || "").slice(0, 125),
        type: type,
        icon: type === "publication" ? "fa-book-open" : "fa-file-alt",
        execute: function () { navigate(doc.url); }
      });
    });
    return items;
  }

  function makeOption(choice, index) {
    var li = document.createElement("li");
    li.className = "command-palette__option";
    li.id = "command-palette-option-" + index;
    li.setAttribute("role", "option");
    li.setAttribute("aria-selected", index === currentIndex ? "true" : "false");

    var icon = document.createElement("i");
    icon.className = "fas " + choice.icon;
    icon.setAttribute("aria-hidden", "true");
    li.appendChild(icon);

    var content = document.createElement("span");
    content.className = "command-palette__text";
    var title = document.createElement("span");
    title.className = "command-palette__title";
    title.textContent = choice.title;
    var detail = document.createElement("span");
    detail.className = "command-palette__detail";
    detail.textContent = choice.detail || "";
    content.appendChild(title);
    content.appendChild(detail);
    li.appendChild(content);

    var type = document.createElement("span");
    type.className = "command-palette__type";
    type.textContent = choice.type === "publication" ? "Paper" :
      choice.type === "page" ? "Page" : "Action";
    li.appendChild(type);

    li.addEventListener("mouseenter", function () { select(index); });
    li.addEventListener("mousedown", function (event) { event.preventDefault(); });
    li.addEventListener("click", function () { choice.execute(); });
    return li;
  }

  function select(index) {
    if (!choices.length) return;
    currentIndex = (index + choices.length) % choices.length;
    Array.from(results.children).forEach(function (element, i) {
      element.setAttribute("aria-selected", i === currentIndex ? "true" : "false");
    });
    input.setAttribute("aria-activedescendant", "command-palette-option-" + currentIndex);
    var selected = results.children[currentIndex];
    if (selected) selected.scrollIntoView({ block: "nearest" });
  }

  function render() {
    var raw = normalize(input.value);
    var mode = raw.startsWith("#") ? "tag" : raw.startsWith("@") ? "publication" : "all";
    var query = mode === "all" ? raw : raw.slice(1).trim();
    var commands = findActions(query, mode);
    var records = buildLunrResults(query, mode);
    var pages = new Set(commands.filter(function (c) { return c.type === "page"; })
      .map(function (c) { return normalize(c.title); }));
    records = records.filter(function (c) {
      return c.type !== "page" || !pages.has(normalize(c.title));
    });
    // Empty query: show commands immediately, without building/searching an index.
    choices = commands.concat(records).slice(0, limit);
    currentIndex = 0;
    results.replaceChildren();
    if (!choices.length) {
      var empty = document.createElement("li");
      empty.className = "command-palette__empty";
      empty.textContent = query ? "No matches. Try a different term." : "No commands available.";
      empty.setAttribute("role", "presentation");
      results.appendChild(empty);
      input.removeAttribute("aria-activedescendant");
      say("No results.");
      return;
    }
    var fragment = document.createDocumentFragment();
    choices.forEach(function (choice, i) { fragment.appendChild(makeOption(choice, i)); });
    results.appendChild(fragment);
    input.setAttribute("aria-activedescendant", "command-palette-option-0");
    say(choices.length + " results. Use arrow keys to navigate and Enter to select.");
  }

  function open() {
    if (!root.hidden) return;
    formerFocus = document.activeElement;
    root.hidden = false;
    document.body.classList.add("command-palette-open");
    input.value = "";
    lastQuery = "";
    render();
    input.focus();
  }

  function close() {
    if (root.hidden) return;
    root.hidden = true;
    document.body.classList.remove("command-palette-open");
    clearTimeout(debounceTimer);
    if (formerFocus && formerFocus.isConnected && formerFocus.focus) formerFocus.focus();
  }

  // Capture phase prevents Minimal Mistakes' existing click listener from
  // opening its *old* search overlay. The magnifier now opens this palette.
  if (searchButton) {
    searchButton.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      open();
    }, true);
  }

  document.addEventListener("keydown", function (event) {
    var shortcut = (event.metaKey || event.ctrlKey) && !event.altKey &&
      normalize(event.key) === "k";
    if (shortcut) {
      event.preventDefault();
      if (root.hidden) open(); else close();
      return;
    }
    if (root.hidden) return;
    if (event.key === "Escape") {
      event.preventDefault();
      close();
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      select(currentIndex + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      select(currentIndex - 1);
    } else if (event.key === "Enter" && choices.length) {
      event.preventDefault();
      choices[currentIndex].execute();
    } else if (event.key === "Tab") {
      // Only the input and close button are tab stops inside this dialog.
      if (event.shiftKey && document.activeElement === input) {
        event.preventDefault();
        closeButton.focus();
      } else if (!event.shiftKey && document.activeElement === closeButton) {
        event.preventDefault();
        input.focus();
      }
    }
  }, true);

  input.addEventListener("input", function () {
    if (input.value === lastQuery) return;
    lastQuery = input.value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(render, 70);
  });

  root.querySelectorAll("[data-palette-close]").forEach(function (button) {
    button.addEventListener("click", close);
  });
})();
