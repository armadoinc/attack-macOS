/**
 * Sidebar filters, header search dropdown, procedure view tabs.
 */
(function () {
  function norm(s) {
    return (s || "").toString().trim().toLowerCase();
  }

  function loadSearchIndex() {
    var el = document.getElementById("proc-search-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent || "[]");
    } catch (e) {
      return [];
    }
  }

  var searchIndex = [];

  function matchProcedure(item, q, tactic, author, ttp) {
    if (tactic && norm(item.tactic) !== tactic) return false;
    if (author && norm(item.author || "").indexOf(author) === -1) return false;
    if (ttp && norm(item.ttp).indexOf(ttp) === -1) return false;
    if (q) {
      var blob =
        norm(item.name) +
        " " +
        norm(item.intent) +
        " " +
        norm(item.tactic) +
        " " +
        norm(item.ttp) +
        " " +
        norm(item.author);
      if (blob.indexOf(q) === -1) return false;
    }
    return true;
  }

  function applySidebarFilter() {
    var q = norm(document.getElementById("proc-search") && document.getElementById("proc-search").value);
    var tactic = norm(document.getElementById("filter-tactic") && document.getElementById("filter-tactic").value);
    var author = norm(document.getElementById("filter-author") && document.getElementById("filter-author").value);
    var ttp = norm(document.getElementById("filter-ttp") && document.getElementById("filter-ttp").value);

    document.querySelectorAll("#proc-list a[data-name]").forEach(function (a) {
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
    });
  }

  function renderSearchDropdown() {
    var input = document.getElementById("proc-search");
    var dropdown = document.getElementById("proc-search-dropdown");
    if (!input || !dropdown) return;

    var q = norm(input.value);
    var tactic = norm(document.getElementById("filter-tactic") && document.getElementById("filter-tactic").value);
    var author = norm(document.getElementById("filter-author") && document.getElementById("filter-author").value);
    var ttp = norm(document.getElementById("filter-ttp") && document.getElementById("filter-ttp").value);

    if (!q) {
      dropdown.classList.add("hidden");
      dropdown.innerHTML = "";
      input.setAttribute("aria-expanded", "false");
      return;
    }

    var matches = searchIndex.filter(function (item) {
      return matchProcedure(item, q, tactic, author, ttp);
    }).slice(0, 12);

    if (!matches.length) {
      dropdown.innerHTML = '<p class="search-empty">No matching procedures</p>';
    } else {
      dropdown.innerHTML = matches
        .map(function (item) {
          var meta = [item.tactic, item.ttp].filter(Boolean).join(" · ");
          return (
            '<a class="search-hit" role="option" href="' +
            item.href +
            '"><span class="search-hit-name">' +
            item.name +
            "</span>" +
            (meta ? '<span class="search-hit-meta">' + meta + "</span>" : "") +
            "</a>"
          );
        })
        .join("");
    }

    dropdown.classList.remove("hidden");
    input.setAttribute("aria-expanded", "true");
  }

  function initSearchDropdown() {
    var input = document.getElementById("proc-search");
    var dropdown = document.getElementById("proc-search-dropdown");
    if (!input || !dropdown) return;

    input.addEventListener("input", function () {
      applySidebarFilter();
      renderSearchDropdown();
    });

    input.addEventListener("focus", renderSearchDropdown);

    document.addEventListener("click", function (e) {
      if (!dropdown.contains(e.target) && e.target !== input) {
        dropdown.classList.add("hidden");
        input.setAttribute("aria-expanded", "false");
      }
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        dropdown.classList.add("hidden");
        input.setAttribute("aria-expanded", "false");
        input.blur();
      }
    });
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
    searchIndex = loadSearchIndex();
    ["filter-tactic", "filter-author", "filter-ttp"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener("input", function () {
          applySidebarFilter();
          renderSearchDropdown();
        });
        el.addEventListener("change", function () {
          applySidebarFilter();
          renderSearchDropdown();
        });
      }
    });
    applySidebarFilter();
    initSearchDropdown();
    initProcViewTabs();
  });
})();
