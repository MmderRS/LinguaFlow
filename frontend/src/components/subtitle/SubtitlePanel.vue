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

    <div v-if="isMockAsr" class="mock-banner">
      <strong>当前为 Mock ASR 演示模式</strong>
      <span>录音不会转写你的真实语音，字幕会显示模拟识别结果。请切换到 faster-whisper 或 openai 后再进行真实识别。</span>
    </div>

    <div v-if="partialText" class="partial-box" :class="{ 'partial-box--mock': isMockAsr }">
      <p class="partial-label">{{ isMockAsr ? '模拟识别输出' : '实时识别中' }}</p>
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
  isMockAsr: boolean
}>()

defineEmits<{
  edit: [segment: SubtitleSegment]
}>()

const orderedSegments = computed(() => [...props.segments].reverse())
</script>

<style scoped>
.panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  min-height: 0;
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

.mock-banner {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  margin-bottom: 18px;
  border-radius: 18px;
  background: rgba(245, 166, 35, 0.12);
  border: 1px solid rgba(245, 166, 35, 0.24);
  color: #ffd9a5;
}

.mock-banner strong {
  font-size: 14px;
}

.mock-banner span {
  line-height: 1.6;
  font-size: 13px;
}

.partial-box {
  padding: 16px 18px;
  margin-bottom: 18px;
  border-radius: 18px;
  background: rgba(47, 155, 255, 0.12);
  border: 1px solid rgba(113, 184, 255, 0.18);
}

.partial-box--mock {
  background: rgba(245, 166, 35, 0.08);
  border-color: rgba(245, 166, 35, 0.18);
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
  flex: 1;
  min-height: 0;
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
