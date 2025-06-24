/**
* Template Name: Medilab
* Template URL: https://bootstrapmade.com/medilab-free-medical-bootstrap-theme/
* Updated: Aug 07 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
  if (mobileNavToggleBtn) {
    function mobileNavToogle() {
      document.querySelector('body').classList.toggle('mobile-nav-active');
      mobileNavToggleBtn.classList.toggle('bi-list');
      mobileNavToggleBtn.classList.toggle('bi-x');
    }
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  const navMenuLinks = document.querySelectorAll('#navmenu a');
  if (navMenuLinks.length > 0 && typeof mobileNavToogle === 'function') {
    navMenuLinks.forEach(navmenu => {
      navmenu.addEventListener('click', () => {
        if (document.querySelector('.mobile-nav-active')) {
          mobileNavToogle();
        }
      });
    });
  }

  /**
   * Toggle mobile nav dropdowns
   */
  const toggleDropdowns = document.querySelectorAll('.navmenu .toggle-dropdown');
  if (toggleDropdowns.length > 0) {
    toggleDropdowns.forEach(navmenu => {
      navmenu.addEventListener('click', function(e) {
        e.preventDefault();
        this.parentNode.classList.toggle('active');
        this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
        e.stopImmediatePropagation();
      });
    });
  }

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  if (scrollTop) {
    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

  // Accessibility Features
  const accessibilityIcon = document.getElementById('accessibility-icon');
  const accessibilityPanel = document.getElementById('accessibility-panel');
  const closeAccessibilityPanelBtn = document.getElementById('close-accessibility-panel');

  if (accessibilityIcon) {
      accessibilityIcon.addEventListener('click', (event) => {
          event.stopPropagation();
          accessibilityPanel.classList.toggle('open');
      });
  }

  if (closeAccessibilityPanelBtn) {
      closeAccessibilityPanelBtn.addEventListener('click', () => {
          accessibilityPanel.classList.remove('open');
      });
  }

  // Close the panel when clicking outside
  document.addEventListener('click', (event) => {
      const isClickInsidePanel = accessibilityPanel.contains(event.target);
      const isClickOnIcon = accessibilityIcon.contains(event.target);

      if (!isClickInsidePanel && !isClickOnIcon && accessibilityPanel.classList.contains('open')) {
          accessibilityPanel.classList.remove('open');
      }
  });

  // Dark Mode Feature
  const darkModeSwitch = document.getElementById('dark-mode-switch');
  const darkModeIcon = document.getElementById('dark-mode-icon');
  const darkModeText = document.getElementById('dark-mode-text');
  const body = document.body;

  function updateDarkModeUI(isDarkMode) {
      if (darkModeIcon && darkModeText && darkModeSwitch) {
          if (isDarkMode) {
              darkModeIcon.classList.remove('bi-moon');
              darkModeIcon.classList.add('bi-sun');
              darkModeText.textContent = 'Dark Mode (On)';
              darkModeSwitch.checked = true;
          } else {
              darkModeIcon.classList.remove('bi-sun');
              darkModeIcon.classList.add('bi-moon');
              darkModeText.textContent = 'Dark Mode';
              darkModeSwitch.checked = false;
          }
      }
  }

  // Check for saved theme preference on load
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
      body.classList.add(savedTheme);
      updateDarkModeUI(savedTheme === 'dark-mode');
  } else {
      // Default to light mode and save preference
      body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light-mode');
      updateDarkModeUI(false);
  }

  if (darkModeSwitch) {
      darkModeSwitch.addEventListener('change', () => {
          const isDarkMode = darkModeSwitch.checked;
          if (isDarkMode) {
              body.classList.add('dark-mode');
              localStorage.setItem('theme', 'dark-mode');
          } else {
              body.classList.remove('dark-mode');
              localStorage.setItem('theme', 'light-mode');
          }
          updateDarkModeUI(isDarkMode);
      });
  }

  // Adjustable Font Size (Text Magnifier)
  const increaseTextBtn = document.getElementById('increase-text-btn');
  const decreaseTextBtn = document.getElementById('decrease-text-btn');
  const currentFontSizeSpan = document.getElementById('current-font-size');
  const initialFontSize = 16; // Base font size in pixels
  const fontSizeStep = 2; // Pixels to increase/decrease by
  const minFontSize = 12; // Minimum font size
  const maxFontSize = 24; // Maximum font size

  function setFontSize(size) {
      body.style.fontSize = `${size}px`;
      if (currentFontSizeSpan) {
          currentFontSizeSpan.textContent = `${size}px`;
      }
      localStorage.setItem('fontSize', size);
  }

  // Load saved font size on page load
  const savedFontSize = localStorage.getItem('fontSize');
  if (savedFontSize) {
      body.style.fontSize = `${savedFontSize}px`;
      if (currentFontSizeSpan) {
          currentFontSizeSpan.textContent = `${savedFontSize}px`;
      }
  } else {
      // Set initial font size if not saved
      body.style.fontSize = `${initialFontSize}px`;
      localStorage.setItem('fontSize', initialFontSize);
      if (currentFontSizeSpan) {
          currentFontSizeSpan.textContent = `${initialFontSize}px`;
      }
  }

  if (increaseTextBtn) {
      increaseTextBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentSize = parseInt(body.style.fontSize);
          if (isNaN(currentSize)) {
              currentSize = initialFontSize;
          }
          let newSize = Math.min(currentSize + fontSizeStep, maxFontSize);
          setFontSize(newSize);
      });
  }

  if (decreaseTextBtn) {
      decreaseTextBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentSize = parseInt(body.style.fontSize);
          if (isNaN(currentSize)) {
              currentSize = initialFontSize;
          }
          let newSize = Math.max(currentSize - fontSizeStep, minFontSize);
          setFontSize(newSize);
      });
  }

  // Highlight Links Feature
  const highlightLinkSwitch = document.getElementById('highlight-link-switch');
  const highlightLinkIcon = document.getElementById('highlight-link-icon');
  const highlightLinkText = document.getElementById('highlight-link-text');

  function updateHighlightLinkUI(isActive) {
      if (highlightLinkIcon && highlightLinkText && highlightLinkSwitch) {
          if (isActive) {
              highlightLinkIcon.classList.remove('bi-link');
              highlightLinkIcon.classList.add('bi-check-circle-fill');
              highlightLinkText.textContent = 'Highlight Links (On)';
              highlightLinkSwitch.checked = true;
          } else {
              highlightLinkIcon.classList.remove('bi-check-circle-fill');
              highlightLinkIcon.classList.add('bi-link');
              highlightLinkText.textContent = 'Highlight Links';
              highlightLinkSwitch.checked = false;
          }
      }
  }

  // Load saved state on page load
  const savedHighlightLinks = localStorage.getItem('highlightLinks');
  if (savedHighlightLinks === 'true') {
      body.classList.add('highlight-links-active');
      updateHighlightLinkUI(true);
  } else {
      body.classList.remove('highlight-links-active');
      updateHighlightLinkUI(false);
  }

  if (highlightLinkSwitch) {
      highlightLinkSwitch.addEventListener('change', () => {
          const isActive = highlightLinkSwitch.checked;
          if (isActive) {
              body.classList.add('highlight-links-active');
              localStorage.setItem('highlightLinks', true);
          } else {
              body.classList.remove('highlight-links-active');
              localStorage.setItem('highlightLinks', false);
          }
          updateHighlightLinkUI(isActive);
      });
  }

  // Highlight Titles Feature
  const highlightTitleSwitch = document.getElementById('highlight-title-switch');
  const highlightTitleIcon = document.getElementById('highlight-title-icon');
  const highlightTitleText = document.getElementById('highlight-title-text');

  function updateHighlightTitleUI(isActive) {
      if (highlightTitleIcon && highlightTitleText && highlightTitleSwitch) {
          if (isActive) {
              highlightTitleIcon.classList.remove('bi-type-h1');
              highlightTitleIcon.classList.add('bi-check-circle-fill');
              highlightTitleText.textContent = 'Highlight Titles (On)';
              highlightTitleSwitch.checked = true;
          } else {
              highlightTitleIcon.classList.remove('bi-check-circle-fill');
              highlightTitleIcon.classList.add('bi-type-h1');
              highlightTitleText.textContent = 'Highlight Titles';
              highlightTitleSwitch.checked = false;
          }
      }
  }

  // Load saved state on page load
  const savedHighlightTitles = localStorage.getItem('highlightTitles');
  if (savedHighlightTitles === 'true') {
      body.classList.add('highlight-titles-active');
      updateHighlightTitleUI(true);
  } else {
      body.classList.remove('highlight-titles-active');
      updateHighlightTitleUI(false);
  }

  if (highlightTitleSwitch) {
      highlightTitleSwitch.addEventListener('change', () => {
          const isActive = highlightTitleSwitch.checked;
          if (isActive) {
              body.classList.add('highlight-titles-active');
              localStorage.setItem('highlightTitles', true);
          } else {
              body.classList.remove('highlight-titles-active');
              localStorage.setItem('highlightTitles', false);
          }
          updateHighlightTitleUI(isActive);
      });
  }

  // Readable Font Feature
  const readableFontSwitch = document.getElementById('readable-font-switch');
  const readableFontIcon = document.getElementById('readable-font-icon');
  const readableFontText = document.getElementById('readable-font-text');

  function updateReadableFontUI(isActive) {
      if (readableFontIcon && readableFontText && readableFontSwitch) {
          if (isActive) {
              readableFontIcon.classList.remove('bi-fonts');
              readableFontIcon.classList.add('bi-check-circle-fill');
              readableFontText.textContent = 'Readable Font (On)';
              readableFontSwitch.checked = true;
          } else {
              readableFontIcon.classList.remove('bi-check-circle-fill');
              readableFontIcon.classList.add('bi-fonts');
              readableFontText.textContent = 'Readable Font';
              readableFontSwitch.checked = false;
          }
      }
  }

  // Load saved state on page load
  const savedReadableFont = localStorage.getItem('readableFont');
  if (savedReadableFont === 'true') {
      body.classList.add('readable-font-active');
      updateReadableFontUI(true);
  } else {
      body.classList.remove('readable-font-active');
      updateReadableFontUI(false);
  }

  if (readableFontSwitch) {
      readableFontSwitch.addEventListener('change', () => {
          const isActive = readableFontSwitch.checked;
          if (isActive) {
              body.classList.add('readable-font-active');
              localStorage.setItem('readableFont', true);
          } else {
              body.classList.remove('readable-font-active');
              localStorage.setItem('readableFont', false);
          }
          updateReadableFontUI(isActive);
      });
  }

  // New Feature: Line Height Adjustment
  const decreaseLineHeightBtn = document.getElementById('decrease-line-height-btn');
  const increaseLineHeightBtn = document.getElementById('increase-line-height-btn');
  const currentLineHeightSpan = document.getElementById('current-line-height');

  const initialLineHeight = 1.5; // Base line height
  const lineHeightStep = 0.1; // Step to increase/decrease by
  const minLineHeight = 1.2; 
  const maxLineHeight = 2.0; 

  function setLineHeight(height) {
      body.style.lineHeight = height;
      if (currentLineHeightSpan) {
          currentLineHeightSpan.textContent = height.toFixed(1);
      }
      localStorage.setItem('lineHeight', height);
  }

  // Load saved line height on page load
  const savedLineHeight = localStorage.getItem('lineHeight');
  if (savedLineHeight) {
      body.style.lineHeight = savedLineHeight;
      if (currentLineHeightSpan) {
          currentLineHeightSpan.textContent = parseFloat(savedLineHeight).toFixed(1);
      }
  } else {
      body.style.lineHeight = initialLineHeight;
      localStorage.setItem('lineHeight', initialLineHeight);
      if (currentLineHeightSpan) {
          currentLineHeightSpan.textContent = initialLineHeight.toFixed(1);
      }
  }

  if (increaseLineHeightBtn) {
      increaseLineHeightBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentHeight = parseFloat(body.style.lineHeight);
          if (isNaN(currentHeight)) {
              currentHeight = initialLineHeight;
          }
          let newHeight = Math.min(currentHeight + lineHeightStep, maxLineHeight);
          setLineHeight(newHeight);
      });
  }

  if (decreaseLineHeightBtn) {
      decreaseLineHeightBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentHeight = parseFloat(body.style.lineHeight);
          if (isNaN(currentHeight)) {
              currentHeight = initialLineHeight;
          }
          let newHeight = Math.max(currentHeight - lineHeightStep, minLineHeight);
          setLineHeight(newHeight);
      });
  }

  // New Feature: Letter Spacing Adjustment
  const decreaseLetterSpacingBtn = document.getElementById('decrease-letter-spacing-btn');
  const increaseLetterSpacingBtn = document.getElementById('increase-letter-spacing-btn');
  const currentLetterSpacingSpan = document.getElementById('current-letter-spacing');

  const initialLetterSpacing = 0; // Base letter spacing in pixels
  const letterSpacingStep = 0.5; // Pixels to increase/decrease by
  const minLetterSpacing = 0; 
  const maxLetterSpacing = 2.0; 

  function setLetterSpacing(spacing) {
      body.style.letterSpacing = `${spacing}px`;
      if (currentLetterSpacingSpan) {
          currentLetterSpacingSpan.textContent = `${spacing}px`;
      }
      localStorage.setItem('letterSpacing', spacing);
  }

  // Load saved letter spacing on page load
  const savedLetterSpacing = localStorage.getItem('letterSpacing');
  if (savedLetterSpacing) {
      body.style.letterSpacing = `${savedLetterSpacing}px`;
      if (currentLetterSpacingSpan) {
          currentLetterSpacingSpan.textContent = `${savedLetterSpacing}px`;
      }
  } else {
      body.style.letterSpacing = `${initialLetterSpacing}px`;
      localStorage.setItem('letterSpacing', initialLetterSpacing);
      if (currentLetterSpacingSpan) {
          currentLetterSpacingSpan.textContent = `${initialLetterSpacing}px`;
      }
  }

  if (increaseLetterSpacingBtn) {
      increaseLetterSpacingBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentSpacing = parseFloat(body.style.letterSpacing);
          if (isNaN(currentSpacing)) {
              currentSpacing = initialLetterSpacing;
          }
          let newSpacing = Math.min(currentSpacing + letterSpacingStep, maxLetterSpacing);
          setLetterSpacing(newSpacing);
      });
  }

  if (decreaseLetterSpacingBtn) {
      decreaseLetterSpacingBtn.addEventListener('click', (e) => {
          e.preventDefault();
          let currentSpacing = parseFloat(body.style.letterSpacing);
          if (isNaN(currentSpacing)) {
              currentSpacing = initialLetterSpacing;
          }
          let newSpacing = Math.max(currentSpacing - letterSpacingStep, minLetterSpacing);
          setLetterSpacing(newSpacing);
      });
  }

  // Initialize Swiper for testimonials slider on About page
  window.addEventListener('load', function() {
    var testimonialsSlider = document.querySelector('.testimonials-slider');
    if (testimonialsSlider && typeof Swiper !== 'undefined') {
      new Swiper(testimonialsSlider, {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        pagination: {
          el: '.swiper-pagination',
          clickable: true,
        },
        autoplay: false // Set to { delay: 5000 } for autoplay
      });
    }
  });

})();