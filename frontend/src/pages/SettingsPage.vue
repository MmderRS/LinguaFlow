<template>
  <section class="lf-page">
    <div class="header lf-panel">
      <div>
        <h2 class="lf-heading">设置与术语库</h2>
        <p class="lf-subheading">当前版本的 provider 选择由后端环境变量控制，这里展示运行态配置，并允许你管理用户术语。</p>
      </div>
      <el-button type="primary" @click="reloadAll">刷新配置</el-button>
    </div>

    <div class="settings-grid">
      <section class="lf-panel settings-card">
        <header>
          <p class="eyebrow">Runtime</p>
          <h3>运行时配置</h3>
        </header>
        <dl>
          <div>
            <dt>当前 ASR</dt>
            <dd>{{ settingsStore.settings?.asr_provider || '加载中' }}</dd>
          </div>
          <div>
            <dt>当前翻译</dt>
            <dd>{{ settingsStore.settings?.translation_provider || '加载中' }}</dd>
          </div>
          <div>
            <dt>支持 ASR</dt>
            <dd>{{ settingsStore.settings?.available_asr_providers.join(', ') || '-' }}</dd>
          </div>
          <div>
            <dt>支持翻译</dt>
            <dd>{{ settingsStore.settings?.available_translation_providers.join(', ') || '-' }}</dd>
          </div>
        </dl>
      </section>

      <section class="lf-panel settings-card">
        <header>
          <p class="eyebrow">Glossary</p>
          <h3>新增术语</h3>
        </header>
        <div class="term-form">
          <el-input v-model="form.domain" placeholder="领域，例如 Remote Sensing" />
          <el-input v-model="form.source" placeholder="英文术语" />
          <el-input v-model="form.target" placeholder="中文译法" />
          <el-button type="primary" @click="createUserTerm">添加术语</el-button>
        </div>
      </section>
    </div>

    <section class="lf-panel glossary-panel">
      <header class="glossary-head">
        <div>
          <p class="eyebrow">Glossary List</p>
          <h3>术语清单</h3>
        </div>
        <el-input v-model="termQuery" placeholder="检索术语" style="max-width: 260px" clearable @change="loadTerms" />
      </header>

      <el-table :data="terms" stripe empty-text="暂无术语">
        <el-table-column prop="domain" label="领域" min-width="160" />
        <el-table-column prop="source" label="英文术语" min-width="220" />
        <el-table-column prop="target" label="中文译法" min-width="220" />
        <el-table-column label="来源" width="110">
          <template #default="scope">
            <el-tag v-if="scope.row.builtin" type="info">内置</el-tag>
            <el-tag v-else type="success">用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <div class="row-actions">
              <el-button text :disabled="scope.row.builtin" @click="startEdit(scope.row)">编辑</el-button>
              <el-button text type="danger" :disabled="scope.row.builtin" @click="removeTerm(scope.row.id)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="editVisible" title="编辑术语" width="520px">
      <div class="term-form">
        <el-input v-model="editForm.domain" placeholder="领域" />
        <el-input v-model="editForm.target" placeholder="中文译法" />
      </div>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { createTerm, deleteTerm, fetchTerms, updateTerm } from '../services/api'
import { useSettingsStore } from '../stores/settings'
import type { TermItem } from '../types'

const settingsStore = useSettingsStore()

const terms = ref<TermItem[]>([])
const termQuery = ref('')
const editVisible = ref(false)
const editingTerm = ref<TermItem | null>(null)

const form = reactive({
  domain: 'General',
  source: '',
  target: '',
})

const editForm = reactive({
  domain: '',
  target: '',
})

onMounted(async () => {
  await reloadAll()
})

async function reloadAll() {
  await settingsStore.load()
  await loadTerms()
}

async function loadTerms() {
  terms.value = await fetchTerms(termQuery.value)
}

async function createUserTerm() {
  if (!form.source.trim() || !form.target.trim()) return
  await createTerm({ ...form })
  form.source = ''
  form.target = ''
  await loadTerms()
}

function startEdit(term: TermItem) {
  editingTerm.value = term
  editForm.domain = term.domain
  editForm.target = term.target
  editVisible.value = true
}

async function submitEdit() {
  if (!editingTerm.value) return
  await updateTerm(editingTerm.value.id, {
    domain: editForm.domain,
    target: editForm.target,
  })
  editVisible.value = false
  await loadTerms()
}

async function removeTerm(termId: number) {
  await deleteTerm(termId)
  await loadTerms()
}
</script>

<style scoped>
.header {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: end;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.settings-card,
.glossary-panel {
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
  margin: 0 0 12px;
}

.settings-card dl {
  display: grid;
  gap: 16px;
}

.settings-card div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(113, 184, 255, 0.12);
}

.settings-card dt {
  color: var(--lf-text-muted);
}

.settings-card dd {
  margin: 0;
  text-align: right;
}

.term-form {
  display: grid;
  gap: 12px;
}

.glossary-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  margin-bottom: 18px;
}

.row-actions {
  display: flex;
  gap: 10px;
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: rgba(113, 184, 255, 0.1);
  --el-table-text-color: var(--lf-text);
  --el-table-header-text-color: var(--lf-text-muted);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.04);
}

@media (max-width: 1080px) {
  .header,
  .glossary-head {
    flex-direction: column;
    align-items: stretch;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
