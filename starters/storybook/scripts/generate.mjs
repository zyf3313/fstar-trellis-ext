import { mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { basename, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createReviewDataModule, extractPrototype, parseDocument, sha256 } from './lib/content.mjs'
import { readArtifactSource, readTextInside, resolveProjectRoot, validateManifest } from './lib/project.mjs'
import { createStorybookProjection } from './lib/storybook.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const configPath = resolve(root, 'review.config.json')
const configSource = await readFile(configPath, 'utf8')
const config = JSON.parse(configSource)
const projectRoot = resolveProjectRoot(root, config.projectRoot)
const { source: manifestSource } = await readTextInside(root, config.manifest, 'manifest')
const manifest = JSON.parse(manifestSource)
validateManifest(manifest)
const generatedRoot = resolve(root, 'shared/generated')
const storybookGeneratedRoot = resolve(root, 'src/generated')
const storybookPublicSources = resolve(root, 'public/sources')

for (const directory of [generatedRoot, storybookGeneratedRoot, storybookPublicSources]) {
  await rm(directory, { recursive: true, force: true })
  await mkdir(directory, { recursive: true })
}

const artifacts = []
const storybookSources = new Map()
let prototype

for (const item of manifest.artifacts) {
  const artifactSource = await readArtifactSource(projectRoot, item)
  if (!artifactSource) continue
  const { sourcePath, source } = artifactSource
  const parsed = parseDocument(source)
  const resolvedArtifact = {
    ...item,
    title: parsed.title,
    summary: parsed.meta.summary ?? item.summary ?? '打开权威源文档',
    date: parsed.meta.date ?? manifest.updatedAt,
    reviewDeadline: parsed.meta.review_deadline,
    sourceHash: sha256(source),
    sourceFile: `${item.id}-${basename(sourcePath)}`,
  }

  artifacts.push(resolvedArtifact)
  storybookSources.set(item.id, { body: parsed.body })
  await writeFile(resolve(storybookPublicSources, resolvedArtifact.sourceFile), source)

  if (item.id === 'product-prototype') prototype = extractPrototype(source)
}

if (!prototype) throw new Error('manifest 缺少 product-prototype 产物')

const resolvedManifest = {
  ...manifest,
  projectRoot: config.projectRoot,
  manifestSource: config.manifest,
  configHash: sha256(configSource),
  manifestHash: sha256(manifestSource),
  artifacts,
}

await writeFile(resolve(generatedRoot, 'manifest.resolved.json'), `${JSON.stringify(resolvedManifest, null, 2)}\n`)
await writeFile(resolve(generatedRoot, 'prototype.json'), `${JSON.stringify(prototype, null, 2)}\n`)
await writeFile(resolve(generatedRoot, 'review-data.ts'), createReviewDataModule(resolvedManifest, prototype))

for (const [file, content] of createStorybookProjection(resolvedManifest, storybookSources)) {
  await writeFile(resolve(storybookGeneratedRoot, file), content)
}

console.log(`已生成 ${artifacts.length} 份 Storybook 源文件投影与 ${prototype.states.length} 个原型状态。`)
