/* Menu: marca a página atual e fecha com Esc, clique fora ou ao escolher um link */
(function () {
  var m = document.querySelector("details.menu"); if (!m) return;
  var here = location.pathname.split("/").pop() || "index.html";
  m.querySelectorAll(".menu-panel a").forEach(function (a) { if (a.getAttribute("href").split("#")[0] === here && !a.classList.contains("cta")) a.setAttribute("aria-current", "page"); a.addEventListener("click", function () { m.removeAttribute("open"); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") m.removeAttribute("open"); });
  document.addEventListener("click", function (e) { if (m.open && !m.contains(e.target)) m.removeAttribute("open"); });
})();
