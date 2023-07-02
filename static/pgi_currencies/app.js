window.addEventListener("load", () => {
    document.querySelectorAll(".nav-link").forEach(navbar => {
        if (navbar.href === window.location.href) {
            navbar.classList.add("active");
            navbar.setAttribute("aria-current", "page");
        }
    });
});