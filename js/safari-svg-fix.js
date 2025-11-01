document.addEventListener("DOMContentLoaded", function () {
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!isSafari) return;

    // انتخاب تمام دکمه‌هایی که داخلشون SVG هست
    const buttons = document.querySelectorAll(
        '.theme-toggle, .contact-btn, .popup-icons button, .popup-icons a, .popup-icons div'
    );

    buttons.forEach(btn => {
        const svgImg = btn.querySelector('img[src$=".svg"]');
        if (!svgImg) return;

        // اندازه واقعی دکمه از کامپیوتد CSS
        const btnStyles = window.getComputedStyle(btn);
        const btnWidth = parseFloat(btnStyles.width);
        const btnHeight = parseFloat(btnStyles.height);

        // SVG همیشه کمی کوچیک‌تر از دکمه باشه (مثلاً 80%)
        const size = Math.min(btnWidth, btnHeight) * 0.8;

        // اعمال تنظیمات دقیق
        svgImg.style.width = `${size}px`;
        svgImg.style.height = `${size}px`;
        svgImg.style.display = "block";
        svgImg.style.margin = "auto";
        svgImg.style.objectFit = "contain";
        svgImg.style.transformOrigin = "center";

        // جلوگیری از بُزرگ‌شدن بیش از حد هنگام hover
        btn.addEventListener('mouseenter', () => {
            svgImg.style.transformOrigin = "center center";
        });
    });
});
