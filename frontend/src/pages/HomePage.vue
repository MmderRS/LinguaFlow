<template>
  <section class="lf-page">
    <div class="hero lf-panel">
      <div>
        <p class="hero-kicker">Conference Copilot</p>
        <h2 class="lf-heading">实时听懂技术会议，而不是在字幕后面追赶。</h2>
        <p class="lf-subheading">
          LinguaFlow 将浏览器音频流转为英文识别结果和中文字幕，支持术语优先、动态修正、历史回看和实时双语字幕。
        </p>
      </div>
      <div class="hero-actions">
        <RouterLink to="/realtime">
          <el-button type="primary" size="large">进入实时翻译</el-button>
        </RouterLink>
        <RouterLink to="/history">
          <el-button size="large">查看历史记录</el-button>
        </RouterLink>
      </div>
    </div>

    <div class="stats-grid">
      <article class="lf-panel stat-card">
        <span class="stat-label">核心能力</span>
        <strong>实时音频 -> ASR -> 翻译</strong>
        <p>WebSocket 实时通信，支持浏览器麦克风采集和调试文本注入。</p>
      </article>
      <article class="lf-panel stat-card">
        <span class="stat-label">字幕体验</span>
        <strong>双语字幕与自动修正</strong>
        <p>保留英文原文，显示中文字幕，历史字幕可被上下文自动修正并显式标记。</p>
      </article>
      <article class="lf-panel stat-card">
        <span class="stat-label">术语策略</span>
        <strong>内置词库 + 用户扩展</strong>
        <p>针对 Remote Sensing、GIS、Deep Learning 等领域优先翻译术语。</p>
      </article>
    </div>

    <div class="timeline lf-panel">
      <div class="timeline-head">
        <h3>当前 MVP 路线</h3>
        <p class="lf-subheading">先用 mock 打通全链路，再替换真实 OpenAI Whisper 与双翻译 provider。</p>
      </div>
      <ol>
        <li>项目结构与 FastAPI/Vue 基础骨架</li>
        <li>实时翻译页与双语字幕系统</li>
        <li>历史记录、设置页与术语管理</li>
        <li>OpenAI Whisper 与 OpenAI/Gemini 翻译接入</li>
      </ol>
    </div>
  </section>
</template>

<style scoped>
.hero {
  padding: 28px;
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
  gap: 24px;
  align-items: end;
}

.hero-kicker {
  margin: 0 0 10px;
  color: var(--lf-accent-soft);
  letter-spacing: 0.24em;
  text-transform: uppercase;
  font-size: 12px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  padding: 24px;
}

.stat-label {
  display: inline-block;
  margin-bottom: 12px;
  color: var(--lf-accent-soft);
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.stat-card strong {
  display: block;
  font-size: 22px;
  margin-bottom: 12px;
}

.stat-card p {
  margin: 0;
  color: var(--lf-text-muted);
  line-height: 1.8;
}

.timeline {
  padding: 28px;
}

.timeline-head {
  margin-bottom: 18px;
}

.timeline h3 {
  margin: 0 0 8px;
}

.timeline ol {
  margin: 0;
  padding-left: 20px;
  display: grid;
  gap: 10px;
  line-height: 1.7;
}

@media (max-width: 1080px) {
  .hero,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
