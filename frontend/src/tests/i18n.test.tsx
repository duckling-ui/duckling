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


