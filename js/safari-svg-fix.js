document.addEventListener("DOMContentLoaded", () => {
    // بررسی Safari
    function isSafari() {
        const ua = navigator.userAgent;
        return /^((?!chrome|android).)*safari/i.test(ua);
    }

    if (isSafari()) {
        const targetFiles = ['moon.svg', 'sun.svg', 'contact.svg'];
        const imgs = document.querySelectorAll('img');

        imgs.forEach(img => {
            const srcFile = img.src.split('/').pop(); // فقط اسم فایل
            if (targetFiles.includes(srcFile)) {
                const src = img.src;
                img.src = '';
                setTimeout(() => {
                    img.src = src;
                }, 50); // 50ms تا Safari رندر کنه
            }
        });
    }
});
