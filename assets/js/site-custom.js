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

  function initialize() {
    updateStickySidebar();
    restoreHeadingLinkStyle();
    window.addEventListener("resize", updateStickySidebar);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
