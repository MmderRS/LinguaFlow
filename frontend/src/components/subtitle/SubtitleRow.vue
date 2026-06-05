<template>
  <article class="row">
    <div class="row-head">
      <div>
        <p class="segment-id">{{ segment.segmentId }}</p>
        <h4 class="row-title">双语字幕</h4>
      </div>
      <div class="actions">
        <CorrectionTag v-if="segment.corrected" />
        <el-button size="small" text @click="$emit('edit', segment)">人工修正</el-button>
      </div>
    </div>

    <p class="source">{{ segment.source || '等待识别结果...' }}</p>
    <p class="target">{{ segment.target || '等待翻译结果...' }}</p>

    <div v-if="segment.terms?.length" class="terms">
      <span v-for="term in segment.terms" :key="String(term.source)">
        {{ term.source }} -> {{ term.target }}
      </span>
    </div>
  </article>
</template>

<script setup lang="ts">
import CorrectionTag from './CorrectionTag.vue'
import type { SubtitleSegment } from '../../types'

defineProps<{
  segment: SubtitleSegment
}>()

defineEmits<{
  edit: [segment: SubtitleSegment]
}>()
</script>

<style scoped>
.row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid rgba(113, 184, 255, 0.14);
  background: rgba(255, 255, 255, 0.02);
}

.row-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.segment-id {
  margin: 0 0 4px;
  color: var(--lf-accent-soft);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.row-title {
  margin: 0;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.source,
.target {
  margin: 0;
  line-height: 1.7;
}

.source {
  color: var(--lf-text);
  font-size: 18px;
}

.target {
  color: #8dd6ff;
  font-size: 20px;
  font-weight: 600;
}

.terms {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.terms span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(47, 155, 255, 0.12);
  color: var(--lf-text-muted);
  font-size: 12px;
}

@media (max-width: 768px) {
  .row-head {
    flex-direction: column;
  }
}
</style>
