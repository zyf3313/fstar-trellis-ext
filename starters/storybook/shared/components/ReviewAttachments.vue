<script setup lang="ts">
type Adapter = {
  kind: string
  renderer: string
  mode: string
  fallback: string
}

defineProps<{
  manifestId: string
  manifestSource: string
  manifestHash: string
  version: string
  status: string
  sourceRoot: string
  adapters: readonly Adapter[]
}>()
</script>

<template>
  <main class="review-attachments">
    <a class="review-skip-link" href="#adapter-table">跳到格式表</a>
    <header class="dossier-header">
      <div>
        <h1>附件与格式说明</h1>
        <p>附件根据格式、来源和哈希选择查看器；无法安全内嵌的文件保留元数据与下载路径。</p>
      </div>
      <aside class="source-proof" aria-label="附件合同来源">
        <dl>
          <div><dt>内容清单</dt><dd><code>{{ manifestId }}</code></dd></div>
          <div><dt>清单源</dt><dd><code>{{ manifestSource }}</code></dd></div>
          <div><dt>清单哈希</dt><dd><code>{{ manifestHash }}</code></dd></div>
          <div><dt>版本</dt><dd>{{ version }}</dd></div>
          <div><dt>评审</dt><dd>{{ status }}</dd></div>
          <div><dt>正文根目录</dt><dd><code>{{ sourceRoot }}</code></dd></div>
        </dl>
      </aside>
    </header>

    <section class="adapter-section" aria-labelledby="adapter-title">
      <div class="dossier-section-heading">
        <h2 id="adapter-title">格式处理规则</h2>
        <p>当前门户展示信息架构与降级说明，不启动 Office 转换服务，也不执行未知文件。</p>
      </div>
      <div id="adapter-table" class="review-table-wrap" tabindex="0" role="region" aria-label="可横向滚动的附件格式表">
        <table>
          <thead><tr><th scope="col">类型</th><th scope="col">默认查看器</th><th scope="col">预览模式</th><th scope="col">降级路径</th></tr></thead>
          <tbody>
            <tr v-for="adapter in adapters" :key="adapter.kind">
              <td><code>{{ adapter.kind }}</code></td>
              <td>{{ adapter.renderer }}</td>
              <td>{{ adapter.mode }}</td>
              <td>{{ adapter.fallback }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="adapter-contract" aria-labelledby="adapter-contract-title">
      <h2 id="adapter-contract-title">统一返回合同</h2>
      <p>每个 adapter 返回格式、源哈希、查看器及其版本、能否内嵌、预览或下载地址和警告。转换后的 Office 预览必须显示转换器版本，不能声称与原格式版式完全一致。</p>
    </section>
  </main>
</template>
