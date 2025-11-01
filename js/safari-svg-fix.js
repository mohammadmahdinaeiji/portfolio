document.addEventListener("DOMContentLoaded", function () {
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!isSafari) return;

    const buttons = document.querySelectorAll(
        '.theme-toggle, .contact-btn, .popup-icons button, .popup-icons a, .popup-icons div'
    );

    buttons.forEach(btn => {
        const svgImg = btn.querySelector('img[src$=".svg"]');
        if (!svgImg) return;

        // گرفتن ابعاد دقیق دکمه
        const rect = btn.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;

        // SVG → دقیقاً اندازه دکمه
        svgImg.style.width = width + "px";
        svgImg.style.height = height + "px";
        svgImg.style.display = "block";

        // کوچک‌سازی ×5
        svgImg.style.transform = "scale(0.2)";
        svgImg.style.transformOrigin = "center center";

        // جلوگیری از جابجایی ناخواسته
        svgImg.style.objectFit = "contain";
        svgImg.style.margin = "0";
        svgImg.style.padding = "0";
    });
});
