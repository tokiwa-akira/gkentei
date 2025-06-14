import { NavLink, Stack } from '@mantine/core'
import { IconSearch, IconFileText, IconChartBar, IconSettings } from '@tabler/icons-react'
import { useLocation, useNavigate } from 'react-router-dom'

const navItems = [
  { icon: IconSearch, label: '検索', href: '/search' },
  { icon: IconFileText, label: '模試', href: '/exam' },
  { icon: IconChartBar, label: 'ダッシュボード', href: '/dashboard' },
  { icon: IconSettings, label: '設定', href: '/settings' },
]

export function AppNavbar() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Stack gap={0} p="md">
      {navItems.map((item) => (
        <NavLink
          key={item.href}
          href={item.href}
          label={item.label}
          leftSection={<item.icon size="1rem" />}
          active={location.pathname === item.href}
          onClick={(e) => {
            e.preventDefault()
            navigate(item.href)
          }}
        />
      ))}
    </Stack>
  )
}