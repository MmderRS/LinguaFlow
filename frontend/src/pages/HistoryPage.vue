<template>
  <section class="lf-page">
    <div class="filters lf-panel">
      <div>
        <h2 class="lf-heading">历史记录</h2>
        <p class="lf-subheading">查询、删除、导出历史字幕，并支持对历史片段继续发起人工修正。</p>
      </div>

      <div class="filter-grid">
        <el-input v-model="historyStore.query" placeholder="关键词检索英文或中文" clearable />
        <el-input v-model="historyStore.sessionId" placeholder="按会话 ID 过滤" clearable />
        <el-button type="primary" @click="historyStore.load()">查询</el-button>
        <el-button :disabled="historyStore.items.length === 0" @click="exportCurrentHistoryTxt">导出 TXT</el-button>
        <el-button @click="openExportDialog">导出 JSON</el-button>
      </div>
    </div>

    <HistoryTable :items="historyStore.items" @delete="historyStore.removeRecord" @edit="editHistoryItem">
      <template #actions>
        <el-button v-if="historyStore.sessionId" type="danger" plain @click="historyStore.removeSession(historyStore.sessionId)">
          删除当前会话
        </el-button>
      </template>
    </HistoryTable>

    <div class="pagination lf-panel">
      <el-pagination
        layout="prev, pager, next, total"
        :total="historyStore.total"
        :page-size="historyStore.pageSize"
        :current-page="historyStore.page"
        @current-change="handlePageChange"
      />
    </div>

    <EditSubtitleDialog
      v-model="dialogVisible"
      :segment="selectedSegment"
      @save="saveCorrection"
    />
    <ExportDialog v-model="exportDialogVisible" :url="exportUrl" />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ExportDialog from '../components/history/ExportDialog.vue'
import HistoryTable from '../components/history/HistoryTable.vue'
import EditSubtitleDialog from '../components/subtitle/EditSubtitleDialog.vue'
import { exportHistoryUrl } from '../services/api'
import { exportHistoryItemsToTxt } from '../services/subtitleExport'
import { useHistoryStore } from '../stores/history'
import { useRealtimeStore } from '../stores/realtime'
import type { HistoryItem, SubtitleSegment } from '../types'

const historyStore = useHistoryStore()
const realtimeStore = useRealtimeStore()

const dialogVisible = ref(false)
const exportDialogVisible = ref(false)
const selectedSegment = ref<SubtitleSegment | null>(null)

const exportUrl = computed(() =>
  exportHistoryUrl({
    query: historyStore.query || undefined,
    sessionId: historyStore.sessionId || undefined,
  }),
)

onMounted(() => {
  historyStore.load()
})

function handlePageChange(page: number) {
  historyStore.page = page
  historyStore.load()
}

function editHistoryItem(item: HistoryItem) {
  realtimeStore.sessionId = item.session_id
  selectedSegment.value = {
    segmentId: item.segment_id,
    source: item.source_text,
    target: item.target_text,
    corrected: item.corrected,
    isFinal: true,
    recordId: item.id,
  }
  dialogVisible.value = true
}

async function saveCorrection(payload: { segmentId: string; sourceText?: string; targetText?: string }) {
  await realtimeStore.saveManualCorrection(payload.segmentId, {
    sourceText: payload.sourceText,
    targetText: payload.targetText,
  })
  await historyStore.load()
}

function openExportDialog() {
  exportDialogVisible.value = true
}

function exportCurrentHistoryTxt() {
  exportHistoryItemsToTxt(historyStore.items, historyStore.sessionId || historyStore.query || 'history')
}
</script>

<style scoped>
.filters {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: end;
}

.filter-grid {
  display: grid;
  grid-template-columns: 220px 220px auto auto auto;
  gap: 10px;
  align-items: center;
}

.pagination {
  padding: 18px 24px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1180px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
