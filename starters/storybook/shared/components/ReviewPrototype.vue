<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { artifactProvenance, prototypeFixture } from '../generated/review-data'

type StateId = typeof prototypeFixture.states[number]['id']

const props = withDefaults(defineProps<{
  initialState?: StateId
  explorerName?: string
}>(), {
  initialState: 'draft',
  explorerName: '组件浏览器',
})

const activeId = ref<StateId>(props.initialState)
const provenance = artifactProvenance['product-prototype']
const announcement = ref('')
const activeIndex = computed(() => prototypeFixture.states.findIndex(({ id }) => id === activeId.value))
const activeState = computed(() => prototypeFixture.states[activeIndex.value] ?? prototypeFixture.states[0])

watch(() => props.initialState, (value) => {
  activeId.value = value
})

function selectState(id: StateId): void {
  activeId.value = id
  announcement.value = `已切换到${prototypeFixture.states.find((state) => state.id === id)?.label ?? ''}状态`
}

function advance(): void {
  const nextIndex = (activeIndex.value + 1) % prototypeFixture.states.length
  selectState(prototypeFixture.states[nextIndex].id)
}

function reset(): void {
  selectState('draft')
}
</script>

<template>
  <main class="review-prototype">
    <header class="prototype-header">
      <div>
        <h1>{{ prototypeFixture.title }}</h1>
        <p>{{ prototypeFixture.description }}</p>
      </div>
      <aside class="source-proof" aria-label="原型来源">
        <dl>
          <div><dt>运行器</dt><dd>{{ explorerName }}</dd></div>
          <div><dt>数据源</dt><dd><code>{{ provenance.source }}#prototype</code></dd></div>
          <div><dt>模块</dt><dd>{{ provenance.module }}</dd></div>
          <div><dt>版本</dt><dd>{{ provenance.version }}</dd></div>
          <div><dt>评审</dt><dd>{{ provenance.reviewStatus }}</dd></div>
          <div><dt>SHA-256</dt><dd><code>{{ provenance.sourceHash }}</code></dd></div>
        </dl>
      </aside>
    </header>

    <nav class="state-nav" aria-label="原型状态">
      <button
        v-for="state in prototypeFixture.states"
        :key="state.id"
        type="button"
        :aria-pressed="activeId === state.id"
        @click="selectState(state.id)"
      >
        {{ state.label }}
      </button>
    </nav>

    <section class="prototype-panel" :aria-labelledby="`state-${activeState.id}`">
      <span class="state-marker">{{ activeState.label }}</span>
      <h2 :id="`state-${activeState.id}`">{{ activeState.title }}</h2>
      <p>{{ activeState.body }}</p>
      <ul class="fact-list">
        <li v-for="fact in activeState.facts" :key="fact">{{ fact }}</li>
      </ul>
      <div class="prototype-actions">
        <button type="button" @click="advance">{{ activeState.action }}</button>
        <button class="secondary" type="button" :disabled="activeId === 'draft'" @click="reset">恢复初始状态</button>
      </div>
    </section>

    <p class="sr-only" aria-live="polite">{{ announcement }}</p>
  </main>
</template>
