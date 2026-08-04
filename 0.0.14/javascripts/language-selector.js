/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-present David G. Simmons
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

(function() {
  'use strict';

  // Map language codes to flag emojis
  const languageFlags = {
    'en': '🇺🇸',
    'es': '🇪🇸',
    'fr': '🇫🇷',
    'de': '🇩🇪'
  };

  /** Locales that use a first-segment prefix on the standalone site (mkdocs-static-i18n). */
  const PREFIX_LOCALES = ['es', 'fr', 'de'];

  /** In-app docs panel (Duckling UI) serves the built site under this path prefix. */
  const INAPP_DOCS_RE = /^(\/api\/docs\/site\/)(en|es|fr|de)(\/.*)?$/;

  function ensureMkdocsDirUrl(path) {
    if (!path || path === '/' || path.endsWith('/') || /\.[a-z0-9]+$/i.test(path)) {
      return path;
    }
    return path + '/';
  }

  /**
   * Parse pathname into locale + logical doc path (shared across languages).
   * Supports standalone MkDocs (/es/..., /...) and in-app /api/docs/site/<lang>/...
   */
  function parsePathContext(pathname) {
    var raw = (pathname || '/').split(/[?#]/)[0];
    var app = raw.match(INAPP_DOCS_RE);
    if (app) {
      var tail = app[3];
      var rest = !tail || tail === '/' ? '/' : tail;
      return { kind: 'inapp', base: app[1], locale: app[2], rest: rest };
    }
    var loc = raw.match(/^\/(es|fr|de)(\/.*)?$/);
    if (loc) {
      var tail2 = loc[2];
      var rest2 = !tail2 || tail2 === '/' ? '/' : tail2;
      return { kind: 'standalone', locale: loc[1], rest: rest2 };
    }
    var restEn = raw && raw !== '' ? raw : '/';
    return { kind: 'standalone', locale: 'en', rest: restEn };
  }

  /**
   * Absolute path on this host for the same page in another language.
   */
  function hrefForPathContext(ctx, targetLang, hash) {
    var h = hash && hash.length > 1 ? hash : '';
    var rest = ctx.rest || '/';
    if (rest.charAt(0) !== '/') {
      rest = '/' + rest;
    }
    if (ctx.kind === 'inapp') {
      var mid = ctx.base + targetLang;
      var tailPart = rest === '/' ? '/' : rest;
      return ensureMkdocsDirUrl(mid + tailPart) + h;
    }
    if (targetLang === 'en') {
      return ensureMkdocsDirUrl(rest) + h;
    }
    var out = '/' + targetLang + (rest === '/' ? '/' : rest);
    return ensureMkdocsDirUrl(out) + h;
  }

  /**
   * Determine locale for a language menu anchor, even when Material emits broken relative hrefs.
   */
  function getAnchorLanguage(anchor) {
    if (!anchor) {
      return null;
    }
    var explicit = anchor.getAttribute('hreflang') ||
      anchor.getAttribute('lang') ||
      anchor.getAttribute('data-md-value');
    if (explicit && Object.prototype.hasOwnProperty.call(languageFlags, explicit)) {
      return explicit;
    }

    var rawHref = anchor.getAttribute('href') || '';
    if (!rawHref) {
      return null;
    }
    var normalizedHref = rawHref.split(/[?#]/)[0];

    try {
      normalizedHref = new URL(rawHref, window.location.origin).pathname;
    } catch (e) {
      // Keep raw href fallback for partial/broken relative paths.
    }

    var match = normalizedHref.match(/\/(en|es|fr|de)(?:\/|$)/);
    if (!match) {
      match = normalizedHref.match(/(?:^|[./])(en|es|fr|de)\/?$/);
    }
    return match ? match[1] : null;
  }

  /**
   * mkdocs-static-i18n + Material can emit broken relative hrefs like "../../../../../..es/" (missing slash
   * before the locale). Rewrite language dropdown links so switching locale keeps the same page (and hash).
   */
  function fixLanguageSwitcherHrefs() {
    var pathname = window.location.pathname;
    var ctx = parsePathContext(pathname);
    var hash = window.location.hash || '';

    document.querySelectorAll('a.md-select__link').forEach(function(anchor) {
      var lang = getAnchorLanguage(anchor);
      if (!lang || !Object.prototype.hasOwnProperty.call(languageFlags, lang)) {
        return;
      }
      anchor.setAttribute('hreflang', lang);
      anchor.setAttribute('href', hrefForPathContext(ctx, lang, hash));
    });
  }

  /**
   * Detect the current language from the URL path
   */
  function detectCurrentLanguage() {
    var path = window.location.pathname;
    var app = path.match(INAPP_DOCS_RE);
    if (app) {
      return app[2];
    }
    for (var i = 0; i < PREFIX_LOCALES.length; i++) {
      var code = PREFIX_LOCALES[i];
      if (path === '/' + code || path.startsWith('/' + code + '/')) {
        return code;
      }
    }
    return 'en';
  }

  /**
   * Update the language selector icon/button to show the current language flag
   */
  function updateLanguageSelectorIcon() {
    const currentLang = detectCurrentLanguage();
    const flag = languageFlags[currentLang] || '🇺🇸';
    
    // Material for MkDocs uses a button with an icon for the language selector
    // The button is typically: .md-header__button--lang or contains the language selector
    // Find all header buttons and check which one is the language selector
    const headerButtons = document.querySelectorAll('.md-header__button');
    let langButton = null;
    
    // Try to find the language button by checking for language-related attributes/content
    for (const button of headerButtons) {
      const ariaLabel = button.getAttribute('aria-label') || '';
      const buttonText = button.textContent || '';
      const hasLangIcon = button.querySelector('[data-md-icon="language"]') || 
                         button.querySelector('[data-md-icon="translate"]') ||
                         button.querySelector('[data-md-icon="flag"]') ||
                         button.querySelector('.md-icon--lang');
      
      if (ariaLabel.toLowerCase().includes('language') || 
          ariaLabel.toLowerCase().includes('lang') ||
          button.classList.contains('md-header__button--lang') ||
          hasLangIcon) {
        langButton = button;
        break;
      }
    }
    
    // Fallback: try common selectors
    if (!langButton) {
      langButton = document.querySelector('.md-header__button--lang') ||
                  document.querySelector('[data-md-component="lang"]') ||
                  document.querySelector('.md-header__button:has([data-md-icon])');
    }
    
    if (langButton) {
      // Remove any existing flag we added previously
      const existingFlag = langButton.querySelector('.md-header__lang-flag');
      if (existingFlag) {
        existingFlag.remove();
      }
      
      // Find and hide the icon element
      const iconElement = langButton.querySelector('.md-icon') ||
                         langButton.querySelector('svg') ||
                         langButton.querySelector('[data-md-icon]');
      
      if (iconElement) {
        // Completely hide the icon
        iconElement.style.cssText = 'display: none !important; visibility: hidden !important; opacity: 0 !important; width: 0 !important; height: 0 !important;';
        iconElement.setAttribute('aria-hidden', 'true');
        
        // Create flag span
        const flagSpan = document.createElement('span');
        flagSpan.className = 'md-header__lang-flag';
        flagSpan.textContent = flag;
        flagSpan.setAttribute('aria-hidden', 'true');
        flagSpan.style.cssText = 'font-size: 1.5rem !important; line-height: 1 !important; display: inline-block !important; vertical-align: middle !important; width: 1.5rem !important; height: 1.5rem !important; text-align: center !important; visibility: visible !important; opacity: 1 !important;';
        
        // Replace the icon with the flag
        const iconParent = iconElement.parentElement;
        if (iconParent) {
          // If parent is the button itself, replace icon
          if (iconParent === langButton) {
            langButton.replaceChild(flagSpan, iconElement);
          } else {
            // Otherwise, insert flag and hide icon
            iconParent.insertBefore(flagSpan, iconElement);
          }
        } else {
          // Fallback: prepend to button
          langButton.insertBefore(flagSpan, langButton.firstChild);
        }
      } else {
        // No icon found - check if button already has flag, if not add it
        const buttonContent = langButton.innerHTML || '';
        if (!buttonContent.match(/[🇺🇸🇪🇸🇫🇷🇩🇪]/)) {
          const flagSpan = document.createElement('span');
          flagSpan.className = 'md-header__lang-flag';
          flagSpan.textContent = flag;
          flagSpan.style.cssText = 'font-size: 1.5rem !important; line-height: 1 !important; display: inline-block !important; vertical-align: middle !important; margin-right: 0.25rem !important;';
          langButton.insertBefore(flagSpan, langButton.firstChild);
        } else {
          // Update existing flag
          const existingFlagInContent = langButton.querySelector('.md-header__lang-flag') ||
                                       Array.from(langButton.childNodes).find(node => 
                                         node.nodeType === Node.TEXT_NODE && 
                                         node.textContent.match(/[🇺🇸🇪🇸🇫🇷🇩🇪]/)
                                       );
          if (existingFlagInContent) {
            if (existingFlagInContent.textContent !== flag) {
              existingFlagInContent.textContent = flag;
            }
          }
        }
      }
    }
  }

  /**
   * Initialize and set up observers
   */
  function init() {
    fixLanguageSwitcherHrefs();
    updateLanguageSelectorIcon();

    // Try multiple times to catch Material's rendering
    const attempts = [100, 300, 500, 1000, 2000];
    attempts.forEach(delay => {
      setTimeout(() => {
        fixLanguageSwitcherHrefs();
        updateLanguageSelectorIcon();
      }, delay);
    });
    
    // Watch for DOM changes (Material's instant navigation)
    const observer = new MutationObserver(function(mutations) {
      let shouldUpdate = false;
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          // Check if any added nodes contain the language button
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.classList?.contains('md-header') ||
                  node.classList?.contains('md-header__button') ||
                  node.querySelector?.('.md-header__button--lang') ||
                  node.querySelector?.('[data-md-component="lang"]')) {
                shouldUpdate = true;
              }
            }
          });
        }
        if (mutation.type === 'attributes') {
          const target = mutation.target;
          if (target && (
            target.classList?.contains('md-header__button') ||
            target.classList?.contains('md-header')
          )) {
            shouldUpdate = true;
          }
        }
      });
      if (shouldUpdate) {
        setTimeout(function() {
          fixLanguageSwitcherHrefs();
          updateLanguageSelectorIcon();
        }, 150);
      }
    });
    
    // Observe the header specifically
    const header = document.querySelector('.md-header');
    if (header) {
      observer.observe(header, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'data-md-component', 'aria-label']
      });
    }
    
    // Also observe the entire document as fallback
    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'data-md-component']
    });
    
    // Watch for URL changes
    let lastUrl = location.href;
    setInterval(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(function() {
          fixLanguageSwitcherHrefs();
          updateLanguageSelectorIcon();
        }, 150);
      }
    }, 500);
    
    // Also watch for hash changes
    window.addEventListener('hashchange', function() {
      setTimeout(function() {
        fixLanguageSwitcherHrefs();
        updateLanguageSelectorIcon();
      }, 150);
    });
    
    // Watch for popstate (browser back/forward)
    window.addEventListener('popstate', function() {
      setTimeout(function() {
        fixLanguageSwitcherHrefs();
        updateLanguageSelectorIcon();
      }, 150);
    });
    
    // Watch for Material's instant navigation events
    document.addEventListener('navigation', function() {
      setTimeout(function() {
        fixLanguageSwitcherHrefs();
        updateLanguageSelectorIcon();
      }, 200);
    });
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
