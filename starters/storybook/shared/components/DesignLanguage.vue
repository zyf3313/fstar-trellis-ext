<script setup lang="ts">
import { artifactProvenance } from '../generated/review-data'

const provenance = artifactProvenance['ui-design']
const tokens = [
  { name: '案卷底色', css: '--review-canvas', value: '#F3F5F4' },
  { name: '纸张', css: '--review-paper', value: '#FFFDF8' },
  { name: '深海军蓝', css: '--review-ink', value: '#10283D' },
  { name: '克制青绿', css: '--review-accent', value: '#1B6B63' },
  { name: '结构线', css: '--review-rule', value: '#C9D3D6' },
] as const
</script>

<template>
  <main class="design-language">
    <header class="design-header">
      <div>
        <h1>评审案卷设计语言</h1>
        <p>评审门户使用同一组颜色、间距、字号、焦点和减少动态效果规则。设计源与代码原型通过稳定 ID 关联，并保持独立所有者。</p>
      </div>
      <aside class="source-proof" aria-label="设计资产来源">
        <dl>
          <div><dt>执行源</dt><dd><code>shared/tokens.css</code></dd></div>
          <div><dt>说明源</dt><dd><code>{{ provenance.source }}</code></dd></div>
          <div><dt>版本</dt><dd>{{ provenance.version }}</dd></div>
          <div><dt>评审</dt><dd>{{ provenance.reviewStatus }}</dd></div>
          <div><dt>SHA-256</dt><dd><code>{{ provenance.sourceHash }}</code></dd></div>
        </dl>
      </aside>
    </header>

    <section class="design-ledger" aria-label="颜色 Token">
      <div v-for="token in tokens" :key="token.css" class="design-row">
        <span class="design-swatch" :style="{ '--swatch': token.value }" aria-hidden="true" />
        <strong>{{ token.name }}</strong>
        <code>{{ token.css }} · {{ token.value }}</code>
      </div>
    </section>
  </main>
</template>
