<template>
  <el-dialog v-model="visible" title="人工修正字幕" width="560px">
    <div class="form-body">
      <el-input v-model="sourceText" type="textarea" :rows="3" placeholder="英文原文" />
      <el-input v-model="targetText" type="textarea" :rows="3" placeholder="中文字幕" />
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存修正</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { SubtitleSegment } from '../../types'

const props = defineProps<{
  modelValue: boolean
  segment: SubtitleSegment | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [payload: { segmentId: string; sourceText?: string; targetText?: string }]
}>()

const sourceText = ref('')
const targetText = ref('')
const saving = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

watch(
  () => props.segment,
  (segment) => {
    sourceText.value = segment?.source || ''
    targetText.value = segment?.target || ''
  },
  { immediate: true },
)

async function save() {
  if (!props.segment) return
  saving.value = true
  try {
    emit('save', {
      segmentId: props.segment.segmentId,
      sourceText: sourceText.value,
      targetText: targetText.value,
    })
    visible.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

:deep(.el-textarea__inner),
:deep(.el-input__wrapper) {
  background: rgba(8, 22, 42, 0.94);
  color: var(--lf-text);
}
</style>
