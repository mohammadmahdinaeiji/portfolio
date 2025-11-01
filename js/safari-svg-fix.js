// Detect Safari (desktop + iOS) robustly
function isSafariBrowser() {
  const ua = navigator.userAgent || '';
  const vendor = navigator.vendor || '';
  // AppleWebKit present but not Chrome/Chromium/Edge/Firefox (including iOS variants)
  const webkit = /AppleWebKit/.test(ua);
  const notOther = !/(Chrome|CriOS|Chromium|Edg|OPR|FxiOS)/.test(ua);
  // vendor contains Apple on Safari desktop; on some iOS webviews vendor may be empty — rely on webkit+notOther
  return webkit && notOther && (vendor.includes('Apple') || true);
}

// filenames to hide
const filesToHide = ['moon.svg', 'sun.svg', 'contact.svg'];

function elementReferencesFilename(el, filename) {
  try {
    // 1) <img src="...">
    if (el.tagName === 'IMG' && el.src && el.src.indexOf(filename) !== -1) return true;

    // 2) <use xlink:href="..."> or <use href="...">
    if (el.tagName === 'USE') {
      const href = el.getAttribute('href') || el.getAttribute('xlink:href') || '';
      if (href.indexOf(filename) !== -1) return true;
    }

    // 3) elements with <image href="..."> inside inline SVGs
    if (el.tagName === 'IMAGE') {
      const href = el.getAttribute('href') || el.getAttribute('xlink:href') || '';
      if (href.indexOf(filename) !== -1) return true;
    }

    // 4) CSS background-image: url(".../moon.svg")
    const style = window.getComputedStyle(el);
    if (style && style.backgroundImage && style.backgroundImage !== 'none' && style.backgroundImage.indexOf(filename) !== -1) {
      return true;
    }

    // 5) any element with src/href attributes (catch anchors, source, etc.)
    const srcAttr = el.getAttribute && (el.getAttribute('src') || el.getAttribute('href'));
    if (srcAttr && srcAttr.indexOf(filename) !== -1) return true;
  } catch (e) {
    // ignore cross-origin or other errors for some nodes
  }
  return false;
}

function hideSvgFilesOpacityZero(filenames, options = {}) {
  const transition = options.transition || 'opacity 300ms ease';
  const changed = new Set();

  // Consider all elements in document
  const all = document.getElementsByTagName('*');
  for (let i = 0; i < all.length; i++) {
    const el = all[i];
    for (const fname of filenames) {
      if (elementReferencesFilename(el, fname)) {
        // apply transition + opacity
        el.style.transition = transition;
        el.style.opacity = '0';
        changed.add(el);
        break; // no need to check other filenames for this element
      }
    }
  }

  // additionally try to find <img> by attribute selectors (in case src is relative or contains query params)
  filenames.forEach(fname => {
    const imgs = document.querySelectorAll(`img[src*="${fname}"]`);
    imgs.forEach(img => {
      img.style.transition = transition;
      img.style.opacity = '0';
      changed.add(img);
    });
    // background-image quick selector (may not match quotes) — we'll still rely on computed style above
    const bgEls = document.querySelectorAll(`[style*="${fname}"], [data-icon*="${fname}"]`);
    bgEls.forEach(el => {
      el.style.transition = transition;
      el.style.opacity = '0';
      changed.add(el);
    });
  });

  return Array.from(changed);
}

// Run on DOM ready
document.addEventListener('DOMContentLoaded', function () {
  if (isSafariBrowser()) {
    hideSvgFilesOpacityZero(filesToHide, { transition: 'opacity 240ms ease' });
    // optional: log for debugging
    // console.log('Safari detected — hidden files:', filesToHide);
  }
});
