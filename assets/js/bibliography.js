/* Copy BibTeX from Jekyll Scholar records. No additional dependencies. */
(function () {
  "use strict";

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    // Fallback for older browsers and localhost contexts without Clipboard API.
    var field = document.createElement("textarea");
    field.value = value;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    var ok = document.execCommand("copy");
    field.remove();
    if (!ok) throw new Error("Clipboard unavailable");
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-copy-bibtex]");
    if (!button) return;

    var disclosure = button.closest(".publication-tools__details--bibtex");
    if (!disclosure) return;

    var code = disclosure.querySelector(".publication-tools__bibtex code");
    var status = disclosure.querySelector(".publication-tools__copy-status");
    if (!code || !status) return;

    button.disabled = true;
    copyText(code.textContent.trim())
      .then(function () { status.textContent = "Copied BibTeX to clipboard."; })
      .catch(function () { status.textContent = "Copy failed. Please select the BibTeX text manually."; })
      .finally(function () { button.disabled = false; });
  });
})();
