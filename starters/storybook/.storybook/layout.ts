export const storybookNoAddonPanelTag = 'no-addon-panel'

type StorybookIndexEntry = {
  tags?: string[]
}

export type StorybookLayoutState = {
  storyId?: string
  internal_index?: {
    entries: Record<string, StorybookIndexEntry | undefined>
  }
}

export function showAddonPanelForEntry(state: StorybookLayoutState, defaultValue: boolean) {
  const selectedEntry = state.storyId ? state.internal_index?.entries[state.storyId] : undefined
  return selectedEntry?.tags?.includes(storybookNoAddonPanelTag) ? false : defaultValue
}
