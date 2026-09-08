'use client';

import { Languages } from 'lucide-react';
import { useLanguage } from './LanguageProvider';

export default function LanguageToggle() {
  const { language, toggleLanguage, t } = useLanguage();
  const title = language === 'en' ? t('language.switchToChinese') : t('language.switchToEnglish');

  return (
    <button
      type="button"
      onClick={toggleLanguage}
      className="group relative flex h-8 min-w-11 items-center justify-center rounded-lg border border-gray-700 bg-gray-800 px-1.5 text-gray-300 transition-all hover:border-blue-500 hover:bg-gray-700 hover:text-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      title={title}
      aria-label={title}
    >
      <Languages className="h-4 w-4 transition-transform group-hover:-rotate-6" aria-hidden="true" />
      <span className="ml-1 flex flex-col text-[8px] font-semibold leading-[8px] tracking-tight" aria-hidden="true">
        <span className={language === 'zh' ? 'text-blue-400' : ''}>中</span>
        <span className={language === 'en' ? 'text-blue-400' : ''}>EN</span>
      </span>
    </button>
  );
}
