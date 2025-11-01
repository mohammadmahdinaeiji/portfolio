document.addEventListener("DOMContentLoaded", function() {
    // تشخیص Safari
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!isSafari) return;

    // اصلاح تمام SVG های داخل <img>
    const svgImgs = document.querySelectorAll('img[src$=".svg"]');
    svgImgs.forEach(img => {
        img.style.display = "block";
        img.style.width = "100%";
        img.style.height = "auto";
        img.style.transformOrigin = "center center";
    });

    // اصلاح آیکون‌هایی که transform دارند
    const toggleButtons = document.querySelectorAll('.theme-toggle, .contact-btn, .popup-icons img');
    toggleButtons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transformOrigin = "center center";
        });
    });
});
