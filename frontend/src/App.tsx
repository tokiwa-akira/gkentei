import { Routes, Route } from 'react-router-dom'
import { AppShell } from '@mantine/core'

import { AppHeader } from '@/components/layout/AppHeader'
import { AppNavbar } from '@/components/layout/AppNavbar'
import { SearchPage } from '@/pages/search/SearchPage'
import { ExamPage } from '@/pages/exam/ExamPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { SettingsPage } from '@/pages/settings/SettingsPage'

function App() {
  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <AppHeader />
      </AppShell.Header>
      
      <AppShell.Navbar>
        <AppNavbar />
      </AppShell.Navbar>
      
      <AppShell.Main>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/exam" element={<ExamPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App