import { readFile, realpath } from 'node:fs/promises'
import { isAbsolute, relative, resolve } from 'node:path'

export function resolveInside(base, value, label) {
  if (typeof value !== 'string' || !value || isAbsolute(value)) {
    throw new Error(`${label} 必须是非空相对路径`)
  }
  const resolved = resolve(base, value)
  const offset = relative(base, resolved)
  if (offset.startsWith('..') || isAbsolute(offset)) {
    throw new Error(`${label} 不能越出配置根目录：${value}`)
  }
  return resolved
}

export function resolveProjectRoot(reviewRoot, value) {
  if (typeof value !== 'string' || !value || isAbsolute(value)) {
    throw new Error('projectRoot 必须是非空相对路径')
  }
  return resolve(reviewRoot, value)
}

export async function readTextInside(base, value, label) {
  const path = resolveInside(base, value, label)
  const [canonicalBase, canonicalPath] = await Promise.all([realpath(base), realpath(path)])
  const offset = relative(canonicalBase, canonicalPath)
  if (offset.startsWith('..') || isAbsolute(offset)) {
    throw new Error(`${label} 不能通过符号链接越出配置根目录：${value}`)
  }
  return { path: canonicalPath, source: await readFile(canonicalPath, 'utf8') }
}

export async function readArtifactSource(projectRoot, item) {
  const sourcePath = resolveInside(projectRoot, item.source, `artifact ${item.id}`)
  try {
    const [canonicalRoot, canonicalSource] = await Promise.all([
      realpath(projectRoot),
      realpath(sourcePath),
    ])
    const offset = relative(canonicalRoot, canonicalSource)
    if (offset.startsWith('..') || isAbsolute(offset)) {
      throw new Error(`artifact ${item.id} 不能通过符号链接越出项目根目录：${item.source}`)
    }
    return { sourcePath: canonicalSource, source: await readFile(canonicalSource, 'utf8') }
  } catch (error) {
    if (error?.code === 'ENOENT' && item.required === false) return undefined
    if (error?.message?.includes('不能通过符号链接越出项目根目录')) throw error
    throw new Error(`缺少必需来源 ${item.id}: ${item.source}`, { cause: error })
  }
}

export function validateManifest(manifest) {
  if (!manifest || !Array.isArray(manifest.artifacts)) {
    throw new Error('manifest.artifacts 必须是数组')
  }
  if (!Array.isArray(manifest.adapters)) {
    throw new Error('manifest.adapters 必须是数组')
  }

  const artifactIds = new Set()
  const storyIds = new Set()
  for (const item of manifest.artifacts) {
    if (typeof item?.id !== 'string' || !item.id) throw new Error('每个产物必须包含非空 id')
    if (artifactIds.has(item.id)) throw new Error(`产物 id 不能重复：${item.id}`)
    artifactIds.add(item.id)
    if (typeof item.source !== 'string' || !item.source) {
      throw new Error(`产物 ${item.id} 必须包含非空 source`)
    }
    if (typeof item.story?.id !== 'string' || !item.story.id) {
      throw new Error(`产物 ${item.id} 必须包含非空 story.id`)
    }
    if (storyIds.has(item.story.id)) throw new Error(`story.id 不能重复：${item.story.id}`)
    storyIds.add(item.story.id)
  }

  if (!artifactIds.has('product-prototype')) {
    throw new Error('manifest 必须包含 product-prototype 产物')
  }
}
