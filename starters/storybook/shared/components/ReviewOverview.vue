<script setup lang="ts">
type ArtifactSummary = {
  id: string
  title: string
  summary: string
  version: string
  reviewStatus: string
  source: string
  sourceHash: string
  href: string
}

defineProps<{
  title: string
  version: string
  status: string
  updatedAt: string
  manifestId: string
  manifestSource: string
  manifestHash: string
  sourceRoot: string
  artifacts: readonly ArtifactSummary[]
}>()
</script>

<template>
  <main class="review-dossier">
    <a class="review-skip-link" href="#dossier-artifacts">跳到产物清单</a>
    <header class="dossier-header">
      <div>
        <h1>{{ title }}</h1>
        <p>Storybook 评审门户：在同一侧栏中阅读需求与技术方案、核对设计资产、运行真实原型，并查看验收与附件格式边界。</p>
      </div>
      <aside class="source-proof" aria-label="案卷来源与状态">
        <dl>
          <div><dt>版本</dt><dd>{{ version }}</dd></div>
          <div><dt>评审</dt><dd>{{ status }}</dd></div>
          <div><dt>更新</dt><dd>{{ updatedAt }}</dd></div>
          <div><dt>清单</dt><dd><code>{{ manifestId }}</code></dd></div>
          <div><dt>清单源</dt><dd><code>{{ manifestSource }}</code></dd></div>
          <div><dt>清单哈希</dt><dd><code>{{ manifestHash }}</code></dd></div>
          <div><dt>正文根目录</dt><dd><code>{{ sourceRoot }}</code></dd></div>
        </dl>
      </aside>
    </header>

    <section id="dossier-artifacts" class="dossier-ledger" aria-labelledby="dossier-artifacts-title">
      <div class="dossier-section-heading">
        <h2 id="dossier-artifacts-title">评审产物</h2>
        <p>{{ artifacts.length }} 份正文均由权威 Markdown 生成；版本、状态与完整哈希来自共享 manifest。</p>
      </div>
      <ol>
        <li v-for="(artifact, index) in artifacts" :key="artifact.id">
          <span class="dossier-index" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span>
          <div class="dossier-entry-copy">
            <a :href="artifact.href" target="_top">{{ artifact.title }}</a>
            <p>{{ artifact.summary }}</p>
            <code>{{ artifact.source }}</code>
          </div>
          <dl>
            <div><dt>版本</dt><dd>{{ artifact.version }}</dd></div>
            <div><dt>评审</dt><dd>{{ artifact.reviewStatus }}</dd></div>
            <div><dt>SHA-256</dt><dd><code>{{ artifact.sourceHash }}</code></dd></div>
          </dl>
        </li>
      </ol>
    </section>

    <section class="dossier-experiment" aria-labelledby="dossier-experiment-title">
      <h2 id="dossier-experiment-title">门户职责</h2>
      <p>Storybook 承载项目评审案卷。正文仍由仓库源文件拥有，生成层只负责安全渲染、来源证明和侧栏信息架构。</p>
      <a href="./?path=/story/attachment-formats--formats" target="_top">查看附件与格式说明</a>
    </section>
  </main>
</template>
