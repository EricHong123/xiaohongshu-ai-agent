/* global App */
(() => {
  const $ = (id) => document.getElementById(id);

  function escHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function addChatMessage(role, content) {
    const root = $("chatMessages");
    if (!root) return;
    const wrap = document.createElement("div");
    wrap.className = "mb-2 d-flex " + (role === "user" ? "justify-content-end" : "justify-content-start");
    const bubble = document.createElement("div");
    bubble.className =
      "p-2 px-3 rounded-3 " +
      (role === "user"
        ? "text-bg-primary"
        : "text-bg-dark border border-light border-opacity-10");
    bubble.style.maxWidth = "86%";
    bubble.innerHTML = escHtml(content).replaceAll("\n", "<br/>");
    wrap.appendChild(bubble);
    root.appendChild(wrap);
    root.scrollTop = root.scrollHeight;
  }

  async function onSendChat() {
    const input = $("chatInput");
    const btn = $("chatSendBtn");
    if (!input || !btn) return;
    const msg = input.value.trim();
    if (!msg) return;
    addChatMessage("user", msg);
    input.value = "";
    App.setBusy(btn, true, "发送中…");
    try {
      const r = await App.apiCall("/api/chat", { method: "POST", body: { message: msg } });
      addChatMessage("assistant", r.response || "");
    } catch (e) {
      App.toast(e.message || "请求失败", { variant: "danger", title: "对话" });
      addChatMessage("assistant", "请求失败：" + (e.message || "未知错误"));
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function onSearch() {
    const kw = $("searchKeyword")?.value.trim();
    const btn = $("searchBtn");
    const box = $("searchResults");
    if (!kw) {
      App.toast("请输入关键词", { variant: "warning", title: "搜索" });
      return;
    }
    if (box) box.innerHTML = `<div class="empty">搜索中…</div>`;
    App.setBusy(btn, true, "搜索中…");
    try {
      const r = await App.apiCall("/api/search", { method: "POST", body: { keyword: kw } });
      const posts = r.posts || [];
      if (!posts.length) {
        if (box) box.innerHTML = `<div class="empty">没有找到结果（可能需要先登录 / 启动 MCP）。</div>`;
        return;
      }
      if (box) {
        box.innerHTML = posts
          .slice(0, 12)
          .map(
            (p) => `
            <div class="p-3 rounded-3 mb-2" style="background: rgba(0,0,0,.18); border:1px solid rgba(255,255,255,.10);">
              <div class="fw-semibold">${escHtml(p.title || "无标题")}</div>
              <div class="small muted mt-1">👍 ${p.likes || 0} · 💬 ${p.comments || 0} · ⭐ ${p.collects || 0}</div>
            </div>`
          )
          .join("");
      }
    } catch (e) {
      if (box) box.innerHTML = `<div class="empty">搜索失败：${escHtml(e.message || "未知错误")}</div>`;
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function onGenerate() {
    const kw = $("generateKeyword")?.value.trim();
    const btn = $("generateBtn");
    const panel = $("generateResult");
    if (!kw) {
      App.toast("请输入主题", { variant: "warning", title: "生成内容" });
      return;
    }
    App.setBusy(btn, true, "生成中…");
    try {
      const r = await App.apiCall("/api/generate", { method: "POST", body: { keyword: kw } });
      const c = r.content || {};
      $("generatedTitle").value = c.title || "";
      $("generatedContent").value = c.content || "";
      const tags = c.tags || [];
      const tagRoot = $("generatedTags");
      if (tagRoot) {
        tagRoot.innerHTML = tags
          .slice(0, 12)
          .map((t) => `<span class="badge text-bg-dark border border-light border-opacity-10">#${escHtml(t)}</span>`)
          .join("");
      }
      panel?.classList.remove("d-none");
      App.toast("已生成", { variant: "success", title: "生成内容" });
    } catch (e) {
      App.toast(e.message || "生成失败", { variant: "danger", title: "生成内容" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function onPublish() {
    const btn = $("publishBtn");
    const images = ($("publishImages")?.value || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!images.length) {
      App.toast("请至少提供一张图片路径", { variant: "warning", title: "发布" });
      return;
    }
    App.setBusy(btn, true, "发布中…");
    try {
      await App.apiCall("/api/publish", {
        method: "POST",
        body: {
          title: $("publishTitle")?.value || "",
          content: $("publishContent")?.value || "",
          images,
          tags: ($("publishTags")?.value || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        },
      });
      App.toast("发布请求已提交", { variant: "success", title: "发布" });
    } catch (e) {
      App.toast(e.message || "发布失败", { variant: "danger", title: "发布" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function loadStats() {
    try {
      const r = await App.apiCall("/api/stats");
      const s = r.stats || {};
      $("statPublished").textContent = s.published_posts || 0;
      $("statLikes").textContent = s.total_likes || 0;
      $("statComments").textContent = s.total_comments || 0;
    } catch (e) {
      App.toast(e.message || "获取统计失败", { variant: "danger", title: "统计" });
    }
  }

  async function loadConfig() {
    const providerSel = $("providerSelect");
    const modelSel = $("modelSelect");
    try {
      const r = await App.apiCall("/api/config");
      const providers = r.providers || {};
      const cfg = r.config || {};
      if (providerSel) {
        providerSel.innerHTML = Object.entries(providers)
          .map(([k, v]) => `<option value="${escHtml(k)}">${escHtml(v.name || k)}</option>`)
          .join("");
        providerSel.value = cfg.provider || Object.keys(providers)[0] || "openai";
      }

      const refreshModels = () => {
        const provider = providerSel?.value || cfg.provider;
        const models = providers?.[provider]?.models || [];
        if (!modelSel) return;
        modelSel.innerHTML = models.map((m) => `<option value="${escHtml(m)}">${escHtml(m)}</option>`).join("");
        modelSel.value = cfg.model && models.includes(cfg.model) ? cfg.model : models[0] || "";
      };

      providerSel?.addEventListener("change", refreshModels);
      refreshModels();

      $("mcpUrlInput").value = cfg.mcp_url || "";
    } catch (e) {
      App.toast(e.message || "加载配置失败", { variant: "danger", title: "配置" });
    }
  }

  async function saveConfig() {
    const btn = $("configSaveBtn");
    App.setBusy(btn, true, "保存中…");
    try {
      await App.apiCall("/api/config", {
        method: "POST",
        body: {
          provider: $("providerSelect")?.value,
          model: $("modelSelect")?.value,
          api_key: $("apiKeyInput")?.value,
          mcp_url: $("mcpUrlInput")?.value,
        },
      });
      $("apiKeyInput").value = "";
      App.toast("已保存", { variant: "success", title: "配置" });
    } catch (e) {
      App.toast(e.message || "保存失败", { variant: "danger", title: "配置" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function loadMemory() {
    const box = $("memoryList");
    if (box) box.innerHTML = `<div class="empty">加载中…</div>`;
    try {
      const r = await App.apiCall("/api/memory");
      const items = r.history || [];
      if (!items.length) {
        if (box) box.innerHTML = `<div class="empty">暂无对话记忆。</div>`;
        return;
      }
      if (box) {
        box.innerHTML = items
          .slice(0, 20)
          .map(
            (m) => `
            <div class="p-2 rounded-3 mb-2" style="background: rgba(0,0,0,.18); border:1px solid rgba(255,255,255,.10);">
              <div class="small muted">${escHtml(m.role || "")}</div>
              <div class="small">${escHtml(m.content || "").slice(0, 200)}</div>
            </div>`
          )
          .join("");
      }
    } catch (e) {
      if (box) box.innerHTML = `<div class="empty">加载失败：${escHtml(e.message || "未知错误")}</div>`;
    }
  }

  async function clearMemory() {
    const btn = $("memoryClearBtn");
    if (!confirm("确定清空对话记忆？")) return;
    App.setBusy(btn, true, "清空中…");
    try {
      await App.apiCall("/api/memory/clear", { method: "POST" });
      App.toast("已清空", { variant: "success", title: "记忆" });
      await loadMemory();
    } catch (e) {
      App.toast(e.message || "清空失败", { variant: "danger", title: "记忆" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  // init
  document.addEventListener("DOMContentLoaded", () => {
    addChatMessage("assistant", "你好，我是小红书 AI Agent。你可以直接描述你的需求，我会给你标题、正文与标签建议。");
    $("chatSendBtn")?.addEventListener("click", onSendChat);
    $("chatInput")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") onSendChat();
    });
    $("searchBtn")?.addEventListener("click", onSearch);
    $("searchKeyword")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") onSearch();
    });
    $("generateBtn")?.addEventListener("click", onGenerate);
    $("publishBtn")?.addEventListener("click", onPublish);
    $("statsRefreshBtn")?.addEventListener("click", loadStats);
    $("configSaveBtn")?.addEventListener("click", saveConfig);
    $("memoryRefreshBtn")?.addEventListener("click", loadMemory);
    $("memoryClearBtn")?.addEventListener("click", clearMemory);

    loadStats();
    loadConfig();
    loadMemory();
  });
})();

