import assert from 'node:assert/strict'
import test from 'node:test'
import { extractPrototype, parseDocument, sha256 } from './lib/content.mjs'
import { renderMarkdown } from './lib/markdown.mjs'
import { storybookDocumentHref } from './lib/storybook.mjs'
import { readReviewAnchor, scrollToReviewAnchor } from '../shared/preview-anchor.ts'

test('解析中文文档元数据并保留正文', () => {
  const source = '# 示例\n```meta\nstatus: 评审中\nsummary: 一条摘要\n```\n\n## 正文\n内容'
  const parsed = parseDocument(source)
  assert.equal(parsed.title, '示例')
  assert.equal(parsed.meta.status, '评审中')
  assert.match(parsed.body, /## 正文/)
})

test('普通模板 Markdown 无自定义 meta 围栏也可直接读取', () => {
  const parsed = parseDocument('# 产品需求说明\n\n> 状态：草稿\n\n## 背景与范围\n正文')
  assert.equal(parsed.title, '产品需求说明')
  assert.deepEqual(parsed.meta, {})
  assert.match(parsed.body, /> 状态：草稿/)
})

test('原型数据块必须包含多个状态', () => {
  const source = '```prototype\n{"states":[{"id":"draft"},{"id":"reviewing"},{"id":"changes"},{"id":"approved"}]}\n```'
  assert.equal(extractPrototype(source).states.length, 4)
})

test('摘要哈希稳定', () => {
  assert.equal(sha256('评审'), '66faf426cb2b00b6c70bed868d6d0f7e3e6f73d8fada9e5f8964c9bf4a857fd5')
})

test('Storybook 文档投影保留锚点、目录与局部横向表格', () => {
  const rendered = renderMarkdown('## 一、范围 {#scope}\n\n| 字段 | 说明 |\n|---|---|\n| `id` | 标识 |')
  assert.deepEqual(rendered.toc, [{ level: 2, title: '一、范围', id: 'scope' }])
  assert.match(rendered.html, /<h2 id="scope">一、范围<\/h2>/)
  assert.match(rendered.html, /class="review-table-wrap"/)
  assert.match(rendered.html, /<code>id<\/code>/)
})

test('Storybook 文档投影转义原始 HTML 并显式降级 Mermaid', () => {
  const rendered = renderMarkdown('正文 <script>alert(1)</script>\n\n```mermaid\ngraph TD\n```')
  assert.doesNotMatch(rendered.html, /<script>/)
  assert.match(rendered.html, /&lt;script&gt;/)
  assert.match(rendered.html, /尚未引入运行时渲染器/)
  assert.match(rendered.html, /language-mermaid/)
})

test('Storybook 文档投影区分安全内链、外链和危险协议', () => {
  const rendered = renderMarkdown('[章节](#scope) [官网](https://example.com/a?b=1&c=2) [危险](javascript:alert(1))')
  assert.match(rendered.html, /<a href="#scope">章节<\/a>/)
  assert.match(rendered.html, /<a href="https:\/\/example\.com\/a\?b=1&amp;c=2" target="_blank" rel="noopener noreferrer">官网<\/a>/)
  assert.doesNotMatch(rendered.html, /href="javascript:/)
})

test('Storybook 文档投影拒绝重复标题锚点', () => {
  assert.throws(
    () => renderMarkdown('## 第一节 {#same}\n\n## 第二节 {#same}'),
    /重复的标题锚点：same/,
  )
})

test('Storybook 文档投影支持模板字典锚点和受控相对文档链接', () => {
  const target = storybookDocumentHref('technical-design', 'dict-order-status')
  const rendered = renderMarkdown(
    '字段字典见 [ORDER_STATUS](technical-design.md#dict-order-status)。\n\n<a id="dict-local"></a>\n\n## 本地字典',
    { resolveRelativeLink: (href) => href === 'technical-design.md#dict-order-status' ? target : undefined },
  )
  assert.match(rendered.html, /href="\.\/\?path=\/story\/technical-design--document&amp;reviewAnchor=dict-order-status&amp;reviewTarget=%2Fstory%2Ftechnical-design--document"/)
  assert.match(rendered.html, /target="_top"/)
  assert.match(rendered.html, /id="dict-local"/)
  assert.doesNotMatch(rendered.html, /&lt;a id=/)
})

test('Storybook 跨文档锚点在目标 iframe 挂载后滚动正文元素', () => {
  let scrolled
  let replacedSearch
  const target = { scrollIntoView: (options) => { scrolled = options } }
  const scheduled = scrollToReviewAnchor({
    parentLocation: { search: '?path=/story/technical-design--document&reviewAnchor=dict-order-status&reviewTarget=%2Fstory%2Ftechnical-design--document' },
    documentRef: { getElementById: (id) => id === 'dict-order-status' ? target : null },
    schedule: (callback) => {
      callback(0)
      return 1
    },
    replaceParentSearch: (search) => { replacedSearch = search },
  })

  assert.equal(scheduled, true)
  assert.deepEqual(scrolled, { block: 'start' })
  assert.equal(replacedSearch, 'path=%2Fstory%2Ftechnical-design--document')
  assert.equal(readReviewAnchor({
    search: '?path=/story/technical-design--document&reviewAnchor=bad%2Fanchor&reviewTarget=%2Fstory%2Ftechnical-design--document',
  }), undefined)
})

test('Storybook 跨文档锚点只对链接声明的目标 story 生效', () => {
  let scheduled = false
  const handled = scrollToReviewAnchor({
    parentLocation: { search: '?path=/story/product-requirements--document&reviewAnchor=shared-section&reviewTarget=%2Fstory%2Ftechnical-design--document' },
    documentRef: { getElementById: () => null },
    schedule: () => {
      scheduled = true
      return 1
    },
  })

  assert.equal(handled, false)
  assert.equal(scheduled, false)
})
