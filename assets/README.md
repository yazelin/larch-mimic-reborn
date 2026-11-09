# 素材

Larch 透過 jsDelivr 讀這裡的檔案，網址格式：

```
https://cdn.jsdelivr.net/gh/yazelin/larch-mimic-reborn@<tag>/<路徑>
```

- jsDelivr 會算整個 ref 的大小，超過 50 MB 就回 403。素材多起來之後改用每類一組的孤兒 tag（做法同 larch-three-gentlemen 的 `tools/assets.py`），不直接用 commit SHA。
- 圖片轉 WebP 再提交，原始大圖不進 repo。
- 3D 模型用 `.glb`，提交前先壓過面數與貼圖尺寸。
- 每個素材的來源與授權記在 `CREDITS.md`。
