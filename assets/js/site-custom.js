/* Personal website behaviors carried over from the old custom Minimal Mistakes bundle.
 * Theme JavaScript (including heading permalink creation) now comes from remote_theme.
 */
(function () {
  "use strict";

  function updateStickySidebar() {
    var sidebar = document.querySelector(".sidebar");
    if (!sidebar) return;

    var authorButton = document.querySelector(".author__urls-wrapper button");
    var buttonVisible = authorButton &&
      window.getComputedStyle(authorButton).display !== "none" &&
      authorButton.getClientRects().length > 0;

    // Preserve the previous responsive behavior: the sidebar sticks only when
    // its author-links dropdown is hidden (or above 1024px without a dropdown).
    var shouldStick = authorButton ? !buttonVisible : window.innerWidth > 1024;
    sidebar.classList.toggle("sticky", shouldStick);
  }

  function restoreHeadingLinkStyle() {
    // The upstream bundle creates accessible heading permalink anchors.
    // Keep the site's original icon presentation without creating duplicates.
    document.querySelectorAll(".page__content .header-link").forEach(function (link) {
      var headingText = Array.from(link.parentElement.childNodes)
        .filter(function (node) { return node !== link; })
        .map(function (node) { return node.textContent; })
        .join("").trim();
      link.innerHTML = '<span class="sr-only">Permalink</span><i class="fas fa-link" aria-hidden="true"></i>';
      link.setAttribute("aria-label", "Permalink to " + headingText);
    });
  }

  function initializeThemeSwitcher() {
    var control = document.getElementById("site-theme-toggle");
    var lightCSS = document.getElementById("site-css-light");
    var darkCSS = document.getElementById("site-css-dark");
    if (!control || !lightCSS || !darkCSS) return;

    var icon = control.querySelector("i");
    var systemPreference = window.matchMedia("(prefers-color-scheme: dark)");
    var modes = ["system", "light", "dark"];
    var icons = {
      system: "fas fa-desktop",
      light: "fas fa-sun",
      dark: "fas fa-moon"
    };
    var labels = { system: "System", light: "Light", dark: "Dark" };

    function applyTheme(preference) {
      if (modes.indexOf(preference) === -1) preference = "system";
      var isDark = preference === "dark" ||
        (preference === "system" && systemPreference.matches);
      var theme = isDark ? "dark" : "light";

      // Enable the next stylesheet before disabling the previous one.
      if (isDark) {
        darkCSS.media = "all";
        lightCSS.media = "not all";
      } else {
        lightCSS.media = "all";
        darkCSS.media = "not all";
      }

      document.documentElement.setAttribute("data-theme", theme);
      document.documentElement.setAttribute("data-theme-preference", preference);

      if (icon) icon.className = icons[preference];
      var nextPreference = modes[(modes.indexOf(preference) + 1) % modes.length];
      control.setAttribute("aria-label", "Appearance: " + labels[preference] +
        ". Activate to switch to " + labels[nextPreference] + ".");
      control.title = "Appearance: " + labels[preference] +
        " (click for " + labels[nextPreference] + ")";

      var browserChromeColor = document.querySelector('meta[name="theme-color"]');
      if (browserChromeColor) {
        browserChromeColor.setAttribute("content", isDark ? "#252a34" : "#ffffff");
      }
    }

    var initialPreference = document.documentElement.getAttribute("data-theme-preference") || "system";
    applyTheme(initialPreference);

    // Share the same theme controller with the command palette. Both controls
    // update the saved preference, stylesheets, and masthead icon together.
    window.EJSungTheme = {
      setPreference: function (preference) {
        if (modes.indexOf(preference) === -1) return;
        try { localStorage.setItem("ejsung-theme", preference); } catch (error) { /* optional */ }
        applyTheme(preference);
      },
      getPreference: function () {
        return document.documentElement.getAttribute("data-theme-preference") || "system";
      }
    };

    // Clicking cycles System -> Light -> Dark -> System.
    control.addEventListener("click", function () {
      var preference = document.documentElement.getAttribute("data-theme-preference") || "system";
      var nextPreference = modes[(modes.indexOf(preference) + 1) % modes.length];
      window.EJSungTheme.setPreference(nextPreference);
    });

    systemPreference.addEventListener("change", function () {
      if (document.documentElement.getAttribute("data-theme-preference") === "system") {
        applyTheme("system");
      }
    });
  }

  function initialize() {
    updateStickySidebar();
    restoreHeadingLinkStyle();
    initializeThemeSwitcher();
    window.addEventListener("resize", updateStickySidebar);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
