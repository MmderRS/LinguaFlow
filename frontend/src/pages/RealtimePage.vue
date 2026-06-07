<template>
  <section class="lf-page">
    <div class="toolbar lf-panel">
      <div>
        <div class="toolbar-headline">
          <h2 class="lf-heading">实时翻译控制台</h2>
          <span class="mode-pill" :class="{ 'mode-pill--mock': realtimeStore.isMockAsr }">
            {{ realtimeStore.isMockAsr ? 'Mock ASR 演示模式' : '真实识别模式' }}
          </span>
        </div>
        <p class="lf-subheading">
          会话 ID：{{ realtimeStore.sessionId }}。{{ realtimeStore.isMockAsr ? '演示模式会自动推送模拟会议字幕，不占用麦克风。' : '当前会话会使用真实 ASR provider 处理语音输入。' }}
        </p>
        <div class="provider-switches">
          <label>
            <span>ASR Provider</span>
            <el-select v-model="selectedAsrProvider" size="small" @change="changeAsrProvider">
              <el-option v-for="provider in settingsStore.settings?.available_asr_providers || []" :key="provider" :label="provider" :value="provider" />
            </el-select>
          </label>
        </div>
      </div>

      <div class="toolbar-actions">
        <el-button
          :type="realtimeStore.isMockAsr ? 'default' : 'primary'"
          :disabled="realtimeStore.recording"
          @click="realtimeStore.startRecording()"
        >
          {{ realtimeStore.isMockAsr ? '启动演示' : '开始录音' }}
        </el-button>
        <el-button :disabled="!realtimeStore.recording" @click="realtimeStore.stopRecording()">
          停止录音
        </el-button>
        <el-button @click="realtimeStore.resetSession()">新建会话</el-button>
        <el-button :disabled="realtimeStore.segments.length === 0" @click="exportCurrentSessionTxt">导出 TXT</el-button>
      </div>
    </div>

    <div class="workspace">
      <div class="left-column">
        <section class="lf-panel input-panel">
          <header>
            <p class="eyebrow">Debug Input</p>
            <h3>调试文本注入</h3>
          </header>
          <div v-if="realtimeStore.isMockAsr" class="mock-note">
            当前后端 ASR 是 mock。点击“启动演示”会自动推送模拟字幕，不会请求麦克风。
          </div>
          <p class="lf-subheading">在没有真实音频链路时，可以直接输入英文句子验证字幕、翻译、术语命中和修正逻辑。</p>
          <el-input
            v-model="realtimeStore.debugInput"
            type="textarea"
            :rows="5"
            placeholder="例如：We will focus on remote sensing image analysis today"
          />
          <div class="panel-actions">
            <el-button :type="realtimeStore.isMockAsr ? 'primary' : 'default'" @click="realtimeStore.sendDebugText(realtimeStore.debugInput)">
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
        :is-mock-asr="realtimeStore.isMockAsr"
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
import { ref, watch } from 'vue'

import EditSubtitleDialog from '../components/subtitle/EditSubtitleDialog.vue'
import SubtitlePanel from '../components/subtitle/SubtitlePanel.vue'
import { useRealtimeSession } from '../composables/useRealtimeSession'
import { exportSubtitleSegmentsToTxt } from '../services/subtitleExport'
import type { SubtitleSegment } from '../types'

const { realtimeStore, settingsStore, reconnectRealtimeSession } = useRealtimeSession()

const dialogVisible = ref(false)
const selectedSegment = ref<SubtitleSegment | null>(null)
const selectedAsrProvider = ref('mock')

watch(
  () => settingsStore.settings?.asr_provider,
  (value) => {
    if (value) {
      selectedAsrProvider.value = value
    }
  },
  { immediate: true },
)

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

async function changeAsrProvider(provider: string) {
  await settingsStore.setAsrProvider(provider)
  await reconnectRealtimeSession()
}

function exportCurrentSessionTxt() {
  exportSubtitleSegmentsToTxt(realtimeStore.sessionId, realtimeStore.segments)
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

.toolbar-headline {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.mode-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(35, 178, 111, 0.14);
  color: #86e9b8;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.mode-pill--mock {
  background: rgba(245, 166, 35, 0.16);
  color: #ffd59a;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.workspace {
  display: grid;
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 18px;
  min-height: 0;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 0;
}

.subtitle-column {
  min-height: 0;
}

.input-panel,
.info-panel {
  padding: 24px;
}

.mock-note {
  margin-bottom: 14px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(245, 166, 35, 0.1);
  border: 1px solid rgba(245, 166, 35, 0.2);
  color: #ffd59a;
  line-height: 1.6;
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
