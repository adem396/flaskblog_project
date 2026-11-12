const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Mobile menu button
const menuBtn = document.getElementById("menu-btn");
const menu = document.getElementById("menu");
if (menuBtn && menu) {
  menuBtn.addEventListener("click", () => {
    const open = menu.classList.toggle("show");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
}

// Header gets a shadow once the page is scrolled
const header = document.getElementById("site-header");
if (header) {
  const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 4);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

// Flash messages: close button, and success/info messages go away by themselves
function dismissFlash(el) {
  if (reduceMotion) {
    el.remove();
    return;
  }
  el.classList.add("leaving");
  el.addEventListener("transitionend", () => el.remove(), { once: true });
  setTimeout(() => el.remove(), 600); // safety net
}
document.querySelectorAll(".flash").forEach((el) => {
  const close = el.querySelector(".flash-close");
  if (close) close.addEventListener("click", () => dismissFlash(el));
  const category = el.dataset.category;
  if (category === "success" || category === "info") {
    setTimeout(() => dismissFlash(el), 6000);
  }
});

// Open / close the delete dialogs
document.querySelectorAll("[data-open-dialog]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById(btn.dataset.openDialog).showModal();
  });
});
document.querySelectorAll("[data-close-dialog]").forEach((btn) => {
  btn.addEventListener("click", () => btn.closest("dialog").close());
});

// Show the chosen profile picture before it is uploaded
const pictureInput = document.getElementById("picture");
const avatarPreview = document.getElementById("avatar-preview");
if (pictureInput && avatarPreview) {
  pictureInput.addEventListener("change", () => {
    const file = pictureInput.files[0];
    if (file) avatarPreview.src = URL.createObjectURL(file);
  });
}

// Timeline rows fade in when they scroll into view
const reveals = document.querySelectorAll(".reveal");
if (reveals.length) {
  if ("IntersectionObserver" in window && !reduceMotion) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveals.forEach((el) => observer.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("in"));
  }
}
