import { readFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { staticStoryContractsFor, storybookNoAddonPanelTag } from './lib/storybook.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const index = JSON.parse(await readFile(resolve(root, 'storybook-static/index.json'), 'utf8'))
const resolvedManifest = JSON.parse(await readFile(resolve(root, 'shared/generated/manifest.resolved.json'), 'utf8'))
const entries = index.entries
const expected = Object.fromEntries([
  ...staticStoryContractsFor(resolvedManifest).map(([id, title, name]) => [id, { title, name }]),
  ...resolvedManifest.artifacts.map(({ story }) => [
    `${story.id}--document`,
    { title: story.group, name: story.name },
  ]),
])

for (const [id, contract] of Object.entries(expected)) {
  const entry = entries[id]
  if (!entry) throw new Error(`Storybook 构建缺少稳定入口：${id}`)
  if (entry.title !== contract.title || entry.name !== contract.name) {
    throw new Error(`Storybook 入口漂移：${id}`)
  }
}

const stories = Object.values(entries).filter(({ type }) => type === 'story')
const docs = Object.values(entries).filter(({ type }) => type === 'docs')
if (stories.length !== Object.keys(expected).length) {
  throw new Error(`Storybook story 数量漂移：期望 ${Object.keys(expected).length}，实际 ${stories.length}`)
}
if (docs.length !== 0) throw new Error(`禁止空 autodocs 入口，实际 ${docs.length}`)

const reading = stories.filter(({ tags }) => tags?.includes(storybookNoAddonPanelTag)).map(({ id }) => id).sort()
const expectedReading = [
  'dossier-home--overview',
  'attachment-formats--formats',
  ...resolvedManifest.artifacts.map(({ story }) => `${story.id}--document`),
].sort()
if (JSON.stringify(reading) !== JSON.stringify(expectedReading)) {
  throw new Error(`阅读入口集合漂移：${reading.join(',')}`)
}

const groups = new Set(stories.map(({ title }) => title))
console.log(`构建索引通过：${groups.size} 个一级组、${stories.length} 个稳定 story、0 个 autodocs、${reading.length} 个阅读入口。`)
