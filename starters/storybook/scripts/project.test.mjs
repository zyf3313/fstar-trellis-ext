import assert from 'node:assert/strict'
import { cp, mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'
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

test('ui-design 存在时生成共享设计资产 story 并传入来源证明', () => {
  const uiDesign = {
    id: 'ui-design',
    title: 'UI 设计说明',
    summary: '示例',
    source: 'design/ui/ui-design.md',
    sourceFile: 'ui-design-ui-design.md',
    sourceHash: 'ui-hash',
    version: 'V1',
    reviewStatus: '示例',
    date: '2026-10-17',
    story: { id: 'ui-design-document', group: 'UI 设计语言与资产', name: 'UI 设计说明' },
  }
  const manifest = { title: '示例', artifacts: [uiDesign], adapters: [] }
  const files = createStorybookProjection(
    manifest,
    new Map([['ui-design', { body: '## 设计原则\n示例' }]]),
  )

  assert.equal(files.has('DesignLanguage.stories.ts'), true)
  assert.match(files.get('DesignLanguage.stories.ts'), /id: 'design-language'/)
  assert.match(files.get('DesignLanguage.stories.ts'), /"sourceHash": "ui-hash"/)
  assert.deepEqual(generatedFilesFor(manifest), [...files.keys()])
})

test('manifest 不含 ui-design 时不生成共享设计资产 story', () => {
  const artifact = {
    id: 'product-requirements',
    title: '产品需求说明',
    summary: '示例',
    source: 'docs/product-requirements.md',
    sourceFile: 'product-requirements-product-requirements.md',
    sourceHash: 'hash',
    version: 'V1',
    reviewStatus: '示例',
    date: '2026-10-17',
    story: { id: 'product-requirements', group: '文档', name: '产品需求说明' },
  }
  const manifest = { title: '示例', artifacts: [artifact], adapters: [] }
  const files = createStorybookProjection(
    manifest,
    new Map([['product-requirements', { body: '## 范围\n示例' }]]),
  )

  assert.equal(files.has('DesignLanguage.stories.ts'), false)
  assert.equal(generatedFilesFor(manifest).includes('DesignLanguage.stories.ts'), false)
})

test('真实生成器从已有 UI 输出切换到省略、缺源、恢复时清理旧 story 与下载源', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-optional-ui-'))
  try {
    const starterRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
    for (const name of ['scripts', 'example-project', 'review.config.json', 'review.manifest.json']) {
      await cp(resolve(starterRoot, name), resolve(root, name), { recursive: true })
    }
    const manifestPath = resolve(root, 'review.manifest.json')
    const manifest = JSON.parse(await readFile(manifestPath, 'utf8'))
    const uiDesign = manifest.artifacts.find(({ id }) => id === 'ui-design')
    const sourcePath = resolve(root, 'example-project', uiDesign.source)
    const source = await readFile(sourcePath, 'utf8')
    const generate = () => {
      const result = spawnSync(process.execPath, ['scripts/generate.mjs'], {
        cwd: root, encoding: 'utf8', timeout: 10_000,
      })
      assert.equal(result.error, undefined)
      return result
    }
    const assertOutputs = async (hasUiDesign) => {
      const resolved = JSON.parse(await readFile(resolve(root, 'shared/generated/manifest.resolved.json'), 'utf8'))
      assert.equal(resolved.artifacts.some(({ id }) => id === 'ui-design'), hasUiDesign)
      const stories = await readdir(resolve(root, 'src/generated'))
      for (const file of ['DesignLanguage.stories.ts', 'UiDesignDocument.stories.ts']) {
        assert.equal(stories.includes(file), hasUiDesign, file)
      }
      const sources = await readdir(resolve(root, 'public/sources'))
      assert.equal(sources.some((file) => file.startsWith('ui-design-')), hasUiDesign)
      if (!hasUiDesign) {
        for (const file of stories) {
          assert.doesNotMatch(await readFile(resolve(root, 'src/generated', file), 'utf8'), /ui-design|design-language--tokens/)
        }
        assert.doesNotMatch(await readFile(resolve(root, 'shared/generated/review-data.ts'), 'utf8'), /ui-design/)
      }
    }

    assert.equal(generate().status, 0)
    await assertOutputs(true)
    await writeFile(manifestPath, JSON.stringify({
      ...manifest, artifacts: manifest.artifacts.filter(({ id }) => id !== 'ui-design'),
    }))
    assert.equal(generate().status, 0)
    await assertOutputs(false)

    await writeFile(manifestPath, JSON.stringify(manifest))
    assert.equal(generate().status, 0)
    await assertOutputs(true)
    await rm(sourcePath)
    assert.equal(generate().status, 0)
    await assertOutputs(false)

    await writeFile(sourcePath, `${source}\nSource restored by regression test.\n`)
    assert.equal(generate().status, 0)
    await assertOutputs(true)
    const story = await readFile(resolve(root, 'src/generated/DesignLanguage.stories.ts'), 'utf8')
    assert.ok(story.includes(sha256(await readFile(sourcePath))))

    uiDesign.required = true
    await writeFile(manifestPath, JSON.stringify(manifest))
    await rm(sourcePath)
    const requiredUi = generate()
    assert.equal(requiredUi.status, 1)
    assert.match(requiredUi.stderr, /缺少必需来源 ui-design:/)

    manifest.artifacts = manifest.artifacts.filter(({ id }) => id !== 'ui-design')
    const prototype = manifest.artifacts.find(({ id }) => id === 'product-prototype')
    prototype.required = false
    await writeFile(manifestPath, JSON.stringify(manifest))
    await rm(resolve(root, 'example-project', prototype.source))
    const missingPrototype = generate()
    assert.equal(missingPrototype.status, 1)
    assert.match(missingPrototype.stderr, /manifest 缺少 product-prototype 产物/)
    manifest.artifacts = manifest.artifacts.filter(({ id }) => id !== 'product-prototype')
    await writeFile(manifestPath, JSON.stringify(manifest))
    const omittedPrototype = generate()
    assert.equal(omittedPrototype.status, 1)
    assert.match(omittedPrototype.stderr, /manifest 必须包含 product-prototype 产物/)
  } finally {
    await rm(root, { recursive: true, force: true })
  }
})

test('必需 ui-design 来源缺失时生成前失败', async () => {
  const root = await mkdtemp(resolve(tmpdir(), 'review-required-ui-'))
  try {
    await assert.rejects(
      () => readArtifactSource(root, {
        id: 'ui-design',
        source: 'design/ui/missing.md',
        required: true,
      }),
      /缺少必需来源 ui-design: design\/ui\/missing\.md/,
    )
  } finally {
    await rm(root, { recursive: true, force: true })
  }
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
