import type { BossGuide } from './guide-types';

export const crossoverGuides: BossGuide[] = [
  {
    slug: 'terraria',
    title: 'Terraria: từ Terrarium đến cả hai Twins of Terror',
    description: 'Tìm bình triệu hồi, luyện Eye of Terror rồi đánh Retinazor và Spazmatism qua nhiều đêm liên tiếp.',
    difficulty: 'Eye: nhập môn • Twins: khó',
    location: 'Mặt đất, chiến đấu ban đêm',
    summary: 'Đây là một nhánh trang bị độc lập. Nên dùng Eye để học cách né lao trước khi đổi sang Twins; chiến thắng Eye không phải điều kiện bắt buộc để gọi Twins.',
    preparations: [
      'Vũ khí mới, giáp đầu và giáp thân dự phòng; tách đồ hồi máu khỏi đồ ăn chống đói.',
      'Lantern cùng nhiên liệu, bãi trống rộng, đường rút lui và nơi hồi sinh đã chuẩn bị.',
      'Đánh Twins: thêm Nightmare Fuel, nhiều đồ thay thế và Pan Flute nếu muốn tách mục tiêu.',
    ],
    sections: [
      {
        id: 'find-terrarium',
        title: '1. Đi từ căn cứ đến bình triệu hồi',
        paragraphs: [
          'Khám phá các vùng Forest để tìm Conspicuous Chest, mở rương lấy Terrarium rồi đánh dấu vị trí cất. Đây là đồ tìm được trong thế giới, không phải công thức cần mở bằng bàn chế tạo. Bình chỉ dùng trên mặt đất; đi xuống hang sẽ khiến nó rơi lại phía trên.',
          'Chuẩn bị sinh tồn trước: dựng Science Machine rồi Alchemy Engine, gom nguyên liệu cho vũ khí và nhiều bộ giáp. Chọn bãi có khoảng trống ở mọi phía, xa căn cứ và đường nước. Đặt đồ thay thế ở mép bãi; chạy thử một vòng để biết nơi nào dễ mắc kẹt khi trời tối.',
        ],
        sources: [{ page: 'Terrarium' }, { page: 'Guides/Making_Bigger_and_Better_Weapons', label: 'Chuẩn bị vũ khí' }],
      },
      {
        id: 'first-night',
        title: '2. Bố trí ánh sáng và gọi Eye lần đầu',
        steps: [
          'Đem Lantern đã nạp đầy xuống bãi trước hoàng hôn. Đặt đèn để tay vẫn cầm được vũ khí; kiểm tra cả đường chạy ngoài vùng sáng chính. Giữ một nguồn sáng dự phòng ở ô dễ bấm.',
          'Thả Terrarium xuống đất và chọn Touch. Nếu đang ban ngày, đợi đêm; chạm vào ban đêm sẽ bắt đầu triệu hồi. Bình bình thường gọi Eye of Terror. Chưa cho Nightmare Fuel vào nếu mục tiêu là luyện Eye.',
          'Cả nhóm nên có mặt ở bãi khi đêm bắt đầu: boss xuất hiện gần người chơi được chọn, không nhất thiết bên cạnh bình. Thống nhất người dẫn boss và người xử lý quái nhỏ để không kéo đường lao xuyên nhau.',
        ],
        tips: ['Lần đầu, hãy dành phần đầu trận để quan sát hoạt ảnh. Mục tiêu thực tế là sống qua chuỗi đòn và còn đủ đồ cho đêm sau.'],
        sources: [{ page: 'Terrarium' }, { page: 'Light_Tab', label: 'Ánh sáng và bóng tối' }],
      },
      {
        id: 'eye-combat',
        title: '3. Eye of Terror: nhận ra lúc phải ngừng đánh',
        paragraphs: [
          'Eye lao rồi sinh trứng; phá trứng trước khi nở. Dưới 65% máu, nó mở miệng, lao liên tiếp, sinh thêm trứng và có đòn đập tạo hố làm chậm.',
          'Gợi ý thực hành: né sang bên khi thấy hướng lao đã chốt, quan sát boss dừng thật sự rồi mới áp sát. Không quay lại ngay sau lần lao đầu. Khi trứng nằm xa nhau, chọn đường tiếp cận an toàn thay vì chạy xuyên boss để dọn cho đủ. Nếu mất nhịp, bỏ cơ hội đánh và lấy lại khoảng cách.',
          'Đừng áp một con số đòn đánh cố định cho mọi nhân vật hay độ trễ mạng. Thử một nhịp ngắn, lùi sớm, rồi tăng dần khi đã quen. Đổi giáp và hồi máu lúc có khoảng trống, không đợi đến khi giáp vỡ giữa chuỗi lao.',
        ],
        sources: [{ page: 'Eye_of_Terror', label: 'Hành vi và Strategy' }],
      },
      {
        id: 'night-loop',
        title: '4. Quản lý bình minh và chuyển sang Twins',
        paragraphs: [
          'Bình minh khiến Eye rút; kích hoạt lại bình đêm sau để tiếp tục. Mỗi đêm bỏ qua, Eye hồi 250 máu. Hãy dùng ban ngày kiểm kê giáp, nấu đồ hồi phục và nạp đèn trước khi nhận trận tiếp theo.',
          'Muốn gọi Twins, cho một Nightmare Fuel vào Terrarium còn sử dụng được để làm nó héo, rồi kích hoạt như cũ. Chỉ chuyển khi đã có dự trữ cho nhiều đêm. Với Twins, bỏ một đêm sau khi đã gọi sẽ đưa bình vào ngủ; đừng coi đây là trận có thể nghỉ tùy ý giữa chừng.',
          'Sau khi hoàn tất boss, bình ngủ 15 ngày theo thiết lập mặc định. Ghi ngày kết thúc và cất bình ở chỗ dễ nhớ. Nếu lịch nhóm không bảo đảm tối mai chơi tiếp, hãy hoãn lần gọi Twins đầu tiên.',
        ],
        sources: [{ page: 'Terrarium' }, { page: 'Eye_of_Terror' }],
      },
      {
        id: 'twins-combat',
        title: '5. Retinazor và Spazmatism: xử lý hai hướng ép',
        paragraphs: [
          'Retinazor thiên về sinh quái, lao xa hơn; Spazmatism thiên về lao nhanh. Mỗi con có 10.000 máu. Chúng vào dạng hai khi tổng máu dưới 13.000 hoặc một con chết; dạng hai tăng áp lực lao, quái nhỏ và hố.',
          'Có thể thổi Pan Flute lúc cả hai vừa xuất hiện, đánh thức một con rồi dẫn ra xa. Gợi ý chia việc: một người giữ hướng di chuyển dễ đoán, người còn lại quan sát quái nhỏ và báo chỗ nguy hiểm. Khi chơi đơn, ưu tiên giữ cả hai trong tầm quan sát; mất dấu một con là lý do để ngừng tấn công.',
          'Tập trung hạ một mục tiêu để giảm việc phải theo dõi hai hướng. Tuy nhiên, chuẩn bị đổi nhịp ngay khi chuyển dạng, không mặc định con còn lại vẫn dễ như đầu trận. Khi sân chật, dịch sang phần trống theo một hướng đã thống nhất; tránh chạy vòng cắt ngang đường đồng đội.',
        ],
        sources: [{ page: 'Eye_of_Terror', label: 'Twins of Terror và Tips' }],
      },
      {
        id: 'loot-repeat',
        title: '6. Thu chiến lợi phẩm và giữ trang bị dùng lâu',
        paragraphs: [
          'Eye Mask là giáp đầu của Eye; Shield of Terror nhận sau khi hạ đủ hai Twins, vừa là vũ khí vừa bảo vệ ở ô tay. Cả hai sửa bằng thức ăn nhưng vẫn mất hẳn nếu độ bền về không. Monster Meat là nguồn sửa tiện lợi; hãy sửa trước trận và cất món gần hỏng để tránh mất vì một lần quên.',
          'Eye còn cho Milky Whites; Twins cho đá quý vàng hoặc xanh lá theo từng con, cùng linh kiện. Dành ô trống trước lúc kết thúc. Kiểm tra loot cùng đồng đội rồi lập danh sách nguyên liệu đã tiêu hao; chỉ lặp lại khi phần thưởng có ích hơn số giáp và thức ăn cần bổ sung.',
        ],
        sources: [{ page: 'Eye_Mask' }, { page: 'Shield_of_Terror' }, { page: 'Monster_Meat' }, { page: 'Eye_of_Terror' }],
      },
    ],
    rewards: [
      { name: 'Eye Mask', use: 'Giáp đầu sửa bằng thức ăn; theo dõi độ bền thường xuyên.', page: 'Eye_Mask' },
      { name: 'Shield of Terror', use: 'Vũ khí kiêm giáp ô tay, phần thưởng khi hạ đủ hai Twins.', page: 'Shield_of_Terror' },
    ],
    mistakes: [
      { question: 'Vì sao bình không cho Touch?', answer: 'Kiểm tra trạng thái ngủ và thiết lập thế giới có tắt Eye of Terror không. Đợi đủ chu kỳ, không cần tìm công thức chế bình.' },
      { question: 'Vì sao vừa né xong đã bị đánh tiếp?', answer: 'Bạn có thể đã quay lại giữa chuỗi lao. Quan sát lần dừng và hoạt ảnh kế tiếp trước khi áp sát.' },
    ],
    next: [{ label: 'Trở về các tuyến boss', href: '/bosses' }],
  },
  {
    slug: 'toadstool',
    title: 'Toadstool và Misery: chuẩn bị một trận tiêu hao trong hang',
    description: 'Tìm nấm triệu hồi, làm Volatile Canary và kiểm soát cây nấm, khí độc trước khi đua sát thương.',
    difficulty: 'Khó • Misery: rất khó',
    location: 'Các hố Toadstool trong Caves',
    summary: 'Nên tập bản thường trước. Route này cần cả hậu cần dưới hang và khả năng dọn Sporecap; chỉ mang thêm vũ khí chưa đủ để đánh Misery.',
    preparations: [
      'Ánh sáng dự phòng, nhiều giáp, vũ khí bền và kho hồi phục nằm ngoài bãi đánh.',
      'Rìu dự phòng hoặc Moon Glass Axe; Weather Pain nếu có nguyên liệu.',
      'Misery: Friendly Scarecrow, Bird Trap, Canary sống và Birdcage đặt dưới hang.',
    ],
    sections: [
      {
        id: 'find-cap',
        title: '1. Mở đường xuống hang và tìm đúng hố',
        paragraphs: [
          'Chuẩn bị đồ đi hang rồi mở Sinkhole, khám phá và đánh dấu đường về. Ba hố Toadstool có thể xuất hiện, nhưng chỉ một hố có mũ nấm để gọi boss. Chặt mũ bằng rìu sẽ triệu hồi bản thường.',
          'Đừng chặt ngay khi thấy nấm. Hãy khảo sát cả khu vực, chọn đường rút tránh hồ và vật cản, rồi vận chuyển đồ xuống theo nhiều chuyến. Gợi ý bố trí: một điểm tiếp tế ngoài sân, một vùng giao chiến rộng và một lối về quen thuộc. Đi thử đường trong điều kiện ánh sáng thực tế trước khi mang đồ quý vào.',
          'Lantern và nguồn sáng dự phòng phải đủ cho trận kéo dài. Gom Light Bulbs trên đường thám hiểm, nạp đèn trước trận; tránh để toàn bộ nhiên liệu ở căn cứ trên mặt đất.',
        ],
        sources: [{ page: 'Toadstool' }, { page: 'Light_Tab' }],
      },
      {
        id: 'tools-stockpile',
        title: '2. Chuẩn bị dụng cụ dọn cây và kho dự trữ',
        paragraphs: [
          'Weather Pain cần 10 Down Feathers, một Volt Goat Horn và một Gears tại Alchemy Engine. Lông đến từ Moose/Goose và Moslings; sừng từ Volt Goat, bánh răng từ Clockworks. Đây là một nhánh chuẩn bị riêng, nên thu gom trước thay vì đến cửa boss mới làm.',
          'Lốc của Weather Pain phá được cây, hữu ích khi dọn Sporecap. Nhắm vào cụm cây thay vì tiêu hết lượt dùng lên boss. Dù có gậy, vẫn mang rìu dự phòng để xử lý cây còn sót hoặc khi lốc đi không đúng ý.',
          'Gợi ý hậu cần: chia vật tư thành bộ đang dùng và bộ thay thế, giao một người phụ trách dọn cây nếu chơi nhóm. Đặt đồ hồi máu, hồi tinh thần và thức ăn riêng để thao tác nhanh. Kiểm tra lượng vũ khí theo một trận dài, không dựa trên lượng đủ đánh các boss ngắn.',
        ],
        sources: [{ page: 'Weather_Pain' }, { page: 'Guides/Making_Bigger_and_Better_Weapons' }],
      },
      {
        id: 'volatile-canary',
        title: '3. Nhánh Misery: tạo Volatile Canary từ đầu',
        steps: [
          'Làm Friendly Scarecrow tại Science Machine từ một Pumpkin, ba Cut Grass và ba Boards. Dựng trên mặt đất, đặt Bird Trap gần đó trên nền khác Grass Turf (ví dụ Forest Turf), rồi mồi Seeds để bắt Canary màu vàng. Canary không đáp trên Grass Turf. Bird Trap cần ba Twigs, bốn Silk; đừng giết con chim đã bắt.',
          'Học Birdcage tại Alchemy Engine: sáu Gold Nuggets, hai Papyrus, hai Seeds. Thu Reeds ở đầm lầy để làm Papyrus; quan sát Tentacle khi hái. Mang nguyên liệu xuống hang và xây lồng tại điểm tiếp tế.',
          'Nhốt Canary dưới hang khi Toadstool còn tồn tại; sau khoảng 6–12 phút nó thành Volatile Canary. Không cần gọi boss lên để chờ. Kiểm tra đúng biến thể trước khi lấy chim ra, giữ ô trống và tránh thao tác nhầm thành giết chim.',
          'Khi toàn bộ nhóm đã sẵn sàng, thả Volatile Canary sát mũ nấm để nó nổ và đổi mũ sang Misery. Chặt mũ đã đổi trước khi trạng thái hết sau tám phút. Đừng thả chim ở lồng tiếp tế rồi mới đi tới hố.',
        ],
        sources: [{ page: 'Canary' }, { page: 'Friendly_Scarecrow' }, { page: 'Bird_Trap/DST' }, { page: 'Birdcage' }, { page: 'Toadstool' }],
      },
      {
        id: 'sporecaps',
        title: '4. Dọn Sporecap trước khi đánh tiếp',
        paragraphs: [
          'Sporecap tăng sức mạnh và giảm sát thương boss nhận; mức cao nhất chặn 80% ở bản thường, 99% ở Misery. Đây là lý do đánh mãi không xuống máu. Chặt cây để giảm cấp cường hóa.',
          'Gợi ý xử lý: ngay khi cây xuất hiện, chuyển từ đua sát thương sang mở một vùng sạch. Người giữ boss nên tạo khoảng cách cho người chặt, không kéo nguy hiểm xuyên qua cụm đang dọn. Khi chơi đơn, chọn cây dễ tới trước rồi quay lại đánh sau; cố đứng đánh giữa rừng cây chỉ kéo dài trận và làm hao giáp.',
          'Theo dõi rìu hoặc số lượt gậy sau mỗi đợt. Có thể dành Pan Flute tạo khoảng nghỉ để dọn cây. Duy trì một ô dụng cụ cố định để không mở túi tìm đồ trong lúc khẩn cấp.',
        ],
        sources: [{ page: 'Toadstool', label: 'Sporecap và Tips' }, { page: 'Weather_Pain' }, { page: 'Damage_Reduction' }],
      },
      {
        id: 'clouds-and-retreat',
        title: '5. Đặt khí độc đúng chỗ, giữ đường rút',
        paragraphs: [
          'Spore Bomb nổ sau 3,5 giây, để mây độc một phút, gây đau và làm đồ dễ hỏng thối nhanh. Boomshroom mọc rồi nổ. Dưới 40% máu, boss thêm chuỗi hai cú nhảy và động đất.',
          'Gợi ý di chuyển: người dính bom chạy ra mép đã quy ước, bỏ mây độc tại đó rồi vòng về bằng đường sạch. Không chạy tới kho đồ hay đồng đội đang chặt cây. Khi thấy nấm nổ mọc quanh chân, tìm khoảng trống trước khi tính chuyện đánh thêm.',
          'Hãy đặt ngưỡng rút trước trận: hết giáp dự phòng, thiếu ánh sáng hoặc không còn đường sạch thì dừng. Boss sẽ chui xuống nếu bỏ trận; chấp nhận mất công thay vì để cả nhóm chết và phải nhặt đồ giữa hang. Khi còn tiếp tục, bổ sung tinh thần trong khoảng nghỉ và luôn chừa khả năng né cú nhảy tiếp theo.',
        ],
        sources: [{ page: 'Toadstool' }, { page: 'Mushrooms', label: 'Thức ăn hồi tinh thần và máu' }],
      },
      {
        id: 'fungal-rewards',
        title: '6. Học blueprint, sử dụng da nấm và đánh lại',
        paragraphs: [
          'Thu Shroom Skin và blueprint trước khi rời bãi. Bản thường mở cơ hội lấy Funcap và đèn nấm; Misery bảo đảm blueprint Glowcap và Napsack. Sau khi giết, chờ 20 ngày rồi kiểm tra lại các hố, không chỉ hố cũ.',
          'Mushlight và Glowcap phục vụ chiếu sáng căn cứ. Chúng nhận nhiều nguồn sáng như Light Bulbs và Glow Berries; Glowcap còn nhận bào tử nấm. Sau này, Enlightened Shard có thể giúp duy trì đèn lâu dài. Vì vậy hãy giữ nguyên liệu hiếm cho công trình dự định xây, tránh dùng hết trước khi đọc công thức.',
          'Trước lần lặp tiếp theo, ghi lại thứ hết đầu tiên: ánh sáng, rìu, giáp hay hồi tinh thần. Bổ sung đúng điểm yếu đó. Nếu muốn Misery, hoàn tất dây chuyền chim từ trước và chỉ đổi mũ khi đã sẵn sàng; thắng bản thường một lần chưa có nghĩa kho dự trữ đã đủ cho bản khó.',
        ],
        sources: [{ page: 'Toadstool' }, { page: 'Mushroom_Lights' }, { page: 'Enlightened_Shard' }, { page: 'Funcap' }, { page: 'Napsack' }],
      },
    ],
    rewards: [
      { name: 'Shroom Skin', use: 'Nguyên liệu cho các công thức nấm đã học.', page: 'Shroom_Skin' },
      { name: 'Mushlight / Glowcap', use: 'Blueprint xây đèn nấm cho căn cứ.', page: 'Mushroom_Lights' },
      { name: 'Napsack blueprint', use: 'Mục tiêu đặc biệt của lần hạ Misery; mở công thức túi gây ngủ.', page: 'Napsack' },
    ],
    mistakes: [
      { question: 'Chim không đổi thành Volatile?', answer: 'Kiểm tra đúng Canary, lồng nằm dưới hang, boss chưa bị giết và đã chờ đủ 6–12 phút.' },
      { question: 'Tại sao Ham Bat và đồ hồi máu hỏng nhanh?', answer: 'Mây bào tử làm đồ dễ hỏng thối nhanh. Mang ít thực phẩm vào sân mỗi lượt, đặt phần dự trữ ngoài vùng đánh và tránh đứng trong mây.' },
      { question: 'Có cần giết bản thường rồi mới gọi Misery?', answer: 'Không. Chuyển mũ bằng Volatile Canary trước khi chặt; bản thường là bước luyện tập được khuyên dùng.' },
    ],
    next: [{ label: 'Trở về các tuyến boss', href: '/bosses' }],
  },
];
