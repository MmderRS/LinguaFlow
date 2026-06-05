<template>
  <div class="shell">
    <aside class="sidebar lf-panel">
      <div>
        <p class="brand-kicker">AI Real-time Interpretation</p>
        <h1 class="brand-title">LinguaFlow</h1>
        <p class="brand-copy">面向技术会议、在线课程和学术讲座的实时同声传译助手。</p>
      </div>

      <nav class="nav">
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="nav-link">
          <span class="nav-label">{{ item.label }}</span>
          <span class="nav-detail">{{ item.detail }}</span>
        </RouterLink>
      </nav>

      <div class="brand-footer">
        <span>低延迟字幕</span>
        <span>术语优先</span>
        <span>自动修正</span>
      </div>
    </aside>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
const navItems = [
  { path: '/', label: '首页', detail: '项目概览与能力说明' },
  { path: '/realtime', label: '实时翻译', detail: '音频输入、字幕流、修正' },
  { path: '/history', label: '历史记录', detail: '查询、删除、导出 JSON' },
  { path: '/settings', label: '设置', detail: 'Provider 与术语管理' },
]
</script>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  padding: 20px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 28px;
}

.brand-kicker {
  margin: 0 0 8px;
  color: var(--lf-accent-soft);
  font-size: 12px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
}

.brand-title {
  margin: 0;
  font-size: 40px;
  line-height: 1;
}

.brand-copy {
  margin: 14px 0 0;
  color: var(--lf-text-muted);
  line-height: 1.8;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-link {
  display: block;
  padding: 18px;
  border-radius: 18px;
  color: var(--lf-text);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  transform: translateY(-1px);
  background: rgba(54, 137, 255, 0.12);
  border-color: rgba(113, 184, 255, 0.34);
}

.nav-label {
  display: block;
  font-size: 18px;
  font-weight: 600;
}

.nav-detail {
  display: block;
  margin-top: 6px;
  color: var(--lf-text-muted);
  font-size: 13px;
}

.brand-footer {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.brand-footer span {
  border: 1px solid rgba(113, 184, 255, 0.2);
  border-radius: 999px;
  padding: 8px 12px;
  color: var(--lf-text-muted);
  font-size: 12px;
}

.content {
  min-width: 0;
}

@media (max-width: 1080px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    gap: 20px;
  }
}
</style>
