<template>
  <section class="lf-page">
    <div class="toolbar lf-panel">
      <div>
        <h2 class="lf-heading">实时翻译控制台</h2>
        <p class="lf-subheading">
          会话 ID：{{ realtimeStore.sessionId }}。支持麦克风采集，也支持直接输入英文调试文本模拟实时识别与翻译。
        </p>
      </div>

      <div class="toolbar-actions">
        <el-button type="primary" :disabled="realtimeStore.recording" @click="realtimeStore.startRecording()">
          开始录音
        </el-button>
        <el-button :disabled="!realtimeStore.recording" @click="realtimeStore.stopRecording()">
          停止录音
        </el-button>
        <el-button @click="realtimeStore.resetSession()">新建会话</el-button>
      </div>
    </div>

    <div class="workspace">
      <div class="left-column">
        <section class="lf-panel input-panel">
          <header>
            <p class="eyebrow">Debug Input</p>
            <h3>调试文本注入</h3>
          </header>
          <p class="lf-subheading">在没有真实音频链路时，可以直接输入英文句子验证字幕、翻译、术语命中和修正逻辑。</p>
          <el-input
            v-model="realtimeStore.debugInput"
            type="textarea"
            :rows="5"
            placeholder="例如：We will focus on remote sensing image analysis today"
          />
          <div class="panel-actions">
            <el-button type="primary" @click="realtimeStore.sendDebugText(realtimeStore.debugInput)">
              发送调试文本
            </el-button>
          </div>
        </section>

        <section class="lf-panel info-panel">
          <header>
            <p class="eyebrow">Providers</p>
            <h3>当前后端配置</h3>
          </header>
          <dl>
            <div>
              <dt>ASR</dt>
              <dd>{{ settingsStore.settings?.asr_provider || '加载中' }}</dd>
            </div>
            <div>
              <dt>Translation</dt>
              <dd>{{ settingsStore.settings?.translation_provider || '加载中' }}</dd>
            </div>
            <div>
              <dt>WebSocket</dt>
              <dd>{{ settingsStore.settings?.websocket_path || '/ws/realtime' }}</dd>
            </div>
          </dl>
          <el-alert v-if="realtimeStore.error" :title="realtimeStore.error" type="error" show-icon :closable="false" />
        </section>
      </div>

      <SubtitlePanel
        class="subtitle-column"
        :segments="realtimeStore.segments"
        :partial-text="realtimeStore.partialText"
        :connection-state="String(realtimeStore.connectionState)"
        :connection-detail="realtimeStore.connectionDetail"
        @edit="openCorrectionDialog"
      />
    </div>

    <EditSubtitleDialog
      v-model="dialogVisible"
      :segment="selectedSegment"
      @save="saveCorrection"
    />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import EditSubtitleDialog from '../components/subtitle/EditSubtitleDialog.vue'
import SubtitlePanel from '../components/subtitle/SubtitlePanel.vue'
import { useRealtimeSession } from '../composables/useRealtimeSession'
import type { SubtitleSegment } from '../types'

const { realtimeStore, settingsStore } = useRealtimeSession()

const dialogVisible = ref(false)
const selectedSegment = ref<SubtitleSegment | null>(null)

function openCorrectionDialog(segment: SubtitleSegment) {
  selectedSegment.value = segment
  dialogVisible.value = true
}

async function saveCorrection(payload: { segmentId: string; sourceText?: string; targetText?: string }) {
  await realtimeStore.saveManualCorrection(payload.segmentId, {
    sourceText: payload.sourceText,
    targetText: payload.targetText,
  })
}
</script>

<style scoped>
.toolbar {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: end;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.workspace {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 18px;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-panel,
.info-panel {
  padding: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--lf-accent-soft);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
}

h3 {
  margin: 0 0 10px;
}

.panel-actions {
  margin-top: 16px;
}

.info-panel dl {
  display: grid;
  gap: 16px;
  margin: 18px 0 0;
}

.info-panel div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(113, 184, 255, 0.12);
}

.info-panel dt {
  color: var(--lf-text-muted);
}

.info-panel dd {
  margin: 0;
}

@media (max-width: 1180px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
