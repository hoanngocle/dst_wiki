# Thiết kế lại nhiệm vụ mùa — Achievement & Level

## Bối cảnh

Nguồn Workshop gốc nằm tại `mods/2937640068` và chỉ được dùng để đối chiếu. Bản làm việc hiện tại nằm tại `mods/AchievementLevel`. Sau khi hệ thống được làm sạch, cân bằng và kiểm thử độc lập, phần cần thiết mới được tích hợp trực tiếp vào `mods/PhamNhanTuTien`.

Hệ thống gốc dùng sáu slot nhiệm vụ, các pool theo mùa có nhiều mục trùng nhau và từng có pool riêng theo nhân vật. Bản làm việc đã bỏ giới hạn nhân vật, nhưng cấu trúc sáu slot, save, net variables, UI và phần thưởng vẫn mang kiến trúc cũ.

Danh mục kiểm toán hiện có 437 entry nhiệm vụ mùa trong 10 pool, tương ứng 349 mã riêng. Hai pool `other` trùng hoàn toàn với mùa thu. Bảng kiểm toán tại `mods/AchievementLevel/docs/seasonal-task-inventory.md` là nguồn để tuyển chọn lại nhiệm vụ.

## Mục tiêu

- Tạo bốn pool mùa khác nhau rõ rệt: xuân, hạ, thu và đông.
- Mỗi mùa có đúng 50 nhiệm vụ, gồm 40 nhiệm vụ một lần và 10 nhiệm vụ lặp.
- Toàn bộ 200 nhiệm vụ có ID riêng; một nhiệm vụ chỉ thuộc một mùa.
- Mỗi mùa chọn ngẫu nhiên 20 nhiệm vụ hoạt động, gồm 16 nhiệm vụ một lần và 4 nhiệm vụ lặp.
- Bỏ hoàn toàn giới hạn nhiệm vụ theo nhân vật.
- Mỗi nhiệm vụ hoàn thành có nút Claim XP riêng.
- Giữ tiến trình bốn rương mùa ở các mốc 5, 10, 15 và 20 nhiệm vụ.
- Thiết kế phù hợp cho người chơi solo, nhưng không tạo lỗi rõ ràng khi chạy trong DST host/server.

## Ngoài phạm vi

- Không quyết định lượng XP trao cho từng nhiệm vụ; phần này được cân chỉnh ở task khác.
- Không quyết định nội dung cuối cùng của bốn rương mùa.
- Không tích hợp vào `mods/PhamNhanTuTien` trong giai đoạn thiết kế và làm sạch bản độc lập.
- Không chỉnh sửa nguồn Workshop gốc tại `mods/2937640068`.
- Không duy trì route wiki `/achievement-level` sau khi tính năng đã được nhập vào Phàm Nhân; việc chuyển nội dung wiki là bước sau.

## Phương án kiến trúc

### Phương án được chọn: bốn pool tĩnh đã tuyển chọn

Mỗi mùa có một danh sách tĩnh gồm đúng 50 định nghĩa nhiệm vụ. Danh sách được tuyển chọn từ dữ liệu cũ, sửa tên hoặc điều kiện khi cần, và được validate bằng test.

Ưu điểm:

- Dễ kiểm soát chủ đề của từng mùa.
- Dễ bảo đảm tỷ lệ 40/10 và 200 ID không trùng.
- Kết quả ổn định, dễ review và dễ nhập vào Phàm Nhân.
- Không cần suy luận hoặc deduplicate dữ liệu lúc game đang chạy.

### Phương án không chọn

- Một catalog chung gắn tag mùa: linh hoạt hơn nhưng dễ gắn nhầm mùa và khó review đủ 200 mục.
- Tự lọc các pool cũ lúc runtime: giữ nhiều nợ kỹ thuật, khó kiểm thử và có nguy cơ tạo kết quả khác nhau khi dữ liệu nguồn thay đổi.

## Mô hình dữ liệu nhiệm vụ

Mỗi nhiệm vụ cần có tối thiểu:

- `id`: ID ổn định, duy nhất trên cả bốn mùa.
- `name`: khóa hoặc chuỗi tên hiển thị.
- `season`: một trong `spring`, `summer`, `autumn`, `winter`.
- `kind`: `once` hoặc `repeat`.
- `event`: sự kiện DST cần lắng nghe.
- `condition`: handler hoặc hàm kiểm tra điều kiện.
- `target`: tiến độ cần đạt cho một lượt hoàn thành.
- `xp_reward_key`: khóa truyền sang lớp cân chỉnh XP; dữ liệu nhiệm vụ không hard-code lượng XP.
- `max_claims`: `1` với nhiệm vụ thường, `5` với nhiệm vụ lặp.

Không dùng `character`, pool nhân vật hoặc `other/fallback` trong dữ liệu mới.

## Tuyển chọn 200 nhiệm vụ

Nguồn tuyển chọn là 349 mã riêng trong bảng kiểm toán cũ. Mỗi nhiệm vụ được đánh giá theo các tiêu chí:

1. Phù hợp rõ ràng với mùa được gán.
2. Có thể hoàn thành ổn định trong DST hiện tại.
3. Event, prefab và điều kiện tồn tại, không dựa vào giá trị `undefined` hoặc điều kiện sai.
4. Không yêu cầu nhân vật cụ thể.
5. Không trùng hành vi và mục tiêu với nhiệm vụ đã chọn cho mùa khác.
6. Không quá hiếm hoặc phụ thuộc tình huống khó kiểm soát đối với một mùa chơi solo bình thường.
7. Các hành động dễ, phổ biến và lặp tự nhiên được ưu tiên cho nhóm `repeat`.

Mỗi mùa phải vượt qua validator:

- đúng 50 nhiệm vụ;
- đúng 40 `once` và 10 `repeat`;
- không trùng ID trong mùa;
- không trùng ID với ba mùa còn lại.

## Chọn bộ nhiệm vụ đầu mùa

Khi tạo dữ liệu mùa mới:

1. Xác định mùa hiện tại.
2. Xáo trộn riêng danh sách `once` và `repeat` bằng RNG của game.
3. Chọn không hoàn lại 16 nhiệm vụ từ nhóm `once`.
4. Chọn không hoàn lại 4 nhiệm vụ từ nhóm `repeat`.
5. Lưu 20 ID cùng mã nhận diện mùa hiện tại vào component người chơi.
6. Đăng ký event listener cho đúng 20 nhiệm vụ đã chọn.

Bộ 20 nhiệm vụ bị khóa trong suốt mùa. Không có RPC hoặc nút reroll thủ công.

Nếu nhân vật vào world giữa mùa mà chưa có dữ liệu mùa hợp lệ, hệ thống tạo bộ 20 nhiệm vụ tại lần khởi tạo đầu tiên. Nếu save đã có cùng mã mùa, hệ thống khôi phục nguyên bộ đã lưu thay vì random lại.

## Trạng thái và Claim nhiệm vụ

### Nhiệm vụ một lần

Trạng thái tuần tự:

`active` → `ready_to_claim` → `claimed`

- Khi điều kiện đạt, nhiệm vụ chuyển sang `ready_to_claim`.
- XP chỉ được trao khi người chơi bấm Claim.
- Sau Claim, nhiệm vụ đóng và không nhận thêm tiến độ trong mùa đó.
- Claim thành công cộng một điểm vào tiến trình rương mùa.

### Nhiệm vụ lặp

Mỗi nhiệm vụ lặp có tối đa năm chu kỳ Claim trong một mùa:

`active` → `ready_to_claim` → Claim → `active` ... → Claim lần 5 → `claimed`

- Mỗi chu kỳ đủ điều kiện tạo một lần Claim XP riêng.
- Sau bốn Claim đầu, tiến độ hành động của chu kỳ được reset về 0.
- Sau Claim thứ năm, nhiệm vụ đóng đến hết mùa.
- Chỉ Claim đầu tiên cộng một điểm vào tiến trình rương.
- Claim thứ 2–5 chỉ trao XP, không tăng tiến trình rương.

Server phải xác thực trạng thái trước khi trao XP để không thể Claim hai lần bằng RPC lặp.

Khi Claim hợp lệ, component nhiệm vụ gọi một hàm phân giải XP duy nhất với `task_id`, `kind` và số thứ tự lượt Claim. Hàm này thuộc lớp cân chỉnh XP đang được làm ở task khác. Nhờ vậy việc đổi lượng XP không yêu cầu sửa dữ liệu pool, state machine hoặc UI nhiệm vụ.

## Tiến trình và rương mùa

Tiến trình rương đếm số nhiệm vụ khác nhau đã có Claim đầu tiên, tối đa 20. Các mốc mở rương là:

- 5 nhiệm vụ;
- 10 nhiệm vụ;
- 15 nhiệm vụ;
- 20 nhiệm vụ.

Bốn handler phần thưởng hiện tại được giữ làm điểm móc nối tạm thời. Nội dung và giá trị cuối cùng của từng rương sẽ được quyết định ở task cân bằng riêng. Việc thay đổi nội dung rương không được yêu cầu sửa logic chọn hoặc theo dõi nhiệm vụ.

Mỗi rương chỉ được nhận một lần trong một mùa. Claim rương do server xác thực bằng tiến trình và cờ đã nhận.

## Chuyển mùa

Khi mùa thực sự thay đổi:

1. Ngừng listener của bộ nhiệm vụ cũ.
2. Tự động trao XP cho mọi nhiệm vụ đang ở trạng thái `ready_to_claim`.
3. Tự động nhận mọi rương đã đủ điều kiện nhưng chưa nhận.
4. Không tự hoàn thành nhiệm vụ còn thiếu tiến độ.
5. Xóa trạng thái nhiệm vụ và cờ rương của mùa cũ.
6. Tạo và đăng ký bộ 20 nhiệm vụ của mùa mới.
7. Đồng bộ lại dữ liệu UI.

Thứ tự tự nhận thưởng phải diễn ra trước khi reset để người chơi không mất phần thưởng vì quên mở giao diện.

## Save và di trú

Save mới lưu:

- mã mùa hoặc khóa mùa hiện tại;
- 20 ID nhiệm vụ đã chọn;
- tiến độ hiện tại của từng nhiệm vụ;
- trạng thái sẵn sàng Claim;
- số lượt Claim của nhiệm vụ lặp;
- cờ đã tính nhiệm vụ vào tiến trình rương;
- bốn cờ rương đã nhận.

Khi gặp save kiểu cũ chỉ có sáu slot, hệ thống bỏ riêng dữ liệu nhiệm vụ mùa cũ và tạo bộ 20 nhiệm vụ mới. Không được reset Level, XP, điểm thuộc tính, Sao, perk hoặc thành tựu thường.

Save/load trong cùng mùa phải giữ nguyên lựa chọn và tiến độ; không được random lại do reload, xuống hang hoặc chuyển shard.

## Đồng bộ mạng và UI

Server là nguồn dữ liệu chuẩn cho selection, progress, Claim và phần thưởng. Client chỉ hiển thị trạng thái và gửi yêu cầu Claim.

Thay sáu trường net cố định bằng 20 slot có cấu trúc nhất quán. Mỗi slot cần đồng bộ tối thiểu:

- mã số ổn định được ánh xạ một-một tới task ID;
- tiến độ hiện tại;
- trạng thái sẵn sàng Claim/đã đóng;
- số lượt Claim đã thực hiện.

UI hiển thị danh sách 20 nhiệm vụ có thể cuộn. Mỗi dòng cho biết:

- tên và mô tả nhiệm vụ;
- tiến độ của chu kỳ hiện tại;
- số lượt đã Claim đối với nhiệm vụ lặp;
- nút Claim chỉ bật khi server báo nhiệm vụ sẵn sàng;
- trạng thái hoàn tất khi không còn lượt Claim.

Thanh tiến trình rương hiển thị các mốc 5/10/15/20 và không dùng số lượt Claim lặp thứ 2–5.

## Kiểm thử

Tối thiểu phải có các test sau:

1. Bốn pool đều có đúng 50 nhiệm vụ.
2. Mỗi pool có đúng 40 nhiệm vụ thường và 10 nhiệm vụ lặp.
3. Có đúng 200 ID duy nhất trên cả bốn mùa.
4. Không còn dữ liệu nhiệm vụ giới hạn theo nhân vật hoặc pool `other`.
5. Selection luôn tạo đúng 16 nhiệm vụ thường và 4 nhiệm vụ lặp, không trùng.
6. Save/load cùng mùa giữ nguyên bộ 20 và tiến độ.
7. Nhân vật mới giữa mùa nhận đúng một bộ 20.
8. Nhiệm vụ thường chỉ Claim được một lần.
9. Nhiệm vụ lặp Claim được tối đa năm lần.
10. Chỉ Claim đầu tiên của nhiệm vụ lặp tăng tiến trình rương.
11. Rương chỉ mở ở 5/10/15/20 và chỉ nhận được một lần.
12. RPC Claim lặp không trao thưởng hai lần.
13. Đổi mùa tự nhận nhiệm vụ/rương đã đủ điều kiện trước khi reset.
14. Di trú save sáu slot không làm mất dữ liệu Level, Sao, perk hoặc thành tựu khác.
15. UI hiển thị đủ 20 nhiệm vụ và cập nhật đúng trạng thái Claim.

## Trình tự triển khai

1. Tuyển chọn và validate 200 nhiệm vụ trong `mods/AchievementLevel`.
2. Thay mô hình sáu slot bằng cấu trúc 20 nhiệm vụ và save schema mới.
3. Cài đặt Claim từng nhiệm vụ, nhiệm vụ lặp và tiến trình rương.
4. Cài đặt chuyển mùa, tự nhận thưởng và di trú save.
5. Cập nhật net variables, RPC và UI 20 nhiệm vụ.
6. Chạy test dữ liệu, component, save/load, RPC và UI.
7. Kiểm thử trong game bản Achievement & Level độc lập.
8. Sau khi ổn định, lập đặc tả riêng để tích hợp vào `mods/PhamNhanTuTien` và chuyển nội dung wiki.

## Tiêu chí nghiệm thu

- Mỗi mùa có đúng 50 nhiệm vụ riêng biệt, tỷ lệ 40/10.
- Người chơi nhận đúng 20 nhiệm vụ, tỷ lệ 16/4, và không thể reroll trong mùa.
- Claim XP hoạt động riêng cho từng lượt hoàn thành.
- Nhiệm vụ lặp có tối đa năm Claim nhưng chỉ đóng góp một tiến trình rương.
- Rương hoạt động ở mốc 5/10/15/20.
- Chuyển mùa không làm mất phần thưởng đã đủ điều kiện.
- Không còn giới hạn nhiệm vụ theo nhân vật.
- Save cũ không làm mất tiến trình ngoài hệ thống nhiệm vụ mùa.
- Toàn bộ test liên quan vượt qua trước khi bắt đầu tích hợp vào Phàm Nhân.
