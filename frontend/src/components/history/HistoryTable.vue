<template>
  <section class="lf-panel table-panel">
    <header class="table-head">
      <div>
        <p class="eyebrow">History</p>
        <h3>字幕历史</h3>
      </div>
      <slot name="actions" />
    </header>

    <el-table :data="items" stripe empty-text="暂无历史记录" class="history-table">
      <el-table-column prop="session_id" label="会话" min-width="160" />
      <el-table-column prop="segment_id" label="片段" min-width="120" />
      <el-table-column prop="source_text" label="英文原文" min-width="260" />
      <el-table-column prop="target_text" label="中文字幕" min-width="260" />
      <el-table-column label="修正" width="90">
        <template #default="scope">
          <el-tag v-if="scope.row.corrected" type="warning">已修正</el-tag>
          <span v-else>否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <div class="actions">
            <el-button text type="primary" @click="$emit('edit', scope.row)">修正</el-button>
            <el-button text type="danger" @click="$emit('delete', scope.row.id)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup lang="ts">
import type { HistoryItem } from '../../types'

defineProps<{
  items: HistoryItem[]
}>()

defineEmits<{
  edit: [item: HistoryItem]
  delete: [recordId: number]
}>()
</script>

<style scoped>
.table-panel {
  padding: 24px;
}

.table-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
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
}

.actions {
  display: flex;
  gap: 8px;
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: rgba(113, 184, 255, 0.1);
  --el-table-text-color: var(--lf-text);
  --el-table-header-text-color: var(--lf-text-muted);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.04);
}
</style>
