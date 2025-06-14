import { Group, Title, ActionIcon, useMantineColorScheme } from '@mantine/core'
import { IconSun, IconMoon } from '@tabler/icons-react'

export function AppHeader() {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme()

  return (
    <Group h="100%" px="md" justify="space-between">
      <Title order={3}>G検定対策ツール</Title>
      
      <ActionIcon
        variant="default"
        onClick={() => toggleColorScheme()}
        size={30}
      >
        {colorScheme === 'dark' ? <IconSun size="1rem" /> : <IconMoon size="1rem" />}
      </ActionIcon>
    </Group>
  )
}