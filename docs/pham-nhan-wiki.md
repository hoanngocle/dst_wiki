# Phàm Nhân Tu Tiên runtime wiki

Nguồn chuẩn là snapshot `data/generated/pham-nhan-items.json`, dựng trực tiếp từ `mods/PhamNhanTuTien`; catalog cũ và JSON Solo không được dùng để quyết định item hay công thức.

```powershell
& 'C:\Users\NYX\AppData\Local\Programs\Python\Python313\python.exe' tools/build_pham_nhan_items.py
& 'C:\Users\NYX\AppData\Local\Programs\Python\Python313\python.exe' tools/build_pham_nhan_items.py --check
```

Builder đi từ `modmain.lua`, lưu hash và evidence theo registration. `--check` chỉ so byte, không ghi file. Metadata chỉ được dùng để bổ sung thông tin đã có evidence; không phải nguồn membership. Báo cáo cạnh snapshot liệt kê candidate, exclusion, unresolved và icon chưa có. Builder catalog cũ không cập nhật dữ liệu Phàm Nhân mới.

Tình trạng hiện hành: resolver icon không thay atlas element bằng icon tùy ý; item không resolve sprite vẫn được giữ kèm diagnostic. Cần hoàn tất decoder/atlas publication trước khi coi coverage asset là đạt.
