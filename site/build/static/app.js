/**
 * Sidebar procedure filter (header search + tactic/author/ttp filters).
 * Search only affects #proc-list in the sidebar — not main content.
 */
(function () {
  function norm(s) {
    return (s || "").toString().trim().toLowerCase();
  }

  function applyProcFilter() {
    var q = norm(document.getElementById("proc-search") && document.getElementById("proc-search").value);
    var tactic = norm(document.getElementById("filter-tactic") && document.getElementById("filter-tactic").value);
    var author = norm(document.getElementById("filter-author") && document.getElementById("filter-author").value);
    var ttp = norm(document.getElementById("filter-ttp") && document.getElementById("filter-ttp").value);
    var visible = 0;
    var total = 0;

    document.querySelectorAll("#proc-list a[data-name]").forEach(function (a) {
      total += 1;
      var ok = true;
      if (tactic && norm(a.getAttribute("data-tactic")) !== tactic) ok = false;
      if (author && norm(a.getAttribute("data-author")).indexOf(author) === -1) ok = false;
      if (ttp && norm(a.getAttribute("data-ttp")).indexOf(ttp) === -1) ok = false;
      if (q) {
        var blob =
          norm(a.getAttribute("data-name")) +
          " " +
          norm(a.getAttribute("data-intent")) +
          " " +
          norm(a.getAttribute("data-tactic")) +
          " " +
          norm(a.getAttribute("data-author")) +
          " " +
          norm(a.getAttribute("data-ttp"));
        if (blob.indexOf(q) === -1) ok = false;
      }
      var li = a.closest("li");
      if (li) li.classList.toggle("hidden", !ok);
      if (ok) visible += 1;
    });

    var countEl = document.getElementById("proc-search-count");
    if (countEl) {
      var active = q || tactic || author || ttp;
      if (active && visible !== total) {
        countEl.textContent = visible + " / " + total;
        countEl.classList.remove("hidden");
      } else {
        countEl.textContent = "";
        countEl.classList.add("hidden");
      }
    }
  }

  function initProcViewTabs() {
    var tabs = document.querySelectorAll("[data-proc-view]");
    if (!tabs.length) return;

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var view = tab.getAttribute("data-proc-view");
        tabs.forEach(function (t) {
          var on = t === tab;
          t.classList.toggle("active", on);
          t.setAttribute("aria-selected", on ? "true" : "false");
        });
        document.querySelectorAll(".code-panel").forEach(function (panel) {
          panel.classList.add("hidden");
        });
        var target = document.getElementById("proc-view-" + view);
        if (target) target.classList.remove("hidden");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["proc-search", "filter-tactic", "filter-author", "filter-ttp"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener("input", applyProcFilter);
        el.addEventListener("change", applyProcFilter);
      }
    });
    applyProcFilter();
    initProcViewTabs();
  });
})();
