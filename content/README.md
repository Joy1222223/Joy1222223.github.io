# 怎麼在網站上加作品

每個作品 = 一個 `.md` 文字檔。放進對應的資料夾，網站就會自動多一頁：

| 資料夾 | 會出現在 |
|---|---|
| `unreal/` | Unreal 頁（有作品後「Coming Soon」會自動換成作品卡片，首頁的 Unreal 卡片也會換成封面圖） |
| `fx/` | FX 頁 |
| `animation/` | Animation 頁 |
| `modeling/` | Modeling 頁 |
| `lighting-compositing/` | Lighting / Compositing 頁 |
| `tools/` | Tools 頁 |

每個新作品都會：在該分類頁多一張卡片、在上方選單的下拉裡多一個連結、有自己的一頁。

## 步驟

1. 複製 `unreal/_template.md`，改成作品的英文名字，例如 `unreal/forest-scene.md`（檔名會變成網址，用英文小寫和 `-`）。
2. 圖片放在旁邊的資料夾，例如 `unreal/forest-scene/cover.jpg`。
3. 打開 `.md` 改內容（格式在下面）。
4. 想要中文版：再複製一份叫 `forest-scene.zh.md`，用繁體中文寫。簡體版會自動轉換。沒有 `.zh.md` 的話，中文版網站會顯示英文內容。

> 檔名開頭是 `_` 的檔案（例如 `_template.md`）不會出現在網站上，可以拿來當草稿。

## 檔案格式

最上面三條 `---` 之間是設定：

```
---
title: Forest Scene          ← 作品標題（卡片和頁面上顯示）
cover: forest-scene/cover.jpg ← 卡片封面，可以是圖片，也可以直接貼 YouTube 連結（會用影片縮圖）
order: 1                     ← 排序，數字小的在前面（可不寫）
hide: yes                    ← 暫時不顯示（可不寫）
home: yes                    ← 只用在 unreal/：首頁的 Unreal 卡片用這個作品的封面（可不寫）
---
```

下面寫內容，規則很簡單：

| 你寫 | 網站上會變成 |
|---|---|
| 一般文字 | 段落（空一行 = 新段落） |
| `## 標題` | 大標題 |
| `### 小標題` | 小標題 |
| `- 項目` | 條列清單 |
| `**粗體**` | **粗體** |
| `[文字](https://網址)` | 連結 |
| 單獨一行貼 YouTube / Vimeo 連結 | 直接嵌入影片播放器 |
| `![](forest-scene/shot1.jpg)` | 圖片（點擊可放大） |
| 連續幾行圖片（中間不空行） | 自動排成圖片牆 |
| `![](forest-scene/clip.mp4)` | 影片（小檔案才行，大影片請放 YouTube） |
| `compare Fresh \| Rotten: forest-scene/a.jpg \| forest-scene/b.jpg` | 滑動比較：左邊 a、右邊 b，拖中間的線比較（兩張圖要一樣大小）。標籤可省略：`compare: a.jpg \| b.jpg` |

## 注意

- **大影片放 YouTube**（可以設「不公開」），再把連結貼進來。GitHub 單一檔案上限是 100 MB。
- 圖片建議先縮到寬 2000px 以內、存成 .jpg 或 .webp，網站會比較快。
- 檔案要存成 UTF-8（VS Code、記事本預設都是）。

## 改完之後

- **在 GitHub 網站上改：** 在 github.com 打開這個資料夾 → `Add file` → 上傳圖片或新增檔案 → `Commit`。大約 1–2 分鐘後網站會自動更新。
- **在自己電腦改：** 在 `gh-site` 資料夾執行 `python _src/build.py` 就能在本機預覽，再上傳到 GitHub。
