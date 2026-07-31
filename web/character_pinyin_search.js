// 角色选择器拼音首字母搜索（ComfyUI 扩展）
//
// 为二次元角色选择器节点的角色下拉框附加一个拼音首字母搜索框：
//   - 输入中文子串直接匹配（ComfyUI 原生下拉搜索已支持，此处同样生效）
//   - 输入拼音首字母（如 "kl" -> 凯露、"ht" -> 胡桃）也可匹配
// 匹配数据由 tools/generate_pinyin_data.py 生成并随 web/extensions/pinyin_data.js
// 提供（globalThis.__CHARACTER_PINYIN__），本文件在用户交互时才读取该全局量，
// 与数据文件加载顺序无关。
import { app } from "../../scripts/app.js";

const NODE_TYPES = ["AnimeCharacterSelectorCN", "illustrious_character_select"];
const COMBO_WIDGET = "character";
const MAX_RESULTS = 50;
const INPUT_H = 28;
const ROW_H = 20;
const MAX_LIST_H = 160;

function pinyinOf(name) {
  const index = globalThis.__CHARACTER_PINYIN__;
  const entry = index && index[name];
  if (!entry) return { i: "", p: "", c: "" };
  if (typeof entry === "string") return { i: entry, p: "", c: "" }; // 兼容旧格式
  return { i: entry.i || "", p: entry.p || "", c: entry.c || "" };
}

const CJK_RE = /[\u3400-\u9fff\uf900-\ufaff]/;

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
      // 相邻换位：a[i-2]==b[j-1] && a[i-1]==b[j-2]
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

function filterNames(names, query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const ranked = [];
  const maxDist = fuzzyMaxDist(q);
  for (const n of names) {
    const { i, p, c } = pinyinOf(n);
    if (i.startsWith(q)) {
      ranked.push([n, 0]);
      continue;
    }
    if (p.startsWith(q)) {
      ranked.push([n, 1]);
      continue;
    }
    const lower = n.toLowerCase();
    if (CJK_RE.test(q) && lower.includes(q)) {
      ranked.push([n, 2]);
      continue;
    }
    if (lower.includes(q)) {
      ranked.push([n, 3]);
      continue;
    }
    if (i.includes(q) || p.includes(q)) {
      ranked.push([n, 4]);
      continue;
    }
    // 模糊通道（rank 5）：核心拼音错打 / 中文错字 / 全拼错打
    // 对 核心拼音/中文名 的前缀窗口计算距离，支持“部分输入+错打”（如 kongxi -> 空崎）
    let best = -1;
    if (q.length >= 2) {
      const tryWindow = (candidate) => {
        if (!candidate) return;
        const lo = Math.max(1, q.length - maxDist);
        const hi = Math.min(candidate.length, q.length + maxDist);
        for (let L = lo; L <= hi; L++) {
          // 距离 + 长度差惩罚：抑制“前缀相似但明显更短”的噪音候选
          const d = editDistance(candidate.slice(0, L), q) + Math.abs(L - q.length);
          if (d <= maxDist) best = best < 0 ? d : Math.min(best, d);
        }
      };
      tryWindow(c);
      if (best < 0 && CJK_RE.test(q)) tryWindow(lower);
      // 纯拉丁核心条目（如 La Signora（原神））不走模糊：其拉丁名可由通用子串通道直接命中
    }
    if (best >= 0) ranked.push([n, 5, best]);
  }
  ranked.sort((a, b) => a[1] - b[1] || a[2] - b[2] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  return ranked.slice(0, MAX_RESULTS).map(([n]) => n);
}

function buildSearchWidget(node, charWidget) {
  const allNames = charWidget.options?.values || [];
  const container = document.createElement("div");
  container.style.cssText =
    "display:flex;flex-direction:column;gap:2px;width:100%;height:100%;";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "拼音 / 中文 / 模糊搜索…";
  input.spellcheck = false;
  input.style.cssText =
    "flex:0 0 auto;width:100%;box-sizing:border-box;font-size:12px;" +
    "padding:2px 4px;border:1px solid #444;border-radius:3px;" +
    "background:#222;color:#eee;";
  container.appendChild(input);

  const list = document.createElement("div");
  list.style.cssText =
    "flex:1 1 auto;overflow-y:auto;display:none;border:1px solid #333;" +
    "border-radius:3px;background:#1a1a1a;";
  container.appendChild(list);

  let visible = 0;
  function render(items) {
    list.innerHTML = "";
    visible = items.length;
    for (const name of items) {
      const item = document.createElement("div");
      item.textContent = name;
      item.style.cssText =
        "padding:2px 6px;font-size:12px;cursor:pointer;white-space:nowrap;" +
        "overflow:hidden;text-overflow:ellipsis;color:#ddd;";
      item.addEventListener("mouseenter", () => {
        item.style.background = "#2a4a7a";
      });
      item.addEventListener("mouseleave", () => {
        item.style.background = "transparent";
      });
      item.addEventListener("click", () => {
        charWidget.value = name;
        if (typeof charWidget.callback === "function") charWidget.callback(name);
        node.graph?.setDirtyCanvas(true, true);
        list.style.display = "none";
        input.blur();
      });
      list.appendChild(item);
    }
    list.style.display = items.length ? "block" : "none";
  }

  input.addEventListener("input", () => {
    node._pinyinQuery = input.value;
    render(filterNames(allNames, input.value));
    node.setSize([node.size[0], node.size[1]]);
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      list.style.display = "none";
    } else if (e.key === "Enter" && list.firstChild) {
      list.firstChild.click();
    }
  });

  const widget = node.addDOMWidget("pinyin_search", "pinyin", {
    getValue: () => node._pinyinQuery || "",
    setValue: (v) => {
      node._pinyinQuery = v || "";
      if (input.value !== v) input.value = v || "";
    },
  }, { serialize: false });
  widget.computeSize = function () {
    return [Math.max(node.size[0] - 24, 150), INPUT_H + (visible ? Math.min(visible * ROW_H, MAX_LIST_H) + 2 : 0)];
  };
  widget.element = container;
  return widget;
}

app.registerExtension({
  name: "comfy.character_pinyin_search",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!NODE_TYPES.includes(nodeType.comfyClass)) return;
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onNodeCreated?.apply(this, arguments);
      const charWidget = this.widgets?.find((w) => w.name === COMBO_WIDGET);
      if (!charWidget || !Array.isArray(charWidget.options?.values)) return result;
      buildSearchWidget(this, charWidget);
      return result;
    };
  },
});
