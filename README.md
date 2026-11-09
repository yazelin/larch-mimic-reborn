# 轉生成寶箱怪的我

Larch 第 4 屆創作者挑戰（主題：神秘小島 3D）的參賽作品。從官方 3D 範例《Pulut 大冒險 3D》remix 出來，場景、模型、角色盡量沿用官方的，主要換掉劇情。玩家是島上的原住民寶箱怪，一輪大約 10 分鐘玩完。

- 玩：https://larch.ink/play/market/12cc23dc-9e1b-428b-9067-0c79d3d32071 （2026-11-10 上架，版本 1.0.1，已報名第四屆創作者挑戰）
- Larch 專案：`project-993a4982-d653-4f55-a511-5950e7fda343`
- 設計方向、改動紀錄與驗證紀錄：`設計.md`；劇本：`劇本/`；上架資料：`劇本/上架.md`

## 現在的作品

白板 `main`：

| 卡片 | 類型 | 內容 |
|---|---|---|
| `sw-intro` | 對話 | 序章：大家快醒醒（開場 CG、清晨村口、3D 獵人與寶箱怪上舞台播動作） |
| `sw-world` | 3D 場景 | 整座島：叫醒村口、營地、遺跡的族人，騎火焰飛龍上雲端高台跟冒險隊對決 |
| `sw-ending` | 對話 | 尾聲：蓋子闔上 |
| `mimic-hero`、`hunter-boy-model`、`hunter-girl-model`、`sw-fox` | 3D 模型 | 寶箱怪、少年獵人、少女獵人、卡雅 |
| `quest-hud` | 3D 介面 | 右上角任務欄 |

連線：`sw-intro` → `sw-world` → `sw-ending`。圖是 2D 手繪風、介面是「黃昏軟糖」、五首配樂都是自己做的。

## 這個 repo 放什麼

| 路徑 | 內容 |
|---|---|
| `設計.md` | 比賽條件、已定的方向、官方範例裡有什麼可以沿用 |
| `ui/` | Larch 自訂介面（標題、對話框、選項、選單、收藏），`tools/push_ui.py` 寫回 |
| `assets/audio/` | 配樂循環版（-16 LUFS） |
| `劇本/` | `大綱.md` 已定的設定與段落，`分段.md` 分段劇情與台詞草稿 |
| `assets/` | 要給 Larch 讀的素材（圖、音樂、3D 模型），說明見 `assets/README.md` |
| `tools/` | 推專案、處理素材的小工具：`upload.py` 傳素材到 Larch 媒體庫（記在 `assets/media.json`）、`art.py` 產圖（走 .11 排隊）、`music.py` 產配樂（.11 gemini-web）、`listen.py` 用 Gemini 代聽配樂 |
| `art/` | `refs/` 從遊戲裡拍的參考圖，`cg/` 產出的 CG 與標題圖（旁邊的 .json 記提示詞），`screenshots/` 商店頁的 6 張截圖 |
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
