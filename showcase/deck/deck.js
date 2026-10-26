(function () {
  const slides = Array.from(document.querySelectorAll(".slide"));
  const curEl = document.getElementById("cur");
  const totalEl = document.getElementById("total");
  let i = 0;

  totalEl.textContent = String(slides.length);

  function go(n) {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle("is-active", idx === i));
    curEl.textContent = String(i + 1);
    document.title = "VoiceBill Deck — " + (slides[i].dataset.title || i + 1);
  }

  document.getElementById("prev").addEventListener("click", () => go(i - 1));
  document.getElementById("next").addEventListener("click", () => go(i + 1));

  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
      e.preventDefault();
      go(i + 1);
    } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
      e.preventDefault();
      go(i - 1);
    } else if (e.key === "f" || e.key === "F") {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    } else if (e.key === "Home") go(0);
    else if (e.key === "End") go(slides.length - 1);
  });

  go(0);
})();
