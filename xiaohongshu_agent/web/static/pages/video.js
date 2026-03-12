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

  function renderConfigStatus(cfg) {
    const items = [
      { k: "zhipu", label: "智谱 (图片/视频)" },
      { k: "kling", label: "可灵 (可选)" },
      { k: "minimax", label: "MiniMax (脚本/配音，可选)" },
    ];
    return items
      .map((it) => {
        const ok = !!cfg?.[it.k];
        const badge = ok
          ? `<span class="badge text-bg-success">已配置</span>`
          : `<span class="badge text-bg-secondary">未配置</span>`;
        return `<div class="d-flex align-items-center justify-content-between p-2 rounded-3 mb-2" style="background: rgba(0,0,0,.18); border:1px solid rgba(255,255,255,.10);">
          <div class="fw-semibold">${escHtml(it.label)}</div>
          <div>${badge}</div>
        </div>`;
      })
      .join("");
  }

  function getPreviewImages() {
    return Array.from(document.querySelectorAll("#imagePreview img"))
      .map((img) => img.dataset.src || img.src)
      .filter(Boolean);
  }

  function addPreviewImage(src) {
    const root = $("imagePreview");
    if (!root) return;
    const img = document.createElement("img");
    img.src = src;
    img.dataset.src = src;
    img.alt = "预览";
    img.style.width = "86px";
    img.style.height = "86px";
    img.style.objectFit = "cover";
    img.style.borderRadius = "12px";
    img.style.border = "1px solid rgba(255,255,255,.12)";
    img.style.background = "rgba(0,0,0,.25)";
    img.loading = "lazy";
    img.addEventListener("click", () => {
      img.remove();
    });
    root.appendChild(img);
  }

  async function loadConfigStatus() {
    const box = $("configStatus");
    if (box) box.innerHTML = `<div class="empty">加载中…</div>`;
    try {
      const r = await App.apiCall("/api/video/config");
      if (box) box.innerHTML = renderConfigStatus(r.config || {});
    } catch (e) {
      if (box) box.innerHTML = `<div class="empty">加载失败：${escHtml(e.message || "未知错误")}</div>`;
    }
  }

  async function loadVoices() {
    try {
      const r = await App.apiCall("/api/video/voices");
      const voices = r.voices || {};
      const select = $("voice");
      if (!select) return;
      select.innerHTML = "";
      const all = [...(voices.male || []), ...(voices.female || [])];
      (all.length ? all : ["male-qn-qingse"]).forEach((v) => {
        const opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        select.appendChild(opt);
      });
    } catch (e) {
      App.toast(e.message || "加载音色失败", { variant: "danger", title: "音色" });
    }
  }

  async function saveConfig() {
    const btn = $("saveConfigBtn");
    App.setBusy(btn, true, "保存中…");
    try {
      await App.apiCall("/api/video/config", {
        method: "POST",
        body: {
          zhipu_api_key: $("zhipuKey")?.value,
          kling_api_key: $("klingKey")?.value,
          minimax_api_key: $("minimaxKey")?.value,
        },
      });
      ["zhipuKey", "klingKey", "minimaxKey"].forEach((id) => {
        const el = $(id);
        if (el) el.value = "";
      });
      App.toast("已保存", { variant: "success", title: "配置" });
      await loadConfigStatus();
    } catch (e) {
      App.toast(e.message || "保存失败", { variant: "danger", title: "配置" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function testConfig() {
    const btn = $("testConfigBtn");
    App.setBusy(btn, true, "测试中…");
    try {
      const r = await App.apiCall("/api/video/test");
      const status = r.status || {};
      const msg = Object.entries(status)
        .map(([k, v]) => `${k}: ${v}`)
        .join("<br/>");
      App.toast(msg || "OK", { variant: "success", title: "测试连接", delay: 6000 });
    } catch (e) {
      App.toast(e.message || "测试失败", { variant: "danger", title: "测试连接", delay: 6000 });
    } finally {
      App.setBusy(btn, false);
    }
  }

  async function uploadImages() {
    const fileInput = $("imageFile");
    const btn = $("uploadBtn");
    if (!fileInput?.files?.length) {
      App.toast("请选择图片文件", { variant: "warning", title: "上传" });
      return;
    }
    const formData = new FormData();
    for (const f of fileInput.files) formData.append("images", f);
    App.setBusy(btn, true, "上传中…");
    try {
      const res = await fetch("/api/video/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || `上传失败: ${res.status}`);
      (data.paths || []).forEach((p) => addPreviewImage(p));
      fileInput.value = "";
      App.toast("上传成功（点击缩略图可移除）", { variant: "success", title: "上传" });
    } catch (e) {
      App.toast(e.message || "上传失败", { variant: "danger", title: "上传" });
    } finally {
      App.setBusy(btn, false);
    }
  }

  function addUrlImages() {
    const input = $("imageUrls");
    const raw = (input?.value || "").trim();
    if (!raw) return;
    raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .forEach((u) => addPreviewImage(u));
    input.value = "";
  }

  function clearImages() {
    const root = $("imagePreview");
    if (root) root.innerHTML = "";
  }

  async function generateVideo() {
    const btn = $("generateBtn");
    const images = getPreviewImages();
    if (!images.length) {
      App.toast("请先添加至少一张图片", { variant: "warning", title: "生成视频" });
      return;
    }
    App.setBusy(btn, true, "生成中…（可能需要几分钟）");
    $("generateResult")?.classList.add("d-none");
    try {
      const r = await App.apiCall("/api/video/generate", {
        method: "POST",
        body: {
          images,
          product_name: $("productName")?.value || "",
          context: $("context")?.value || "",
          duration: parseInt($("duration")?.value || "10", 10),
          voice: $("voice")?.value || "male-qn-qingse",
          auto_publish: !!$("autoPublish")?.checked,
        },
        timeoutMs: 600000,
      });

      if (r.status !== "completed") {
        throw new Error(r.error || "生成失败");
      }

      const videoUrl = r?.output?.video;
      const meta = $("generateMeta");
      if (meta) {
        meta.innerHTML = `耗时：${Number(r.duration || 0).toFixed(1)}s · 视频：${escHtml(videoUrl || "")}`;
      }

      const wrap = $("resultVideoWrap");
      if (wrap) {
        wrap.innerHTML = videoUrl
          ? `<video controls preload="metadata" src="${escHtml(videoUrl)}"></video>`
          : `<div class="empty">没有返回视频地址</div>`;
      }

      const openBtn = $("resultOpenBtn");
      const dlBtn = $("resultDownloadBtn");
      if (videoUrl) {
        openBtn?.classList.remove("d-none");
        dlBtn?.classList.remove("d-none");
        openBtn.href = videoUrl;
        dlBtn.href = videoUrl;
      }

      $("generateResult")?.classList.remove("d-none");
      App.toast("生成完成", { variant: "success", title: "生成视频" });
      await loadVideoLibrary();
    } catch (e) {
      App.toast(e.message || "生成失败", { variant: "danger", title: "生成视频", delay: 7000 });
    } finally {
      App.setBusy(btn, false);
    }
  }

  function fmtSize(bytes) {
    const mb = bytes / 1024 / 1024;
    if (mb >= 1) return `${mb.toFixed(2)} MB`;
    const kb = bytes / 1024;
    return `${kb.toFixed(0)} KB`;
  }

  async function loadVideoLibrary() {
    const root = $("videoLibrary");
    if (root) root.innerHTML = `<div class="empty">加载中…</div>`;
    try {
      const r = await App.apiCall("/api/video/list");
      const videos = r.videos || [];
      if (!videos.length) {
        if (root) root.innerHTML = `<div class="empty">暂无生成的视频。</div>`;
        return;
      }
      if (root) {
        root.innerHTML = videos
          .slice(0, 12)
          .map((v) => {
            const url = v.url || (v.path ? `/files/${v.path}` : "");
            const time = v.time ? new Date(v.time * 1000).toLocaleString() : "";
            return `
            <div class="p-3 rounded-3 mb-2" style="background: rgba(0,0,0,.18); border:1px solid rgba(255,255,255,.10);">
              <div class="fw-semibold"><i class="bi bi-camera-video"></i> ${escHtml(v.name || "")}</div>
              <div class="small muted mt-1">${escHtml(time)} · ${fmtSize(v.size || 0)}</div>
              <div class="d-flex gap-2 flex-wrap mt-2">
                ${url ? `<a class="btn btn-sm btn-outline-light" href="${escHtml(url)}" target="_blank"><i class="bi bi-play"></i> 播放</a>` : ""}
                ${url ? `<a class="btn btn-sm btn-primary" href="${escHtml(url)}" download><i class="bi bi-download"></i> 下载</a>` : ""}
              </div>
              <div class="small muted mt-2">${escHtml(v.path || "")}</div>
            </div>`;
          })
          .join("");
      }
    } catch (e) {
      if (root) root.innerHTML = `<div class="empty">加载失败：${escHtml(e.message || "未知错误")}</div>`;
    }
  }

  // init
  document.addEventListener("DOMContentLoaded", () => {
    $("uploadBtn")?.addEventListener("click", uploadImages);
    $("addUrlBtn")?.addEventListener("click", addUrlImages);
    $("imageUrls")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") addUrlImages();
    });
    $("clearImagesBtn")?.addEventListener("click", clearImages);
    $("generateBtn")?.addEventListener("click", generateVideo);

    $("saveConfigBtn")?.addEventListener("click", saveConfig);
    $("testConfigBtn")?.addEventListener("click", testConfig);
    $("loadVoicesBtn")?.addEventListener("click", loadVoices);

    $("videoRefreshBtn")?.addEventListener("click", loadVideoLibrary);

    loadConfigStatus();
    loadVoices();
    loadVideoLibrary();
  });

  window.VideoPage = { loadVideoLibrary };
})();

