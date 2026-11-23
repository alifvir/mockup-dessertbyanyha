(function () {
  var tombol = document.querySelector("[data-nav-tombol]");
  var nav = document.querySelector("[data-nav]");
  if (!tombol || !nav) return;

  function tutup() {
    nav.setAttribute("data-terbuka", "false");
    tombol.setAttribute("aria-expanded", "false");
  }

  tombol.addEventListener("click", function () {
    var terbuka = nav.getAttribute("data-terbuka") === "true";
    nav.setAttribute("data-terbuka", terbuka ? "false" : "true");
    tombol.setAttribute("aria-expanded", terbuka ? "false" : "true");
  });

  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) tutup();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") tutup();
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth > 900) tutup();
  });
})();

(function () {
  var dialog = null;

  function buat() {
    dialog = document.createElement("dialog");
    dialog.className = "zoom";
    var tutup = document.createElement("button");
    tutup.type = "button";
    tutup.className = "zoom__tutup";
    tutup.setAttribute("aria-label", "Tutup foto");
    tutup.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="none" stroke="currentColor" stroke-width="2" d="M6 6l12 12M18 6L6 18"/></svg>';
    var gambar = document.createElement("img");
    gambar.alt = "";
    dialog.append(tutup, gambar);
    document.body.append(dialog);

    tutup.addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
  }

  document.addEventListener("click", function (e) {
    var pemicu = e.target.closest("[data-zoom]");
    if (!pemicu) return;
    if (!dialog) buat();
    var img = dialog.querySelector("img");
    img.src = pemicu.getAttribute("data-zoom");
    img.alt = pemicu.getAttribute("data-zoom-alt") || "";
    dialog.showModal();
  });
})();
