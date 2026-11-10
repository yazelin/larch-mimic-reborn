# 轉生成寶箱怪的我

Larch 第 4 屆創作者挑戰（主題：神秘小島 3D）的參賽作品。從官方 3D 範例《Pulut 大冒險 3D》remix 出來，場景、模型、角色盡量沿用官方的，主要換掉劇情。玩家是島上的原住民寶箱怪。序章結束後可以選在 3D 小島上自己走，或翻開手繪繪本跟著故事走（繪本模式是 1.2 加的，因為有玩家留言說 3D 不適合、希望有純劇情模式）。

- 玩：https://larch.ink/play/market/12cc23dc-9e1b-428b-9067-0c79d3d32071 （2026-11-10 上架，已報名第四屆創作者挑戰）
- 公開站：https://yazelin.github.io/larch-mimic-reborn/ （`tools/build_site.py` 產生 `index.html` 與 `site/img/`）
- Larch 專案：`project-993a4982-d653-4f55-a511-5950e7fda343`
- 設計方向、改動紀錄與驗證紀錄：`設計.md`；劇本：`劇本/`；上架資料：`劇本/上架.md`

## 現在的作品

白板 `main`：

| 卡片 | 類型 | 內容 |
|---|---|---|
| `sw-intro` | 對話 | 序章：寶箱怪圖鑑、三段回憶、獵人上島 |
| `bk-mode` | 選擇 | 在島上自己走走（3D）／翻開繪本 |
| `sw-world` | 3D 場景 | 整座島：叫醒村口、營地、遺跡的族人，騎火焰飛龍上雲端高台跟冒險隊對決 |
| `bk-*`（46 張） | 對話、選擇、小遊戲、設定變數 | 繪本五章：每句台詞帶自己的 CG；敲三下、島上地圖、接蘋果、高台選招式。`tools/build_book.py` 產生並寫進白板 |
| `sw-ending` | 對話 | 尾聲：蓋子闔上（3D 與繪本共用） |
| `mimic-hero`、`hunter-boy-model`、`hunter-girl-model`、`sw-fox`、`pulut-model` | 3D 模型 | 寶箱怪、少年獵人、少女獵人、卡雅（女孩模型換色）、Pulut |
| `quest-hud` | 3D 介面 | 右上角任務欄 |

連線：`sw-intro` → `bk-mode` →（3D）`sw-world` ／（繪本）`bk-1a` … `bk-5o` → `sw-ending`。圖是 2D 手繪風、介面是手繪水彩（`art/ui/` 的水彩紙卡、名牌、色帶，九宮格貼上）、五首配樂都是自己做的。

## 這個 repo 放什麼

| 路徑 | 內容 |
|---|---|
| `設計.md` | 比賽條件、已定的方向、官方範例裡有什麼可以沿用 |
| `ui/` | Larch 自訂介面（標題、對話框、選項、選單、收藏），手繪水彩版，`tools/push_ui.py` 寫回；舊的黃昏軟糖版留在 `*_jelly*.bak` |
| `book/` | 繪本：`games/` 兩個小遊戲（`tools/build_games.py` 產生）、`book_nodes.json` 產生出來的卡片 |
| `assets/audio/` | 配樂循環版（-16 LUFS） |
| `劇本/` | `大綱.md` 已定的設定與段落，`分段.md` 分段劇情與台詞草稿 |
| `assets/` | 要給 Larch 讀的素材（圖、音樂、3D 模型），說明見 `assets/README.md` |
| `tools/` | 推專案、處理素材的小工具：`upload.py` 傳素材到 Larch 媒體庫（記在 `assets/media.json`）、`art.py` 產圖（走 .11 排隊）、`music.py` 產配樂（.11 gemini-web）、`listen.py` 用 Gemini 代聽配樂 |
| `art/` | `refs/` 參考圖與族人定稿，`cg/` 產出的所有 CG（旁邊的 .json 記提示詞，選上與沒選上的都留著），`book/` 繪本選定的 52 張（對照 `selection.json`），`ui/` 水彩介面素材，`screenshots/` 商店頁截圖 |
| `index.html`、`site/` | 公開站 |
| `snapshots/` | 從 Larch 抓下來的專案快照，只留本機，不提交 |

## 官方範例的起點（revision 14，對照用）

白板 `main` 原本有 7 張卡：

| 卡片 | 類型 | 內容 |
|---|---|---|
| `sw-intro` | 對話 | 序章：Pulut 醒來了 |
| `sw-world` | 3D 場景 | Pulut 大冒險 3D，整座島 |
| `sw-ending` | 對話 | 尾聲：門縫的另一邊 |
| `sw-ending-true` | 對話 | 真結局：一起回家 |
| `sw-elder` | 對話 | 長老的話（場景內播放） |
| `sw-merchant` | 對話 | 市集老闆（場景內播放） |
| `sw-fox` | 3D 模型 | 卡雅 |

連線：`sw-intro` → `sw-world` → `sw-ending`。

## 授權

見 `LICENSE.md`。程式碼 MIT；劇本、設定與原創素材 CC BY-NC 4.0。官方範例的場景、模型與內建素材屬於 Larch。
