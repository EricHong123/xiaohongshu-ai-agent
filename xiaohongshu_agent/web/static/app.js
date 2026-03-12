/* global bootstrap */
(() => {
  function safeJsonParse(text) {
    try {
      return JSON.parse(text);
    } catch {
      return null;
    }
  }

  async function apiCall(path, { method = "GET", body, headers, timeoutMs = 30000 } = {}) {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(path, {
        method,
        headers: {
          ...(body ? { "Content-Type": "application/json" } : {}),
          ...(headers || {}),
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: ctrl.signal,
      });
      const text = await res.text();
      const data = safeJsonParse(text) ?? { raw: text };

      // 兼容旧接口：有的只返回 {error: "..."}，有的返回 {success: true}
      const success = typeof data.success === "boolean" ? data.success : res.ok && !data.error;
      if (!success) {
        const errMsg =
          data.error ||
          data.message ||
          (typeof data === "string" ? data : null) ||
          `请求失败: ${res.status}`;
        const e = new Error(errMsg);
        e.status = res.status;
        e.data = data;
        throw e;
      }
      return data;
    } finally {
      clearTimeout(id);
    }
  }

  function toast(message, { variant = "info", title = "提示", delay = 3500 } = {}) {
    const root = document.getElementById("toastRoot");
    if (!root) return;
    const el = document.createElement("div");
    const headerBg =
      variant === "success" ? "bg-success" : variant === "danger" ? "bg-danger" : variant === "warning" ? "bg-warning" : "bg-secondary";
    el.className = "toast text-bg-dark border-0";
    el.role = "status";
    el.ariaLive = "polite";
    el.ariaAtomic = "true";
    el.innerHTML = `
      <div class="toast-header ${headerBg} text-white border-0">
        <strong class="me-auto">${title}</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">${message}</div>
    `;
    root.appendChild(el);
    const t = new bootstrap.Toast(el, { delay });
    el.addEventListener("hidden.bs.toast", () => el.remove());
    t.show();
  }

  function setBusy(el, busy, busyText = "处理中…") {
    if (!el) return;
    if (busy) {
      el.dataset.prevText = el.innerHTML;
      el.disabled = true;
      el.innerHTML = `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>${busyText}`;
    } else {
      el.disabled = false;
      if (el.dataset.prevText) el.innerHTML = el.dataset.prevText;
    }
  }

  async function checkHealth() {
    const text = document.getElementById("appHealthText");
    try {
      const r = await apiCall("/api/health");
      if (text) text.textContent = r.success ? "在线" : "异常";
      toast("后端连接正常", { variant: "success", title: "健康检查" });
    } catch (e) {
      if (text) text.textContent = "离线";
      toast(e.message || "无法连接后端", { variant: "danger", title: "健康检查" });
    }
  }

  // sidebar burger
  const burger = document.getElementById("appBurger");
  const sidebar = document.querySelector(".app-sidebar");
  if (burger && sidebar) {
    burger.addEventListener("click", () => sidebar.classList.toggle("is-open"));
    document.addEventListener("click", (e) => {
      if (window.innerWidth > 980) return;
      if (!sidebar.classList.contains("is-open")) return;
      if (sidebar.contains(e.target) || burger.contains(e.target)) return;
      sidebar.classList.remove("is-open");
    });
  }

  const healthBtn = document.getElementById("appHealthBtn");
  if (healthBtn) {
    healthBtn.addEventListener("click", checkHealth);
  }

  window.App = { apiCall, toast, setBusy };
})();

