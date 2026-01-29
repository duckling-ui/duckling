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

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { act } from 'react';
import { useTranslation } from 'react-i18next';

import i18n from '../i18n';

function Demo() {
  const { t } = useTranslation();
  return <div>{t('docsPanel.title')}</div>;
}

describe('i18n', () => {
  it('switches between English and Spanish', async () => {
    await act(async () => {
      await i18n.changeLanguage('en');
    });

    render(<Demo />);
    expect(screen.getByText('Documentation')).toBeInTheDocument();

    await act(async () => {
      await i18n.changeLanguage('es');
    });

    expect(screen.getByText('Documentación')).toBeInTheDocument();
  });
});


