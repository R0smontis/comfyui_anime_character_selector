// 角色选择器下拉菜单拼音搜索（ComfyUI 扩展）
//
// 思路：不新增自绘搜索框，而是接管 ComfyUI 内建扩展（Comfy.ContextMenuFilter）
// 注入 combo 下拉菜单的默认过滤输入框（input.comfy-context-menu-filter）：
//   - 输入拼音首字母（ht -> 胡桃）、全拼（hutao -> 胡桃）、模糊容错（huato/糊桃 -> 胡桃）、
//     中文子串均可匹配角色中文名
//   - 显示多个匹配候选（最多 100 项），并按匹配质量重排；方向键/Enter/Escape 导航与 Comfy 原生一致
// 实现：cloneNode 替换过滤框以剥离内建 input/keydown 监听器，再绑定拼音/模糊过滤；
// 非中文菜单（英文名等）不接管，继续使用原生逻辑。
// 拼音数据由 tools/generate_pinyin_data.py 生成，见 web/pinyin_data.js
// （globalThis.__CHARACTER_PINYIN__，每条 { i: 首字母, p: 全拼, c: 核心拼音 }）。
import { app } from "../../scripts/app.js";

const CJK_RE = /[\u3400-\u9fff\uf900-\ufaff]/;
const MAX_RESULTS = 100;

function pinyinOf(name) {
  const index = globalThis.__CHARACTER_PINYIN__;
  const entry = index && index[name];
  if (!entry) return { i: "", p: "", c: "" };
  if (typeof entry === "string") return { i: entry, p: "", c: "" }; // 兼容旧格式
  return { i: entry.i || "", p: entry.p || "", c: entry.c || "" };
}

// Damerau-Levenshtein（相邻换位计 1），用于模糊匹配
function editDistance(a, b) {
  if (a === b) return 0;
  const al = a.length;
  const bl = b.length;
  if (!al) return bl;
  if (!bl) return al;
  const prev = new Uint8Array(bl + 1);
  const cur = new Uint8Array(bl + 1);
  for (let j = 0; j <= bl; j++) prev[j] = j;
  for (let i = 1; i <= al; i++) {
    cur[0] = i;
    let prevPrev = prev[0];
    for (let j = 1; j <= bl; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      let v = Math.min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
      if (i > 1 && j > 1 && a[i - 2] === b[j - 1] && a[i - 1] === b[j - 2]) {
        v = Math.min(v, prevPrev + 1);
      }
      cur[j] = v;
      prevPrev = prev[j];
    }
    const t = prev;
    prev.set(cur);
    cur.set(t);
  }
  return prev[bl];
}

function fuzzyMaxDist(q) {
  return q.length <= 4 ? 1 : 2;
}


// 返回按匹配质量排序的名字数组（前 MAX_RESULTS 个）。
// 排序层级：首字母前缀 -> 全拼前缀 -> 直接子串 -> 连续首字母 -> 全拼包含 -> 其他模糊。
function filterNames(names, query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const ranked = [];
  const maxDist = fuzzyMaxDist(q);
  for (const n of names) {
    const { i, p, c } = pinyinOf(n);
    if (i.startsWith(q)) {
      ranked.push([n, 0, 0, 0]);
      continue;
    }
    if (p.startsWith(q)) {
      ranked.push([n, 1, 0, 0]);
      continue;
    }
    const lower = n.toLowerCase();
    if (CJK_RE.test(q) && lower.includes(q)) {
      ranked.push([n, 2, 0, 0]);
      continue;
    }
    if (lower.includes(q)) {
      ranked.push([n, 3, 0, 0]);
      continue;
    }
    // 连续首字母匹配优先：q 必须在角色拼音首字母串 i 中连续出现。
    // 两字符即可启用；首字母前缀已由 rank 0 更早捕获。
    if (q.length >= 2 && i.includes(q)) {
      ranked.push([n, 4, 0, 0]);
      continue;
    }
    // 全拼包含排在连续首字母之后，且保持 >=3 字符以避免短查询噪音。
    if (q.length >= 3 && p.includes(q)) {
      ranked.push([n, 4, 1, 0]);
      continue;
    }
    // 其他模糊（rank 5）：核心拼音 / 中文名前缀窗口 + 长度惩罚。
    let best = -1;
    if (q.length >= 2) {
      const tryWindow = (candidate) => {
        if (!candidate) return;
        const lo = Math.max(1, q.length - maxDist);
        const hi = Math.min(candidate.length, q.length + maxDist);
        for (let L = lo; L <= hi; L++) {
          const d = editDistance(candidate.slice(0, L), q) + Math.abs(L - q.length);
          if (d <= maxDist) best = best < 0 ? d : Math.min(best, d);
        }
      };
      tryWindow(c);
      if (best < 0 && CJK_RE.test(q)) tryWindow(lower);
      // 纯拉丁核心条目（如 La Signora（原神））不走模糊：拉丁名由子串通道直接命中
    }
    if (best >= 0) ranked.push([n, 5, 0, best]);
  }
  ranked.sort(
    (a, b) =>
      a[1] - b[1] || a[2] - b[2] || a[3] - b[3] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0)
  );
  return ranked.slice(0, MAX_RESULTS).map(([n]) => n);
}

// 接管 Comfy.ContextMenuFilter 注入的默认过滤框。
// 做法：cloneNode 替换过滤框（cloneNode 不复制 addEventListener 监听器），
// 从而彻底移除内建扩展绑定的纯子串过滤与键盘导航，改绑我们的实现。
// 返回 true 表示已接管。
function enhanceMenu(ctx, values) {
  if (!ctx || !ctx.root) return false;
  const filter = ctx.root.querySelector(".comfy-context-menu-filter");
  if (!filter) return false;

  const names = values.filter((v) => typeof v === "string");
  if (!names.some((n) => CJK_RE.test(n))) return false; // 非中文菜单：交给原生逻辑

  const items = Array.from(ctx.root.querySelectorAll(".litemenu-entry"));
  if (!items.length) return false;

  // 替换元素以丢弃内建扩展的监听器；克隆保留 class/placeholder 等属性
  const input = filter.cloneNode(true);
  filter.replaceWith(input);

  let displayed = items;
  let count = displayed.length;
  let selectedIndex = 0;
  let selectedItem = displayed[0] ?? null;

  const updateSelected = () => {
    if (selectedItem) {
      selectedItem.style.setProperty("background-color", "");
      selectedItem.style.setProperty("color", "");
    }
    selectedItem = displayed[selectedIndex];
    if (selectedItem) {
      selectedItem.style.setProperty("background-color", "#ccc", "important");
      selectedItem.style.setProperty("color", "#000", "important");
    }
  };

  const applyFilter = (term) => {
    const q = term.trim();
    if (q) {
      // 按匹配质量重排：命中项按 filterNames 顺序移动到菜单顶部
      const orderedNames = filterNames(names, q);
      const itemByName = new Map(items.map((item) => [item.textContent, item]));
      displayed = orderedNames.map((name) => itemByName.get(name)).filter(Boolean);
      const visibleItems = new Set(displayed);
      for (const item of items) item.style.display = visibleItems.has(item) ? "block" : "none";
      for (const item of displayed) ctx.root.appendChild(item);
    } else {
      // 清空查询：恢复原始顺序并全部显示
      for (const item of items) ctx.root.appendChild(item);
      displayed = items;
      for (const item of items) item.style.display = "block";
    }
    selectedIndex = 0;
    if (selectedItem && displayed.includes(selectedItem)) {
      selectedIndex = displayed.findIndex((d) => d === selectedItem);
    }
    count = displayed.length;
    updateSelected();
  };

  input.addEventListener("input", () => applyFilter(input.value));
  input.addEventListener("keydown", (e) => {
    switch (e.key) {
      case "ArrowUp":
        e.preventDefault();
        selectedIndex = selectedIndex === 0 ? count - 1 : selectedIndex - 1;
        updateSelected();
        break;
      case "ArrowDown":
        e.preventDefault();
        selectedIndex = selectedIndex === count - 1 ? 0 : selectedIndex + 1;
        updateSelected();
        break;
      case "ArrowRight":
        e.preventDefault();
        selectedIndex = count - 1;
        updateSelected();
        break;
      case "ArrowLeft":
        e.preventDefault();
        selectedIndex = 0;
        updateSelected();
        break;
      case "Enter":
        selectedItem?.click();
        break;
      case "Escape":
        ctx.close();
        break;
    }
  });

  // 初始化：定位当前选中值对应项（与 Comfy 原生行为一致）并聚焦过滤框
  requestAnimationFrame(() => {
    const currentNode = window.LiteGraph?.LGraphCanvas?.active_canvas?.current_node;
    const clickedValue = currentNode?.widgets
      ?.filter((w) => w.type === "combo" && w.options?.values?.length === values.length)
      .find((w) => w.options.values?.every((v, i) => v === values[i]))?.value;
    const idx = clickedValue ? values.findIndex((v) => v === clickedValue) : -1;
    selectedIndex = idx >= 0 ? idx : 0;
    updateSelected();
    input.focus();
  });

  return true;
}

app.registerExtension({
  name: "comfy.character_pinyin_search",
  init() {
    // 此刻 LiteGraph.ContextMenu 已被 Comfy.ContextMenuFilter 替换为 wrapper
    // （内建扩展先于自定义扩展注册）。包一层：构造完成后接管过滤框。
    const baseContextMenu = LiteGraph.ContextMenu;
    LiteGraph.ContextMenu = function (values, options) {
      const ctx = baseContextMenu(values, options);
      try {
        if (options?.className === "dark") enhanceMenu(ctx, values);
      } catch (err) {
        console.error("[character_pinyin_search] enhance failed:", err);
      }
      return ctx;
    };
    LiteGraph.ContextMenu.prototype = baseContextMenu.prototype;
  },
});
