/**
 * index.js
 * --------
 * トップページのスクロール演出（白いパネル・カードの出現）。
 */

document.addEventListener("DOMContentLoaded", function () {
    const panel = document.querySelector(".features-panel");
    const hint = document.querySelector(".hero-scroll-hint");
    if (!panel) return;

    let revealed = false;

    const reveal = () => {
        if (revealed) return;
        revealed = true;
        panel.classList.add("is-revealed");
        if (hint) hint.classList.add("is-hidden");
    };

    const hasScrolled = () => window.scrollY > 48;

    const tryReveal = () => {
        if (!hasScrolled()) return;

        const panelTop = panel.getBoundingClientRect().top;
        if (panelTop < window.innerHeight * 0.92) {
            reveal();
        }
    };

    window.addEventListener(
        "scroll",
        () => {
            if (hasScrolled() && hint) hint.classList.add("is-hidden");
            tryReveal();
        },
        { passive: true }
    );

    if (!("IntersectionObserver" in window)) {
        window.addEventListener("scroll", tryReveal, { passive: true });
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting && hasScrolled()) {
                    reveal();
                    observer.disconnect();
                }
            });
        },
        { threshold: 0, rootMargin: "0px 0px -15% 0px" }
    );

    observer.observe(panel);
});
