# Báo cáo nhập toàn bộ skin vật phẩm đã sở hữu — Tu Tiên Ký

## Kết quả

Tu Tiên Ký hiện đăng ký **179 lựa chọn skin trên 40 prefab gốc**. Con số này gồm **95 bộ hình ảnh khác nhau**: 42 mẫu vũ khí dùng chung được đăng ký cho ba pháp kiếm có alias nguồn xác nhận, nên tạo 126 lựa chọn nhưng chỉ dùng 42 bộ tài nguyên. So với mốc hiệu lực ban đầu 32 lựa chọn (31 trong JSON cộng `ttt_portal_gcsz` chỉ có trong Lua), đợt này thêm **147 lựa chọn**, tương ứng **63 bộ hình ảnh mới**.

Các nhóm mới gồm:

- Ba mẫu công trình bị importer cũ bỏ sót: `ttk_hmsw_skins_bzxw`, `ttk_tree_xhs_skins_lgs`, `ttk_yhsyz_skins_qlyyz`.
- Mười mẫu giáp/mũ: năm mẫu `ttk_zcmj` và năm mẫu `ttk_xshj`. Sáu mẫu độc quyền `xd_yaohat`, `xd_jtkhat`, `xd_lhyhat`, `xd_yaoarmor`, `xd_jdjarmor`, `xd_hyparmor` được xác nhận qua `EXCLUSIVE_SKIN_OWNERS`; HYParmor là archive build-only nên dùng bank/animation `xd_xshj` với build `xd_hyparmor` khi rơi và thay `swap_body` khi mặc.
- Bốn mẫu vật phẩm đổi tên: `ttk_chuongthienbinh`, `ttk_qwsk`, `nhatvuphuonghoa`, `ttk_ngulongdang`. Ngũ Long Đăng mang theo archive swap riêng.
- Bốn mẫu kiếm builder cho `ttk_tienkiem` và `ttk_makiem`. Archive builder giữ hình rơi/ô đồ; archive `xd_sword_red_*` và `xd_sword_mo_*` cung cấp hình lưỡi kiếm khi cầm.
- 42 mẫu `xd_skin_*` cho đúng ba alias nguồn `xd_xlj`, `xd_wxj`, `xd_htz_qzj`, tương ứng `ttk_tinhlakiem`, `ttk_votuongkiem`, `ttk_thanhtrucphongvankiem`. Tám mẫu ẩn ngoài UI và bốn archive `*_skillbuild` phụ thuộc cũng được đối chiếu; archive skillbuild không được tính thành lựa chọn riêng. FX lấp lánh độc lập của HYYS được chuyển thành `ttk_skin_hyys_fx`, gắn theo vật phẩm và được dọn khi đổi/reset skin.

## Nguồn và cách đối chiếu

Nguồn chuẩn là `mods/mod_steam/3235319974` (Tu Tiên 19.7). Bản Việt hóa `3721846643` là bản 18.1.0 cũ hơn và thiếu `xd_backpack3_skin7`, nên chỉ dùng để so sánh nguồn gốc. Unlock Skin `3773896514` được đọc tĩnh; nó mở các định nghĩa nguồn nhưng không cung cấp ZIP/XML/TEX riêng. Không loader nguồn nào được chạy.

Danh mục khai báo đọc từ `mods/eva-assets-work/skill-audit/decoded/scripts/widgets/xd_skinui.lua`, alias đọc từ phần cuối `decoded/scripts/main/xd_new.lua`, rồi bổ sung archive skin ẩn có đủ build/atlas. Importer dò prefab thật trong `scripts/prefabs` và bảng đăng ký động ở `main`, giữ nguyên ID skin tùy biến `ttt_portal_gcsz`, kiểm CRC ZIP, định danh build nhúng và tham chiếu texture của atlas.

`xd_tree_yx_skins_jqs` không được tạo thành lựa chọn thứ hai: archive này không có icon/khai báo UI và trùng texture với `xd_tree_yxs_skins_jqs`; bản `yxs` là định danh chuẩn đang dùng. Các skin nhân vật hoặc skin của prefab gốc chưa có trong Tu Tiên Ký được ghi `base_not_implemented` trong báo cáo JSON, không bị im lặng bỏ qua.

## Hành vi runtime

Metadata phân biệt công trình, công trình có trạng thái, đồ cầm, mũ, giáp thân và vũ khí. Apply từ chối skin sai prefab, dọn hiệu ứng cũ trước khi áp lại, dùng icon dùng chung đúng atlas, giữ animation hiện tại của `ttk_qwsk`, và dùng `idle_loop` cho Ngũ Long Đăng. Reset trả về bank/build gốc theo từng họ. Các callback equip lấy `GetSkinBuild`; tám mẫu vũ khí ẩn dùng symbol `png`, 34 mẫu UI dùng `swap`.

## Kiểm tra và giới hạn

Các kiểm tra cuối gồm 10 unittest importer (thứ tự ổn định, build-only, metadata JSON/Lua và tài nguyên đích cũ/hỏng), `--check` với `checked=148 imported_records=178 failures=0`, Lua smoke test Apply/Clear/sai prefab/dọn hiệu ứng/equip/icon/HYYS FX, cùng các suite theo họ. Nhánh hiển thị đặc biệt của `xd_yaohat` đã sửa đúng build nhúng; test equip thật xác nhận ẩn `HEAD_HAT` rồi unequip phục hồi đầu/tóc và dọn `swap_hat`. `xd_lhyhat` có symbol `swap_face` và `xd_hyparmor` có `arm_lower/arm_upper`, nhưng code equip nguồn chỉ dùng `swap_hat`/`swap_body`; không tự bịa thêm override ngoài hành vi nguồn. Chạy `--write` lần hai để so hash SHA-256 của manifest, bảng Lua và audit JSON. Kết quả chính xác sau lần chạy cuối nằm trong báo cáo JSON.

Chưa chạy một phiên DST host/client thật. Vì vậy việc hiển thị bộ chọn, lưu/tải, đồng bộ client và đổi skin khi vật phẩm đang được cầm vẫn cần kiểm tra trong game; phần này không được báo cáo như đã xác nhận.

Bốn archive `*_skillbuild` đã được đăng ký làm tài nguyên phụ thuộc để client có dữ liệu hình ảnh, nhưng hiệu ứng kỹ năng/chiến đấu nguồn của chúng không được kích hoạt vì phụ thuộc hệ nhân vật và combat nằm ngoài Tu Tiên Ký. Đây là giới hạn hiệu ứng có chủ ý, không phải thiếu archive. Trong nguồn giải mã chỉ có một prefab FX độc lập mang tên `xd_skin_*_fx`, là HYYS đã được chuyển ở trên.

Backup trước thay đổi: `mods/backups/TuTienKy_before_all_owned_skins_20260920_1630`. Hai file kiếm được sửa trước khi kịp thêm vào backup nên báo cáo JSON ghi rõ giới hạn này, không tuyên bố có bản gốc chính xác. Các thay đổi Solo đồng thời trong `modmain.lua` không do task này tạo và được giữ nguyên. Danh sách **chính xác** mọi file đã chạm, từng tài nguyên được copy và từng record audit nằm trong `2026-09-20-tu-tien-ky-all-owned-skins.json`. Generator wiki được sửa để bỏ qua an toàn các base chưa có bài curated và đọc `icon_name` dùng chung; không chạy tái sinh toàn bộ dữ liệu web để tránh ghi đè nội dung catalog không liên quan. Không tạo gói ZIP phát hành vì repository không có quy trình yêu cầu distributable cho thay đổi này.
