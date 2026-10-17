import { access, readFile, readdir } from 'node:fs/promises'
import { basename, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createReviewDataModule, extractPrototype, parseDocument, sha256 } from './lib/content.mjs'
import { readArtifactSource, readTextInside, resolveProjectRoot, validateManifest } from './lib/project.mjs'
import {
  createStorybookProjection,
  generatedFilesFor,
  storybookNoAddonPanelTag,
  storybookSidebarGroups,
} from './lib/storybook.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const configSource = await readFile(resolve(root, 'review.config.json'), 'utf8')
const config = JSON.parse(configSource)
const projectRoot = resolveProjectRoot(root, config.projectRoot)
const { source: manifestSource } = await readTextInside(root, config.manifest, 'manifest')
const manifest = JSON.parse(manifestSource)
validateManifest(manifest)
const resolvedManifest = JSON.parse(await readFile(resolve(root, 'shared/generated/manifest.resolved.json'), 'utf8'))
const generatedPrototype = JSON.parse(await readFile(resolve(root, 'shared/generated/prototype.json'), 'utf8'))
const sources = new Map()
const expectedArtifacts = []
const checks = []

for (const item of manifest.artifacts) {
  const artifactSource = await readArtifactSource(projectRoot, item)
  if (!artifactSource) continue
  const { sourcePath, source } = artifactSource
  const parsed = parseDocument(source)
  const artifact = {
    ...item,
    title: parsed.title,
    summary: parsed.meta.summary ?? item.summary ?? '打开权威源文档',
    date: parsed.meta.date ?? manifest.updatedAt,
    reviewDeadline: parsed.meta.review_deadline,
    sourceHash: sha256(source),
    sourceFile: `${item.id}-${basename(sourcePath)}`,
  }
  expectedArtifacts.push(artifact)
  sources.set(item.id, { body: parsed.body })
  assert(`${item.id} 来源位于项目根内`, sourcePath.startsWith(`${projectRoot}/`))
  assert(
    `${item.id} 静态来源逐字节一致`,
    await readFile(resolve(root, 'public/sources', artifact.sourceFile), 'utf8') === source,
  )
}

const expectedResolved = {
  ...manifest,
  projectRoot: config.projectRoot,
  manifestSource: config.manifest,
  configHash: sha256(configSource),
  manifestHash: sha256(manifestSource),
  artifacts: expectedArtifacts,
}
assert('resolved manifest 可由当前配置与来源重现', JSON.stringify(resolvedManifest) === JSON.stringify(expectedResolved))

const expectedProjection = createStorybookProjection(expectedResolved, sources)
const actualFiles = (await readdir(resolve(root, 'src/generated'))).sort()
assert(
  '生成 story 清单无缺失或额外文件',
  actualFiles.join(',') === generatedFilesFor(expectedResolved).sort().join(','),
)
assert(
  '静态来源清单无已删除产物的残留文件',
  (await readdir(resolve(root, 'public/sources'))).sort().join(',') ===
    expectedArtifacts.map(({ sourceFile }) => sourceFile).sort().join(','),
)
for (const [file, expected] of expectedProjection) {
  const actual = await readFile(resolve(root, 'src/generated', file), 'utf8')
  assert(`${file} 可逐字节重现`, actual === expected)
  assert(`${file} 不启用 autodocs`, !actual.includes('autodocs'))
}

const prototypeSource = await readArtifactSource(
  projectRoot,
  manifest.artifacts.find(({ id }) => id === 'product-prototype'),
)
assert('原型 fixture 来自权威 prototype 数据块', JSON.stringify(extractPrototype(prototypeSource.source)) === JSON.stringify(generatedPrototype))
assert(
  '运行数据可由当前 manifest 与原型重现',
  await readFile(resolve(root, 'shared/generated/review-data.ts'), 'utf8') === createReviewDataModule(expectedResolved, generatedPrototype),
)

for (const file of ['.storybook/main.ts', '.storybook/preview.ts', 'src/ReviewFlow.stories.ts']) {
  const source = await readFile(resolve(root, file), 'utf8')
  assert(`${file} 不启用 autodocs`, !source.includes('autodocs'))
}

const packageJson = JSON.parse(await readFile(resolve(root, 'package.json'), 'utf8'))
for (const [name, version] of Object.entries(packageJson.devDependencies)) {
  assert(`${name} 使用精确版本`, /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(version))
}
assert('锁文件存在', await exists(resolve(root, 'pnpm-lock.yaml')))
assert('示例明确标注为示例', expectedArtifacts.every(({ reviewStatus }) => reviewStatus === '示例'))
assert('侧栏仅含三个业务一级组', storybookSidebarGroups.map(({ title }) => title).join(',') === '文档,UI 设计语言与资产,可交互原型')
assert(
  '生成的阅读 story 使用统一标签',
  [...expectedProjection.entries()]
    .filter(([file]) => file !== 'DesignLanguage.stories.ts')
    .every(([, source]) => source.includes(storybookNoAddonPanelTag)),
)
assert(
  '共享设计资产保留交互工具',
  !expectedProjection.get('DesignLanguage.stories.ts')?.includes(storybookNoAddonPanelTag),
)

console.log(`一致性检查通过：${checks.length} 项，${expectedArtifacts.length} 份来源。`)

function assert(label, condition) {
  if (!condition) throw new Error(`检查失败：${label}`)
  checks.push(label)
}

async function exists(path) {
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}
