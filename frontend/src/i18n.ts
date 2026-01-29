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

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enCommon from './locales/en/common.json';
import esCommon from './locales/es/common.json';
import frCommon from './locales/fr/common.json';
import deCommon from './locales/de/common.json';

const STORAGE_KEY = 'duckling.locale';

function detectInitialLanguage(): 'en' | 'es' | 'fr' | 'de' {
  try {
    const storage = typeof window !== 'undefined' ? window.localStorage : undefined;
    const saved =
      storage && typeof storage.getItem === 'function'
        ? storage.getItem(STORAGE_KEY)
        : null;
    if (saved === 'en' || saved === 'es' || saved === 'fr' || saved === 'de') return saved;
  } catch {
    // ignore storage access issues (e.g., test env / private mode)
  }

  const nav = (navigator.language || '').toLowerCase();
  if (nav.startsWith('es')) return 'es';
  if (nav.startsWith('fr')) return 'fr';
  if (nav.startsWith('de')) return 'de';
  return 'en';
}

void i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon },
      es: { common: esCommon },
      fr: { common: frCommon },
      de: { common: deCommon },
    },
    lng: detectInitialLanguage(),
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: ['common'],
    interpolation: {
      escapeValue: false,
    },
  });

i18n.on('languageChanged', (lng) => {
  try {
    const storage = typeof window !== 'undefined' ? window.localStorage : undefined;
    if (
      storage &&
      typeof storage.setItem === 'function' &&
      (lng === 'en' || lng === 'es' || lng === 'fr' || lng === 'de')
    ) {
      storage.setItem(STORAGE_KEY, lng);
    }
  } catch {
    // ignore storage access issues
  }
});

export default i18n;


