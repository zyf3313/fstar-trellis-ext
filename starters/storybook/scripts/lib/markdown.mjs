const blockStart = /^(?:#{2,4}\s|```|<a\s+id="|>\s?|[-*]\s+|\d+\.\s+|\|)/

export function renderMarkdown(body, { resolveRelativeLink } = {}) {
  const lines = body.replace(/\r\n?/g, '\n').split('\n')
  const html = []
  const toc = []
  const headingIds = new Set()

  for (let index = 0; index < lines.length;) {
    const line = lines[index]

    if (!line.trim()) {
      index += 1
      continue
    }

    const explicitAnchor = line.match(/^<a\s+id="([A-Za-z0-9_-]+)"\s*><\/a>\s*$/)
    if (explicitAnchor) {
      const id = explicitAnchor[1]
      if (headingIds.has(id)) throw new Error(`重复的标题锚点：${id}`)
      headingIds.add(id)
      html.push(`<span id="${escapeAttribute(id)}" class="review-explicit-anchor" aria-hidden="true"></span>`)
      index += 1
      continue
    }

    const heading = line.match(/^(#{2,4})\s+(.+?)(?:\s+\{#([A-Za-z0-9_-]+)\})?$/)
    if (heading) {
      const level = heading[1].length
      const title = heading[2].trim()
      const id = heading[3] ?? slugify(title)
      if (headingIds.has(id)) throw new Error(`重复的标题锚点：${id}`)
      headingIds.add(id)
      toc.push({ level, title, id })
      html.push(`<h${level} id="${escapeAttribute(id)}">${renderInline(title, resolveRelativeLink)}</h${level}>`)
      index += 1
      continue
    }

    const fence = line.match(/^```([^\s]*)\s*$/)
    if (fence) {
      const content = []
      index += 1
      while (index < lines.length && !/^```\s*$/.test(lines[index])) {
        content.push(lines[index])
        index += 1
      }
      if (index >= lines.length) throw new Error(`未闭合的代码块：${fence[1] || 'text'}`)
      html.push(renderCodeBlock(fence[1].toLowerCase(), content.join('\n'), resolveRelativeLink))
      index += 1
      continue
    }

    if (line.startsWith('>')) {
      const quoted = []
      while (index < lines.length && lines[index].startsWith('>')) {
        quoted.push(lines[index].replace(/^>\s?/, ''))
        index += 1
      }
      html.push(renderCallout(quoted, resolveRelativeLink))
      continue
    }

    if (isTable(lines, index)) {
      const rows = [splitTableRow(lines[index])]
      index += 2
      while (index < lines.length && /^\|.*\|\s*$/.test(lines[index])) {
        rows.push(splitTableRow(lines[index]))
        index += 1
      }
      html.push(renderTable(rows, resolveRelativeLink))
      continue
    }

    const list = line.match(/^(?:([-*])|(\d+)\.)\s+(.+)$/)
    if (list) {
      const ordered = Boolean(list[2])
      const items = []
      while (index < lines.length) {
        const item = lines[index].match(/^(?:([-*])|(\d+)\.)\s+(.+)$/)
        if (!item || Boolean(item[2]) !== ordered) break
        items.push(item[3])
        index += 1
      }
      const tag = ordered ? 'ol' : 'ul'
      html.push(`<${tag}>${items.map((item) => `<li>${renderInline(item, resolveRelativeLink)}</li>`).join('')}</${tag}>`)
      continue
    }

    const paragraph = [line.trim()]
    index += 1
    while (index < lines.length && lines[index].trim() && !blockStart.test(lines[index])) {
      paragraph.push(lines[index].trim())
      index += 1
    }
    html.push(`<p>${renderInline(paragraph.join(' '), resolveRelativeLink)}</p>`)
  }

  return { html: html.join('\n'), toc }
}

function renderCodeBlock(language, content, resolveRelativeLink) {
  if (language === 'flow') {
    const steps = content.split('\n').filter(Boolean).map((line) => {
      const separator = line.indexOf('|')
      const title = separator < 0 ? line.trim() : line.slice(0, separator).trim()
      const detail = separator < 0 ? '' : line.slice(separator + 1).trim()
      return `<li><strong>${renderInline(title, resolveRelativeLink)}</strong>${detail ? `<span>${renderInline(detail, resolveRelativeLink)}</span>` : ''}</li>`
    })
    return `<ol class="review-flow" aria-label="流程">${steps.join('')}</ol>`
  }

  if (language === 'prototype') {
    return `<details class="review-source-block"><summary>查看原型状态数据</summary><pre><code class="language-json">${escapeHtml(content)}</code></pre></details>`
  }

  if (language === 'mermaid') {
    return `<figure class="review-diagram-fallback"><figcaption>当前 Storybook 实验保留 Mermaid 源码，尚未引入运行时渲染器。</figcaption><pre><code class="language-mermaid">${escapeHtml(content)}</code></pre></figure>`
  }

  const className = language ? ` class="language-${escapeAttribute(language)}"` : ''
  return `<pre><code${className}>${escapeHtml(content)}</code></pre>`
}

function renderCallout(lines, resolveRelativeLink) {
  const marker = lines[0]?.match(/^\[!(IMPORTANT|NOTE|WARNING)\]\s*(.*)$/)
  const labels = { IMPORTANT: '重要', NOTE: '说明', WARNING: '警告' }
  const kind = marker?.[1]?.toLowerCase() ?? 'note'
  const label = marker ? labels[marker[1]] : '说明'
  const content = marker ? [marker[2], ...lines.slice(1)] : lines
  return `<aside class="review-callout review-callout--${kind}"><strong>${label}</strong><p>${renderInline(content.filter(Boolean).join(' '), resolveRelativeLink)}</p></aside>`
}

function isTable(lines, index) {
  return /^\|.*\|\s*$/.test(lines[index] ?? '') && /^\|(?:\s*:?-{3,}:?\s*\|)+\s*$/.test(lines[index + 1] ?? '')
}

function splitTableRow(line) {
  return line.trim().slice(1, -1).split('|').map((cell) => cell.trim())
}

function renderTable(rows, resolveRelativeLink) {
  const [head, ...body] = rows
  return `<div class="review-table-wrap" tabindex="0" role="region" aria-label="可横向滚动的表格"><table><thead><tr>${head.map((cell) => `<th scope="col">${renderInline(cell, resolveRelativeLink)}</th>`).join('')}</tr></thead><tbody>${body.map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell, resolveRelativeLink)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`
}

function renderInline(value, resolveRelativeLink) {
  let result = escapeHtml(value)
  result = result.replace(/\[([^\]]+)\]\((#[A-Za-z0-9_-]+)\)/g, '<a href="$2">$1</a>')
  result = result.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
  )
  result = result.replace(/\[([^\]]+)\]\(([^#/\s][^\s)]*(?:#[A-Za-z0-9_-]+)?)\)/g, (match, label, target) => {
    const href = resolveRelativeLink?.(decodeHtml(target))
    return href ? `<a href="${escapeAttribute(href)}" target="_top">${label}</a>` : match
  })
  result = result.replace(/`([^`]+)`/g, '<code>$1</code>')
  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  return result
}

function decodeHtml(value) {
  return value.replaceAll('&amp;', '&')
}

function slugify(value) {
  const normalized = value.toLowerCase().replace(/[^\p{Letter}\p{Number}]+/gu, '-').replace(/^-|-$/g, '')
  return normalized || 'section'
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll('`', '&#096;')
}
