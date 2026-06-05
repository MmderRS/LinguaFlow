<template>
  <el-dialog v-model="visible" title="导出历史记录" width="520px">
    <p class="desc">点击下方按钮，在新窗口中导出当前筛选结果的 JSON 数据。</p>
    <el-input :model-value="url" readonly />
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" @click="openUrl">打开导出链接</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  url: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

function openUrl() {
  window.open(props.url, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.desc {
  color: var(--lf-text-muted);
  line-height: 1.8;
}
</style>
