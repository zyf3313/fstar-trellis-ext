import { createHash } from 'node:crypto'

export function sha256(content) {
  return createHash('sha256').update(content).digest('hex')
}

export function parseDocument(source) {
  const titleMatch = source.match(/^#\s+(.+)$/m)
  const metaMatch = source.match(/```meta\n([\s\S]*?)\n```/)
  if (!titleMatch) throw new Error('文档必须包含一级标题')

  const meta = metaMatch
    ? Object.fromEntries(
      metaMatch[1]
      .split('\n')
      .filter(Boolean)
      .map((line) => {
        const separator = line.indexOf(':')
        if (separator < 1) throw new Error(`无法解析 meta 行：${line}`)
        return [line.slice(0, separator).trim(), line.slice(separator + 1).trim()]
      }),
    )
    : {}

  const body = source
    .replace(titleMatch[0], '')
    .replace(metaMatch?.[0] ?? '', '')
    .trim()

  return { title: titleMatch[1].trim(), meta, body }
}

export function extractPrototype(source) {
  const match = source.match(/```prototype\n([\s\S]*?)\n```/)
  if (!match) throw new Error('原型源文档缺少 prototype 数据块')
  const prototype = JSON.parse(match[1])
  if (!Array.isArray(prototype.states) || prototype.states.length < 2) {
    throw new Error('原型至少需要两个可操作状态')
  }
  const stateIds = prototype.states.map(({ id }) => id)
  if (stateIds.some((id) => typeof id !== 'string' || !id)) {
    throw new Error('每个原型状态必须包含非空 id')
  }
  if (new Set(stateIds).size !== stateIds.length) {
    throw new Error('原型状态 id 不能重复')
  }
  for (const requiredId of ['draft', 'reviewing', 'changes', 'approved']) {
    if (!stateIds.includes(requiredId)) {
      throw new Error(`默认四状态入口缺少原型状态：${requiredId}`)
    }
  }
  return prototype
}

export function createReviewDataModule(manifest, prototype) {
  const artifactProvenance = Object.fromEntries(manifest.artifacts.map((artifact) => [artifact.id, {
    module: artifact.module,
    source: artifact.source,
    sourceFile: artifact.sourceFile,
    sourceHash: artifact.sourceHash,
    version: artifact.version,
    reviewStatus: artifact.reviewStatus,
  }]))

  return `// 此文件由 scripts/generate.mjs 从共享 manifest 与权威 Markdown 生成，请勿手工修改。\nexport const prototypeFixture = ${JSON.stringify(prototype, null, 2)} as const\n\nexport const artifactProvenance = ${JSON.stringify(artifactProvenance, null, 2)} as const\n`
}
