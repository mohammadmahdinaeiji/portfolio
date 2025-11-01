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
        const btnRect = btn.getBoundingClientRect();
        const width = btnRect.width;
        const height = btnRect.height;

        // تنظیم دقیق SVG برابر دکمه
        svgImg.style.width = width + "px";
        svgImg.style.height = height + "px";

        // جلوگیری از بهم‌ریختن
        svgImg.style.objectFit = "contain";
        svgImg.style.transformOrigin = "center center";
        svgImg.style.display = "block";
        svgImg.style.margin = "0";
        svgImg.style.padding = "0";
    });
});
