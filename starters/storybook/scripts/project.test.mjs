import assert from 'node:assert/strict'
import { mkdtemp, mkdir, readFile, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import test from 'node:test'
import { parseDocument, sha256 } from './lib/content.mjs'
import { readArtifactSource, readTextInside, resolveInside, resolveProjectRoot, validateManifest } from './lib/project.mjs'
import { createStorybookProjection, generatedFilesFor } from './lib/storybook.mjs'

test('必需来源缺失时给出产物 ID 与相对路径', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-source-'))
  try {
    await assert.rejects(
      () => readArtifactSource(root, { id: 'prd', source: 'docs/missing.md', required: true }),
      /缺少必需来源 prd: docs\/missing\.md/,
    )
  } finally {
    await rm(root, { recursive: true, force: true })
  }
})

test('可选来源缺失时跳过对应入口且不生成空 story', async () => {
  const missing = await readArtifactSource(
    resolve(tmpdir(), 'review-optional-source'),
    { id: 'technical-design', source: 'docs/optional.md', required: false },
  )
  assert.equal(missing, undefined)

  const manifest = {
    title: '示例',
    artifacts: [{
      id: 'product-requirements',
      title: '产品需求说明',
      summary: '示例',
      source: 'docs/product-requirements.md',
      sourceFile: 'product-requirements-product-requirements.md',
      sourceHash: 'hash',
      version: 'V1',
      reviewStatus: '示例',
      date: '2026-10-17',
      reviewDeadline: '2026-10-24',
      story: { id: 'product-requirements', group: '文档', name: '产品需求说明' },
    }],
    adapters: [],
  }
  const sources = new Map([['product-requirements', { body: '## 范围\n示例' }]])
  const files = createStorybookProjection(manifest, sources)
  assert.deepEqual([...files.keys()], ['Overview.stories.ts', 'ProductRequirements.stories.ts', 'Attachments.stories.ts'])
  assert.deepEqual(generatedFilesFor(manifest), [...files.keys()])
})

test('源文件修改会改变页面使用的 SHA-256', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-hash-'))
  try {
    await mkdir(resolve(root, 'docs'), { recursive: true })
    const path = resolve(root, 'docs/source.md')
    await writeFile(path, '# 示例\n```meta\ndate: 2026-10-17\nreview_deadline: 2026-10-24\nsummary: 示例\n```\n\n正文 A\n')
    const first = await readFile(path, 'utf8')
    await writeFile(path, first.replace('正文 A', '正文 B'))
    const second = await readFile(path, 'utf8')
    assert.notEqual(sha256(first), sha256(second))
    assert.equal(parseDocument(second).body, '正文 B')
  } finally {
    await rm(root, { recursive: true, force: true })
  }
})

test('项目根允许指向 review 上级，来源仍拒绝绝对路径和目录逃逸', () => {
  assert.equal(resolveProjectRoot('/tmp/project/review', '..'), '/tmp/project')
  assert.throws(() => resolveProjectRoot('/tmp/review', '/tmp/project'), /相对路径/)
  assert.throws(() => resolveInside('/tmp/project', '../secret', 'artifact source'), /越出配置根目录/)
})

test('来源拒绝通过符号链接越出项目根目录', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-symlink-root-'))
  const outside = await mkdtemp(resolve(tmpdir(), 'review-symlink-outside-'))
  try {
    await writeFile(resolve(outside, 'secret.md'), '# 外部文件')
    await symlink(resolve(outside, 'secret.md'), resolve(root, 'linked.md'))
    await assert.rejects(
      () => readArtifactSource(root, { id: 'linked', source: 'linked.md', required: true }),
      /不能通过符号链接越出项目根目录/,
    )
  } finally {
    await rm(root, { recursive: true, force: true })
    await rm(outside, { recursive: true, force: true })
  }
})

test('manifest 拒绝通过符号链接越出 review 配置根目录', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-manifest-root-'))
  const outside = await mkdtemp(resolve(tmpdir(), 'review-manifest-outside-'))
  try {
    await writeFile(resolve(outside, 'manifest.json'), '{}')
    await symlink(resolve(outside, 'manifest.json'), resolve(root, 'review.manifest.json'))
    await assert.rejects(
      () => readTextInside(root, 'review.manifest.json', 'manifest'),
      /manifest 不能通过符号链接越出配置根目录/,
    )
  } finally {
    await rm(root, { recursive: true, force: true })
    await rm(outside, { recursive: true, force: true })
  }
})

test('manifest 拒绝重复产物 ID 和重复 story ID', () => {
  const base = {
    adapters: [],
    artifacts: [
      { id: 'product-prototype', source: 'prototype.md', story: { id: 'prototype-document' } },
      { id: 'prd', source: 'prd.md', story: { id: 'product-requirements' } },
    ],
  }
  assert.doesNotThrow(() => validateManifest(base))
  assert.throws(
    () => validateManifest({ ...base, artifacts: [...base.artifacts, { ...base.artifacts[1] }] }),
    /产物 id 不能重复：prd/,
  )
  assert.throws(
    () => validateManifest({
      ...base,
      artifacts: [...base.artifacts, { id: 'other', source: 'other.md', story: { id: 'product-requirements' } }],
    }),
    /story.id 不能重复：product-requirements/,
  )
})
