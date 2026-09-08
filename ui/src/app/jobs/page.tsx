'use client';

import JobsTable from '@/components/JobsTable';
import { TopBar, MainContent } from '@/components/layout';
import Link from 'next/link';
import { useLanguage } from '@/components/LanguageProvider';

export default function Dashboard() {
  const { t } = useLanguage();
  return (
    <>
      <TopBar>
        <div>
          <h1 className="text-base sm:text-lg">{t('queue.title')}</h1>
        </div>
        <div className="flex-1"></div>
        <div>
          <Link
            href="/jobs/new"
            className="text-white bg-slate-600 px-2 sm:px-3 py-1 rounded-md text-sm sm:text-base whitespace-nowrap"
          >
            <span className="sm:hidden">{t('queue.newJob')}</span>
            <span className="hidden sm:inline">{t('queue.newTrainingJob')}</span>
          </Link>
        </div>
      </TopBar>
      <MainContent>
        <JobsTable />
      </MainContent>
    </>
  );
}
