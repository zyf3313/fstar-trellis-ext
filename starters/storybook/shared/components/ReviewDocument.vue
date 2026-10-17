<script setup lang="ts">
import { onMounted } from 'vue'
import { scrollToReviewAnchor } from '../preview-anchor'

type Artifact = {
  id: string
  title: string
  summary: string
  source: string
  sourceFile: string
  sourceHash: string
  version: string
  reviewStatus: string
  date: string
  reviewDeadline: string
}

type TocEntry = { level: number; title: string; id: string }
type RelatedLink = { label: string; href: string }

defineProps<{
  artifact: Artifact
  contentHtml: string
  toc: readonly TocEntry[]
  sourceHref: string
  relatedLinks: readonly RelatedLink[]
}>()

onMounted(() => {
  scrollToReviewAnchor()
})
</script>

<template>
  <main class="review-document-shell">
    <a class="review-skip-link" href="#review-document">跳到正文</a>
    <header class="review-document-header">
      <div class="review-document-heading">
        <h1>{{ artifact.title }}</h1>
        <p>{{ artifact.summary }}</p>
        <nav v-if="relatedLinks.length" class="review-related-links" aria-label="相关资产">
          <a v-for="link in relatedLinks" :key="link.href" :href="link.href" target="_top">{{ link.label }}</a>
        </nav>
      </div>
      <aside class="source-proof" aria-label="来源与评审状态">
        <dl>
          <div><dt>源文件</dt><dd><a :href="sourceHref" target="_blank" rel="noopener noreferrer">{{ artifact.source }}</a></dd></div>
          <div><dt>版本</dt><dd>{{ artifact.version }}</dd></div>
          <div><dt>评审</dt><dd>{{ artifact.reviewStatus }}</dd></div>
          <div><dt>更新</dt><dd>{{ artifact.date }}</dd></div>
          <div><dt>截止</dt><dd>{{ artifact.reviewDeadline }}</dd></div>
          <div><dt>SHA-256</dt><dd><code>{{ artifact.sourceHash }}</code></dd></div>
        </dl>
      </aside>
    </header>

    <div class="review-document-layout">
      <nav class="review-toc" aria-label="本文目录">
        <strong>本文目录</strong>
        <ol>
          <li v-for="entry in toc" :key="entry.id" :class="`toc-level-${entry.level}`">
            <a :href="`#${entry.id}`">{{ entry.title }}</a>
          </li>
        </ol>
      </nav>
      <article id="review-document" class="review-document" v-html="contentHtml" />
    </div>

    <footer class="review-document-footer">
      <strong>投影边界</strong>
      <p>正文由权威 Markdown 在构建时转义并生成。Mermaid 若出现，仅显示可核验源码；本实验不为图表引入额外运行时。</p>
    </footer>
  </main>
</template>
