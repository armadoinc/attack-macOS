/**
 * Client-side filter for procedure list (browse + procedure layout sidebars).
 * Expects #proc-search, #filter-tactic, #filter-author, #filter-ttp,
 * and .proc-list a[data-tactic][data-author][data-ttp][data-name]
 */
(function () {
  function norm(s) {
    return (s || "").toString().trim().toLowerCase();
  }

  function apply() {
    var q = norm(document.getElementById("proc-search") && document.getElementById("proc-search").value);
    var tactic = norm(document.getElementById("filter-tactic") && document.getElementById("filter-tactic").value);
    var author = norm(document.getElementById("filter-author") && document.getElementById("filter-author").value);
    var ttp = norm(document.getElementById("filter-ttp") && document.getElementById("filter-ttp").value);

    document.querySelectorAll(".proc-list a[data-name]").forEach(function (a) {
      var ok = true;
      if (tactic && norm(a.getAttribute("data-tactic")) !== tactic) ok = false;
      if (author && norm(a.getAttribute("data-author")).indexOf(author) === -1) ok = false;
      if (ttp && norm(a.getAttribute("data-ttp")).indexOf(ttp) === -1) ok = false;
      if (q) {
        var blob =
          norm(a.getAttribute("data-name")) +
          " " +
          norm(a.getAttribute("data-tactic")) +
          " " +
          norm(a.getAttribute("data-author")) +
          " " +
          norm(a.getAttribute("data-ttp")) +
          " " +
          norm(a.textContent);
        if (blob.indexOf(q) === -1) ok = false;
      }
      var li = a.closest("li");
      if (li) li.classList.toggle("hidden", !ok);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["proc-search", "filter-tactic", "filter-author", "filter-ttp"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.addEventListener("input", apply);
        el.addEventListener("change", apply);
      }
    });
    apply();
  });
})();
