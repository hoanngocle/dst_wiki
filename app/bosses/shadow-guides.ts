import type { BossGuide } from './guide-types';

export const shadowGuides: BossGuide[] = [
  {
    slug: 'werepig',
    title: 'Nightmare Werepig → Scrappy Werepig',
    description: 'Giải xiềng, xử lý ký sinh, lấy Dreadstone rồi hoàn thành vòng tái đấu trên mặt đất.',
    difficulty: 'Khó • cần quản lý tinh thần và né đòn',
    location: 'Muddy Biome dưới hang → Junk Yard trên mặt đất',
    summary: 'Đây là một chuỗi hai trận luân phiên. Mục tiêu lần đầu là mở khóa trang bị Dreadstone và học cách dùng chính đòn của boss để khai thác phần thưởng.',
    preparations: [
      'Khuyến nghị: vũ khí dự phòng, ít nhất hai bộ giáp/mũ, một chồng đồ hồi máu và thức ăn tinh thần riêng; tăng số lượng nếu chưa quen né.',
      'Pick/Axe để mở xiềng; Lantern đã nạp nhiên liệu hoặc Star Caller’s Staff để chiếu sáng; chuẩn bị đường rút trước khi bắt đầu.',
      'Nightmare Amulet là lựa chọn tiện lợi cho ký sinh; nếu không có, phải chủ động xuống mức điên rồi hồi tinh thần sau pha mở màn.',
    ],
    sections: [
      {
        id: 'starting-kit', title: '1. Từ căn cứ đến bộ đồ đi hang',
        paragraphs: [
          'Đừng dùng hết thực phẩm hồi máu để chống đói trên đường. Khuyến nghị chia hành trang thành đồ đi đường, đồ chữa thương và giáp thay thế, đặt chúng vào ô quen tay trước khi xuống hang. Một cách chuẩn bị Pierogi là nấu 1 trứng, 1 thịt, 1 rau và chất độn phù hợp; tránh cành cây, hai nguyên liệu quái vật hoặc Pepper. Mỗi chiếc hồi 40 máu cho nhân vật ăn uống bình thường. Trứng có thể lấy bằng cách cho chim trong Birdcage ăn thịt.',
          'Pick/Axe cần Luxury Axe, Opulent Pickaxe và 2 Thulecite, chế tạo cạnh Ancient Pseudoscience Station trong Ruins. Đây là công cụ mở trận, không nên dùng làm vũ khí chính. Có thể chế Star Caller’s Staff bằng 4 Nightmare Fuel, 2 Living Logs và 2 Yellow Gems tại trạm cổ đại để có nguồn sáng đặt xuống đất. Giữ thêm đèn dự phòng cho đường về.',
        ],
        sources: [{ page: 'Pick/Axe' }, { page: 'Star_Caller%27s_Staff/DST' }, { page: 'Pierogi' }, { page: 'Egg' }],
      },
      {
        id: 'release', title: '2. Tìm và giải phóng boss đúng cách',
        steps: [
          'Tìm vùng Muddy Biome dưới hang: nền bùn với nhiều Light Flowers. Xác định bộ ba Cracked Pillars trói một con lợn lớn, rồi quan sát khoảng trống quanh chúng.',
          'Dùng cuốc đào bỏ lớp Marble ngoài cả ba cột. Sau đó dùng Pick/Axe đánh lõi từng cột thật nhanh để cả ba cùng rung; chỉ đào lớp ngoài bằng cuốc thường chưa mở được xiềng.',
          'Giữ các cột trong khu vực đánh. Chỉ cú nện đất của Nightmare Werepig phá được lõi, mỗi cột cho 3–4 Dreadstone. Vì vậy cần dụ nện cột trong trận, trước khi kết liễu.',
        ],
        tips: ['Khuyến nghị chạy thử một vòng từ cột này sang cột khác trước khi giải xiềng; biết chỗ nào dễ kẹt giúp bạn chọn đường né khi màn hình bắt đầu rung.'],
        sources: [{ page: 'Cracked_Pillar' }],
      },
      {
        id: 'parasites', title: '3. Pha 0: đánh ký sinh, chưa đánh con lợn',
        paragraphs: [
          'Sau khi được thả, boss vẫn bất tử vì ba Parasitic Shadelings đang bám trên người. Phải ở trạng thái điên mới đánh được chúng. Ngưỡng điên tự nhiên bắt đầu dưới 15% tinh thần; Nightmare Amulet tạo hiệu ứng điên khi đeo mà không cần kéo thanh tinh thần thực về 0.',
          'Đợi boss hất ký sinh xuống đất rồi mới nhắm đánh. Mỗi con có 100 máu và chỉ nằm ngoài trong một khoảng ngắn; đánh lúc nó còn bám sẽ chọn nhầm boss. Hạ đủ ba con để chuyển sang trận chính. Ký sinh không tự tấn công người chơi.',
        ],
        tips: ['Khuyến nghị đeo mũ giáp trong lúc dùng bùa vì bùa chiếm ô thân. Sau khi dọn ký sinh, tháo bùa, mặc lại giáp và kiểm tra tinh thần trước khi tiếp tục.'],
        sources: [{ page: 'Parasitic_Shadeling' }, { page: 'Nightmare_Amulet' }],
      },
      {
        id: 'nightmare-fight', title: '4. Ba pha đánh và thời điểm lấy đá',
        steps: [
          'Trên 50% máu: né cú lao bằng đường chéo về phía boss. Ba lần lao hụt tạo cơ hội đánh lúc nó mệt; trúng đòn làm giảm tích lũy mệt.',
          'Dưới 50%: boss ưu tiên nện. Nhử cạnh cột, lùi khỏi vùng nện rồi quay lại đánh ngắn. Nện không làm boss mệt, nên đừng chờ ba cú như pha đầu.',
          'Dưới 30%: lao và nện kết hợp. Sau khi né, vẫn quan sát đòn nối tiếp; rời tầm khi boss hết mệt. Boss có hồi máu khi ngừng giao chiến, nên không kéo trận bằng chạy vòng quá lâu.',
        ],
        paragraphs: ['Phần thưởng có Pure Horror và các bản thiết kế Dreadstone. Khuyến nghị kiểm tra cả ba vị trí cột trước khi đánh nốt máu cuối; chiến thắng mà bỏ cột sẽ mất cơ hội lấy đá của lượt này.'],
        sources: [{ page: 'Nightmare_Werepig' }],
      },
      {
        id: 'scrappy-fight', title: '5. Scrappy: dùng bãi rác làm vỡ trang bị',
        paragraphs: [
          'Sau 10 ngày, tới Junk Yard và lục Teetering Junk Pile ba lần để gọi Scrappy. Lùi khỏi đồ văng ra. Khi giao chiến, nó lấy trang bị từ đống rác; máu thấp có thể dùng nhiều món cùng lúc.',
          'Chùy và giáp vai hao độ bền khi đánh trúng người, đống rác hoặc hàng rào, không hao khi hụt hoàn toàn. Nhử vào phế liệu rồi né ngang để làm vỡ đồ sau ba lần va chạm. Giữ khoảng trống ngoài đường lao, tranh thủ lúc nó đổi đồ để đánh. Nếu đã hạ Celestial Champion, nó có thể dùng laser: né lúc nạp; ba lần bắn làm súng hỏng dù trượt. Muốn nhận Scrappy Pauldron, kết liễu khi nó còn mặc món đó.',
        ],
        tips: ['Khuyến nghị giữ lại vài vật cản của bãi rác làm mục tiêu nhử; đừng dọn sạch khu vực theo thói quen chuẩn bị đấu trường.'],
        sources: [{ page: 'Scrappy_Werepig' }, { page: 'Junk_Yard' }],
      },
      {
        id: 'repeat', title: '6. Thu hoạch và chuẩn bị vòng tiếp theo',
        paragraphs: [
          'Lục Teetering Junk Pile sau chiến thắng để lấy bản thiết kế T.I.N.G.L.E. Node; khi Scrappy đã bị hạ, lần lục đầu bảo đảm cho bản thiết kế. Đánh xong Scrappy rồi chờ 10 ngày mới có Nightmare và bộ cột trở lại dưới hang. Hai dạng không tồn tại đồng thời.',
          'Khuyến nghị ghi ngày thắng và vị trí hai đấu trường vào kế hoạch đi tài nguyên. Dreadstone Armor và Helm tự sửa độ bền; đây là phần thưởng hữu ích cho các chuyến chiến đấu dài. Nếu đang hướng tới Shadow Rifts hoặc reset Sanctum, để riêng 5 Dreadstone: sau khi hạ Fuelweaver, Beckoning Hand tại Ancient Gateway dùng chúng để sửa cổng. Đừng chế hết đá vào đồ trang trí trước khi quyết định nhánh tiến trình tiếp theo.',
        ],
        sources: [{ page: 'Teetering_Junk_Pile' }, { page: 'Cracked_Pillar' }, { page: 'Scrapbooking' }, { page: 'Ancient_Gateway' }],
      },
    ],
    rewards: [
      { name: 'Dreadstone', use: 'Lấy từ cột bị nện; dùng cho trang bị và sửa Ancient Gateway.', page: 'Cracked_Pillar' },
      { name: 'Pure Horror', use: 'Nguyên liệu chế tạo thuộc nhánh Shadow.', page: 'Pure_Horror' },
      { name: 'Scrappy Pauldron', use: 'Phần thưởng có điều kiện: boss phải còn mặc khi bị hạ.', page: 'Scrappy_Werepig' },
    ],
    mistakes: [
      { question: 'Sao đánh con lợn không mất máu?', answer: 'Kiểm tra ba ký sinh của pha 0; phải điên và đánh chúng lúc rơi khỏi boss.' },
      { question: 'Thắng nhưng không có Dreadstone?', answer: 'Đá nằm trong cột; hãy nhử cú nện phá cột trước khi kết liễu.' },
      { question: 'Chờ lâu mà Nightmare chưa trở lại?', answer: 'Cần hoàn thành lượt Scrappy trên mặt đất trước, rồi mới tính thời gian trở lại.' },
    ],
    next: [{ label: 'Khám phá Ancient Sanctum', href: '/bosses/ancient-sanctum' }, { label: 'Tất cả tuyến boss', href: '/bosses' }],
  },
  {
    slug: 'ancient-sanctum',
    title: 'Ancient Sanctum & Ancient Guard Towers',
    description: 'Bật Archive, vào xoáy biển, dẫn Security Pulses và hoàn tất Key Room để lấy Keystone.',
    difficulty: 'Cuối game • khám phá, giải đố và bốn boss',
    location: 'Giant Whirlpool ngoài biển → Sanctum dưới hang',
    summary: 'Tuyến này dùng cơ chế Sanctum hiện hành năm 2026: Waymark Compass dẫn đường và kéo năng lượng, Guard Towers bảo vệ Key Room, còn Keystone phục vụ việc đặt lại khu vực.',
    preparations: [
      'Bật Archive Switch bằng Iridescent Gem trước chuyến đi; chuẩn bị phương tiện biển có thể chấp nhận mất.',
      'Khuyến nghị mang nhiều giáp và vũ khí thay thế, đồ hồi máu, thức ăn đi đường và nguồn sáng dự phòng cho một chuyến khám phá dài.',
      'Không bắt buộc Spark Ark: Waymark Compass tìm trong Sanctum có thể dẫn bốn Security Pulses.',
    ],
    sections: [
      {
        id: 'archive', title: '1. Mở nguồn điện Archive từ đầu',
        paragraphs: [
          'Dưới hang, tìm Blue Mushtree Forest rồi vùng Lunar Grotto có nền nấm biến dị và cây dạng mặt trăng; vùng này nối Ancient Archive. Trong Archive có ba Ornate Pedestals, hai bệ đã có Iridescent Gem. Cần thêm viên thứ ba, không phải đá quý màu thường.',
          'Chuẩn bị trong Ruins: Star Caller’s Staff cần 4 Nightmare Fuel, 2 Living Logs, 2 Yellow Gems; Deconstruction Staff cần 4 Nightmare Fuel, 2 Living Logs, 2 Green Gems. Cả hai chế cạnh trạm cổ đại. Khai thác tượng Ancient Statues để tìm tài nguyên và đá quý, rồi mang đủ vật liệu trước khi tới trạm.',
          'Tìm Moon Stone trong rừng Evergreen, sửa bằng Moon Rock. Đặt Star Caller’s Staff lên đó vào đêm trăng tròn rồi bảo vệ nghi thức 60 giây khỏi Werepigs và Hounds. Dùng Deconstruction Staff lên Moon Caller’s Staff thu được để lấy Iridescent Gem. Cắm đá vào bệ trống và để nguyên cả ba viên: tháo một viên sẽ cắt điện. Lần bật đầu cũng kích hoạt nguy hiểm mới ở ranh Lunar Grotto, nên khuyến nghị chừa đồ hồi phục cho đường quay ra.',
        ],
        sources: [{ page: 'Lunar_Grotto' }, { page: 'Archive_Switch' }, { page: 'Moon_Stone' }, { page: 'Moon_Caller%27s_Staff' }, { page: 'Star_Caller%27s_Staff/DST' }, { page: 'Deconstruction_Staff/DST' }, { page: 'Green_Gem/DST' }],
      },
      {
        id: 'enter', title: '2. Vào bằng Giant Whirlpool, thu đồ ở sảnh',
        paragraphs: [
          'Tìm Giant Whirlpool ở biển sâu. Thuyền bị hút vào sẽ bị phá hủy; người và vật phẩm được chuyển tới Ocean Detritus trong sảnh Sanctum. Đây là lối vào, không phải một trận đánh trên thuyền. Khuyến nghị để tài sản không cần thiết ở căn cứ, đi bằng phương tiện ít tốn kém và mang đủ đồ khám phá trên người. Sau khi tới nơi, tương tác đống Detritus để lấy lại vật phẩm, kiểm kê trước khi rời sảnh.',
          'Waymark là điểm chuyển phòng. Những người đang ở trong Sanctum cần cùng chạm một Waymark để đi tiếp; hoa văn bên dưới chỉ hướng. Waymark hỏng sửa bằng Portation Orb tìm gần đó. Khuyến nghị cả nhóm cử một người chọn đường và gọi tập trung, tránh mỗi người đứng ở một cửa khiến tưởng cơ chế bị lỗi.',
        ],
        sources: [{ page: 'Giant_Whirlpool' }, { page: 'Sanctum_Waymark' }],
      },
      {
        id: 'navigate', title: '3. Đi mê cung và lấy Waymark Compass',
        steps: [
          'Tìm Waymark Compass tại King Statue Room, Playbill Room hoặc Generator Room. Cầm trên tay để xem chỉ dẫn tới Waymark dẫn về Key Room; đây là món chuyên dụng, không phải Compass thường.',
          'Nếu khám phá nhánh Sequitor: kéo Lever dựng đường đá, rồi chọn đường tới bờ đối diện. Hai Sequitors bắt chước bước đi; ô đá chỉ dùng được một lần trước khi sập.',
          'Ở phòng Flummoxing Flame, mục tiêu bật đồng thời cả chín lửa. Một đèn luôn sáng, một đèn hỏng chỉ bật/tắt được bằng đèn bên cạnh. Khuyến nghị ghi trạng thái từng lần bấm thay vì bật tắt ngẫu nhiên.',
          'Qua Purifier Room bằng Lever của Sanctum Purifiers. Hai nhánh Fountain cho khám phá bổ sung; khi ưu tiên trận boss, tiếp tục theo Compass về Key Room.',
        ],
        sources: [{ page: 'Waymark_Compass' }, { page: 'Sanctum' }],
      },
      {
        id: 'pulses', title: '4. Nạp bốn Security Pulses trước trận',
        paragraphs: [
          'Security Pulses là luồng năng lượng phát ra từ Ancient Guard Posts. Trong Sanctum có năm trụ: ba ở các Hall, hai ở Generator Room. Cầm Waymark Compass tới gần để kéo tối đa bốn luồng theo mình; đổi món trên tay sẽ làm chúng ngừng theo. Dẫn về Key Room, tới gần bốn Pulse Cradles để nạp.',
          'Spark Ark là phương án vận chuyển khác nếu đã có từ tiến trình boss Lunar biến dị. Đặt Ark rỗng xuống để hút Pulse rồi mang tới Cradle. Không cần hoàn thành nhánh Lunar chỉ để có vật này: Compass giải quyết cùng yêu cầu tại chỗ. Nếu trụ vừa mất Pulse, nó tạo lại sau khoảng hai phút.',
          'Nạp đủ bốn sẽ đánh thức các tháp và làm lộ Lustrous Sockets. Kiểm tra giáp và đường né trước khi đánh tháp hoặc kéo Lever, vì đó là hành động khiến chúng giao chiến.',
        ],
        sources: [{ page: 'Ancient_Guard_Post' }, { page: 'Spark_Ark' }, { page: 'Key_Room' }],
      },
      {
        id: 'towers', title: '5. Hạ tháp và đưa bọ vào ổ',
        paragraphs: [
          'Mỗi tháp có 6.000 máu. Né sang bên hoặc sau lưng chuỗi đấm; dưới 75% thêm xoay, dưới 50% thêm nện nhanh. Khi xuống nửa máu, đòn trúng tiếp theo có thể kích hoạt choáng; cửa sổ choáng rút ngắn khi xuống dưới 2.000. Đừng đứng tầm trung chờ nện. Tháp không hồi máu: rời phòng để hồi phục được. Đi nhóm nên giãn vị trí.',
          'Dụ tháp dưới đèn rồi kéo Lever cho Lustrous Weevil rơi trúng: tháp choáng 15 giây và nhận thêm sát thương. Tránh tự đứng dưới điểm rơi. Mỗi bọ có 1.000 máu; đánh tới khi co vỏ, rồi đẩy vào Lustrous Socket trong sáu giây, trước khi nó tỉnh với 500 máu. Làm đủ bốn ổ để gọi Reliquary.',
        ],
        tips: ['Khuyến nghị xử lý từng khu vực, giữ một lối thoát rõ ràng và dừng đánh ngay khi cần đổi giáp. Đừng cố ăn hoặc sửa hành trang ngay giữa chuỗi đòn.'],
        sources: [{ page: 'Ancient_Guard_Tower' }, { page: 'Lustrous_Weevil' }],
      },
      {
        id: 'keystone', title: '6. Nhận Keystone, rời khu vực và reset',
        paragraphs: [
          'Lấy Keystone từ Reliquary để Sanctum Smithy xuất hiện; một Chasm mở đường về Ancient Orchestrina. Thu linh kiện tháp trước khi rời đi. Phân biệt Keystone với Ancient Key: Ancient Key lấy từ rương Ancient Guardian và dùng cho Fuelweaver; Keystone lấy ở đây để reset Sanctum.',
          'Keystone không mang lên mặt đất được: khi đổi tầng, nó bị bỏ lại tại cầu thang. Mang nó theo đường dưới hang tới Ancient Gateway ở Atrium. Cần hạ Fuelweaver để có Beckoning Hand; tay đầu nhận 5 Dreadstone sửa cổng, tay tiếp theo nhận Keystone và yêu cầu xác nhận reset.',
          'Trước khi xác nhận, khuyến nghị cả nhóm thu sạch vật phẩm và công trình cần giữ. Reset xóa đồ cùng công trình tự đặt trong Sanctum, phục hồi các vật phẩm khám phá và làm Waymarks đã sửa hỏng lại. Đây là quyết định làm mới cả khu vực, không chỉ gọi lại boss.',
          'Lưu ý ở bước sửa cổng: trao 5 Dreadstone rồi xác nhận cũng mở chu kỳ Shadow Rift lâu dài trong hang. Bước này thay đổi tiến trình thế giới, nên cả nhóm cần chuẩn bị cho quái và nguy hiểm Rift trước khi làm.',
        ],
        sources: [{ page: 'Key_Room' }, { page: 'Keystone' }, { page: 'Ancient_Key' }, { page: 'Sanctum' }, { page: 'Beckoning_Hand' }],
      },
    ],
    rewards: [
      { name: 'Keystone', use: 'Đổi tại Beckoning Hand để reset Sanctum sau các điều kiện của Ancient Gateway.', page: 'Keystone' },
      { name: 'Sanctum Smithy', use: 'Trạm hiện sau khi lấy Keystone; xử lý linh kiện thu từ Guard Towers.', page: 'Key_Room' },
      { name: 'Ancient Masks & A Task Complete', use: 'Vật phẩm khám phá ở các phòng riêng; thu trước khi rời mê cung.', page: 'Sanctum' },
    ],
    mistakes: [
      { question: 'Đến sảnh nhưng Waymark không chạy?', answer: 'Kiểm tra Archive Switch dưới hang đã đủ ba Iridescent Gems; sau đó tập trung toàn nhóm tại cùng Waymark.' },
      { question: 'Phải mang Ancient Key tới Key Room không?', answer: 'Không. Key Room dùng Security Pulses, Lever và Lustrous Weevils; Ancient Key thuộc tuyến Fuelweaver.' },
      { question: 'Không có Spark Ark thì bị chặn?', answer: 'Không. Cầm Waymark Compass để dẫn Pulses từ các Guard Posts trong Sanctum.' },
      { question: 'Đánh tháp xong sao chưa có Keystone?', answer: 'Cần đưa đủ bốn Lustrous Weevils đã co vỏ vào các socket để Reliquary xuất hiện.' },
    ],
    next: [{ label: 'Lấy Dreadstone từ Werepig', href: '/bosses/werepig' }, { label: 'Tất cả tuyến boss', href: '/bosses' }],
  },
];
