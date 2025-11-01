// تابع تنظیم ابعاد SVGها
function setSvgDimensions(selector, width = 32, height = 32, viewBox = "0 0 24 24") {
    const svgs = document.querySelectorAll(selector);
    svgs.forEach(svg => {
        svg.setAttribute("width", width);
        svg.setAttribute("height", height);
        svg.setAttribute("viewBox", viewBox);
    });
}

// اجرا بعد از لود DOM
document.addEventListener("DOMContentLoaded", () => {
    // روی آیکون‌های تم و باتن تماس اعمال می‌کنیم
    setSvgDimensions(".theme-toggle svg");        // moon & sun
    setSvgDimensions(".contact-btn svg");        // contact
});
