<template>
  <section class="lf-panel panel">
    <header class="panel-head">
      <div>
        <p class="eyebrow">Live Subtitles</p>
        <h3>实时双语字幕</h3>
      </div>
      <div class="status-box">
        <span class="status-pill" :data-state="connectionState">{{ connectionState }}</span>
        <span class="status-detail">{{ connectionDetail }}</span>
      </div>
    </header>

    <div v-if="partialText" class="partial-box">
      <p class="partial-label">识别中</p>
      <p class="partial-text">{{ partialText }}</p>
    </div>

    <div class="rows">
      <SubtitleRow
        v-for="segment in orderedSegments"
        :key="segment.segmentId"
        :segment="segment"
        @edit="$emit('edit', segment)"
      />
      <div v-if="orderedSegments.length === 0" class="empty-state">当前会话还没有字幕片段。</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { SubtitleSegment } from '../../types'
import SubtitleRow from './SubtitleRow.vue'

const props = defineProps<{
  segments: SubtitleSegment[]
  partialText: string
  connectionState: string
  connectionDetail: string
}>()

defineEmits<{
  edit: [segment: SubtitleSegment]
}>()

const orderedSegments = computed(() => [...props.segments].reverse())
</script>

<style scoped>
.panel {
  padding: 24px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--lf-accent-soft);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
}

h3 {
  margin: 0;
  font-size: 26px;
}

.status-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.status-pill {
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(152, 184, 217, 0.16);
  color: var(--lf-text);
  text-transform: capitalize;
}

.status-pill[data-state='listening'],
.status-pill[data-state='connected'] {
  background: rgba(35, 178, 111, 0.18);
  color: #7fe3b2;
}

.status-detail {
  color: var(--lf-text-muted);
  font-size: 13px;
}

.partial-box {
  padding: 16px 18px;
  margin-bottom: 18px;
  border-radius: 18px;
  background: rgba(47, 155, 255, 0.12);
  border: 1px solid rgba(113, 184, 255, 0.18);
}

.partial-label {
  margin: 0 0 8px;
  color: var(--lf-accent-soft);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.partial-text {
  margin: 0;
  font-size: 18px;
}

.rows {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 720px;
  overflow: auto;
}

.empty-state {
  padding: 32px;
  border-radius: 20px;
  text-align: center;
  color: var(--lf-text-muted);
  background: rgba(255, 255, 255, 0.02);
}

@media (max-width: 768px) {
  .panel-head {
    flex-direction: column;
  }

  .status-box {
    align-items: flex-start;
  }
}
</style>
