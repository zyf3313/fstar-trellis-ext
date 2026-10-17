import { renderMarkdown } from './markdown.mjs'
import { posix } from 'node:path'

export const storybookNoAddonPanelTag = 'no-addon-panel'
export const storybookReviewAnchorParam = 'reviewAnchor'
export const storybookReviewTargetParam = 'reviewTarget'

export const storybookSidebarGroups = [
  {
    title: '文档',
    stories: [
      ['dossier-home--overview', '案卷首页'],
      ['product-requirements--document', '产品需求说明'],
      ['technical-design--document', '技术方案'],
      ['test-acceptance--document', '测试验收'],
      ['attachment-formats--formats', '附件与格式说明'],
    ],
  },
  {
    title: 'UI 设计语言与资产',
    stories: [
      ['design-language--tokens', '共享设计资产'],
      ['ui-design-document--document', 'UI 设计说明'],
    ],
  },
  {
    title: '可交互原型',
    stories: [
      ['review-flow--draft', '草稿'],
      ['review-flow--reviewing', '评审中'],
      ['review-flow--changes', '需修改'],
      ['review-flow--approved', '已通过'],
      ['prototype-document--document', '原型说明'],
    ],
  },
]

export const storybookStorySort = {
  includeNames: true,
  order: storybookSidebarGroups.flatMap(({ title, stories }) => [
    title,
    stories.map(([, name]) => name),
  ]),
}

const defaultArtifactStoryIds = [
  'product-requirements',
  'technical-design',
  'ui-design-document',
  'prototype-document',
  'test-acceptance',
]

export const storybookNoAddonPanelStoryIds = [
  'dossier-home--overview',
  ...defaultArtifactStoryIds.map((storyId) => `${storyId}--document`),
  'attachment-formats--formats',
]

export const storybookGeneratedFiles = [
  'Overview.stories.ts',
  'ProductRequirements.stories.ts',
  'TechnicalDesign.stories.ts',
  'UiDesignDocument.stories.ts',
  'PrototypeDocument.stories.ts',
  'TestAcceptance.stories.ts',
  'Attachments.stories.ts',
]

export function generatedFilesFor(manifest) {
  return [
    'Overview.stories.ts',
    ...manifest.artifacts.map(storyDefinition).map(({ file }) => file),
    'Attachments.stories.ts',
  ]
}

export function createStorybookProjection(manifest, sources) {
  const files = new Map()
  const artifactBySource = new Map(manifest.artifacts.map((artifact) => [posix.normalize(artifact.source), artifact]))

  files.set('Overview.stories.ts', overviewStory(manifest))
  for (const artifact of manifest.artifacts) {
    const entry = storyDefinition(artifact)
    const source = sources.get(artifact.id)
    if (!source) throw new Error(`Storybook 投影缺少 ${artifact.id}`)
    const resolveRelativeLink = (target) => {
      const [pathPart, anchor] = target.split('#', 2)
      const resolvedSource = posix.normalize(posix.join(posix.dirname(artifact.source), pathPart))
      const targetArtifact = artifactBySource.get(resolvedSource)
      if (!targetArtifact) return undefined
      const targetStory = storyDefinition(targetArtifact)
      return storybookDocumentHref(targetStory.storyId, anchor)
    }
    files.set(entry.file, documentStory(entry, artifact, renderMarkdown(source.body, { resolveRelativeLink })))
  }
  files.set('Attachments.stories.ts', attachmentsStory(manifest))
  return files
}

export function storybookDocumentHref(storyId, anchor) {
  const storyPath = `/story/${storyId}--document`
  const href = `./?path=${storyPath}`
  if (!anchor) return href
  if (!/^[A-Za-z0-9_-]+$/.test(anchor)) throw new Error(`无效的跨文档锚点：${anchor}`)
  return `${href}&${storybookReviewAnchorParam}=${encodeURIComponent(anchor)}&${storybookReviewTargetParam}=${encodeURIComponent(storyPath)}`
}

function overviewStory(manifest) {
  const entries = manifest.artifacts.map((artifact) => ({
    id: artifact.id,
    title: artifact.title,
    summary: artifact.summary,
    version: artifact.version,
    reviewStatus: artifact.reviewStatus,
    source: artifact.source,
    sourceHash: artifact.sourceHash,
    href: `./?path=/story/${storyDefinition(artifact).storyId}--document`,
  }))

  return generatedHeader() + `import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ReviewOverview from '../../shared/components/ReviewOverview.vue'

const meta = {
  id: 'dossier-home',
  title: '文档',
  component: ReviewOverview,
  tags: [${json(storybookNoAddonPanelTag)}],
  args: {
    title: ${json(manifest.title)},
    version: ${json(manifest.version)},
    status: ${json(manifest.status)},
    updatedAt: ${json(manifest.updatedAt)},
    manifestId: ${json(manifest.id)},
    manifestSource: ${json(manifest.manifestSource)},
    manifestHash: ${json(manifest.manifestHash)},
    sourceRoot: ${json(manifest.projectRoot)},
    artifacts: ${json(entries)},
  },
  parameters: { layout: 'fullscreen', controls: { disable: true } },
} satisfies Meta<typeof ReviewOverview>

export default meta
type Story = StoryObj<typeof meta>

export const Overview: Story = { name: '案卷首页' }
`
}

function storyDefinition(artifact) {
  const story = artifact.story
  if (!story?.id || !story?.group || !story?.name) {
    throw new Error(`产物 ${artifact.id} 缺少 story.id、story.group 或 story.name`)
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(story.id)) {
    throw new Error(`产物 ${artifact.id} 的 story.id 必须是小写短横线标识`)
  }
  if (!storybookSidebarGroups.some(({ title }) => title === story.group)) {
    throw new Error(`产物 ${artifact.id} 的 story.group 必须使用三个既有一级组之一`)
  }
  return {
    file: `${pascalCase(story.id)}.stories.ts`,
    storyId: story.id,
    title: story.group,
    storyName: story.name,
  }
}

function documentStory(entry, artifact, rendered) {
  const relatedLinks = relatedStoryLinks(artifact.id)
  return generatedHeader() + `import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ReviewDocument from '../../shared/components/ReviewDocument.vue'

const meta = {
  id: ${json(entry.storyId)},
  title: ${json(entry.title)},
  component: ReviewDocument,
  tags: [${json(storybookNoAddonPanelTag)}],
  args: {
    artifact: ${json({
      id: artifact.id,
      title: artifact.title,
      summary: artifact.summary,
      source: artifact.source,
      sourceFile: artifact.sourceFile,
      sourceHash: artifact.sourceHash,
      version: artifact.version,
      reviewStatus: artifact.reviewStatus,
      date: artifact.date,
      reviewDeadline: artifact.reviewDeadline,
    })},
    contentHtml: ${json(rendered.html)},
    toc: ${json(rendered.toc)},
    sourceHref: ${json(`./sources/${artifact.sourceFile}`)},
    relatedLinks: ${json(relatedLinks)},
  },
  parameters: { layout: 'fullscreen', controls: { disable: true } },
} satisfies Meta<typeof ReviewDocument>

export default meta
type Story = StoryObj<typeof meta>

export const Document: Story = { name: ${json(entry.storyName)} }
`
}

function attachmentsStory(manifest) {
  return generatedHeader() + `import type { Meta, StoryObj } from '@storybook/vue3-vite'
import ReviewAttachments from '../../shared/components/ReviewAttachments.vue'

const meta = {
  id: 'attachment-formats',
  title: '文档',
  component: ReviewAttachments,
  tags: [${json(storybookNoAddonPanelTag)}],
  args: {
    manifestId: ${json(manifest.id)},
    manifestSource: ${json(manifest.manifestSource)},
    manifestHash: ${json(manifest.manifestHash)},
    version: ${json(manifest.version)},
    status: ${json(manifest.status)},
    sourceRoot: ${json(manifest.projectRoot)},
    adapters: ${json(manifest.adapters)},
  },
  parameters: { layout: 'fullscreen', controls: { disable: true } },
} satisfies Meta<typeof ReviewAttachments>

export default meta
type Story = StoryObj<typeof meta>

export const Formats: Story = { name: '附件与格式说明' }
`
}

function relatedStoryLinks(id) {
  if (id === 'ui-design') {
    return [{ label: '查看共享设计 Token', href: './?path=/story/design-language--tokens' }]
  }
  if (id === 'product-prototype') {
    return [{ label: '运行草稿状态原型', href: './?path=/story/review-flow--draft' }]
  }
  return []
}

function generatedHeader() {
  return '// 此文件由 scripts/generate.mjs 从共享 manifest 与权威 Markdown 生成，请勿手工修改。\n'
}

function json(value) {
  return JSON.stringify(value, null, 2)
}

function pascalCase(value) {
  return value.split('-').map((part) => part[0].toUpperCase() + part.slice(1)).join('')
}
