import { readdir, readFile } from 'node:fs/promises'
import { extname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(fileURLToPath(new URL('..', import.meta.url)))
const extensions = new Set(['.css', '.html', '.js', '.mjs', '.json', '.md', '.ts', '.vue', '.yaml'])
const ignored = new Set(['node_modules', 'dist', 'generated', 'storybook-static'])
const files = await collect(root)
const failures = []

for (const file of files) {
  const content = await readFile(file, 'utf8')
  const relative = file.slice(root.length + 1)
  if (/\t/.test(content)) failures.push(`${relative}: 包含 Tab 缩进`)
  if (/[ \t]+$/m.test(content)) failures.push(`${relative}: 包含行尾空白`)
  if (/console\.log/.test(content) && !relative.endsWith('generate.mjs') && !relative.endsWith('check.mjs') && !relative.endsWith('lint.mjs')) {
    failures.push(`${relative}: 交付代码包含 console.log`)
  }
  if (!relative.includes('surface-brief.md') && /(^|[>\s])(BACKGROUND|PROBLEM|GOALS)([<\s]|$)/m.test(content)) {
    failures.push(`${relative}: 包含禁用英文眉题`)
  }
}

if (failures.length) {
  console.error(failures.join('\n'))
  process.exit(1)
}
console.log(`静态检查通过：${files.length} 个源文件。`)

async function collect(directory) {
  const result = []
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (ignored.has(entry.name) || entry.name === 'pnpm-lock.yaml') continue
    const full = resolve(directory, entry.name)
    if (entry.isDirectory()) result.push(...await collect(full))
    else if (extensions.has(extname(entry.name))) result.push(full)
  }
  return result
}
