import type { BossGuide } from "./guide-types";

export const explorationGuides: BossGuide[] = [
  {
    slug: "seasonal",
    title: "Boss theo mùa",
    description: "Deerclops, Moose/Goose, Antlion và Bearger: chuẩn bị theo thời tiết, bảo vệ trại, học né đòn và tận dụng phần thưởng.",
    difficulty: "Đầu → giữa game",
    location: "Mặt đất",
    summary: "Không phải bốn boss xuất hiện lần lượt ngay cạnh trại. Deerclops và Bearger có cảnh báo; Moose/Goose ở tổ; Antlion phải tìm trong Oasis Desert. Đi theo mùa đang có, đánh dấu chỗ cần quay lại.",
    preparations: [
      "Một vũ khí còn tốt, giáp và mũ dự phòng, thức ăn hồi máu và hồi Sanity. Với lần tập đầu, ưu tiên sống qua một vòng đòn rồi mới tăng số lần phản công.",
      "Mùa đông: nguồn sưởi và Thermal Stone ấm. Mùa xuân: chống ướt. Mùa hè: đá lạnh và phương án làm mát; đừng chỉ mang giáp rồi bỏ qua thời tiết.",
      "Mang nguồn sáng độc lập; chừa lối chạy rộng và chọn sân xa kho đồ, vườn, bếp. Đặt bộ đồ dự phòng ở nơi không nằm trong đường truy đuổi.",
      "Antlion cần Thermal Stone ở nhiệt độ đủ nóng/lạnh để kích hoạt; Desert Goggles giúp đi trong bão cát. Guide có bước kiếm kính bên dưới.",
    ],
    sections: [
      { id: "lich-mua", title: "Lập lịch săn theo mùa", paragraphs: [
        "Với thế giới mặc định, xuân/thu dài 20 ngày, đông/hè dài 15 ngày. Dùng mùa làm mốc chuẩn bị thay vì áp một ngày xuất hiện tuyệt đối: thời gian ở hang, cấu hình và mùa khởi đầu có thể ảnh hưởng trải nghiệm.",
        "Gợi ý thực hành: mùa thu dựng nền thức ăn và đồ dự phòng; mùa đông xử lý Deerclops và tìm Klaus; xuân lấy lông từ Moose/Goose; hè xử lý Antlion. Bearger là mục tiêu mùa thu khi nó xuất hiện, không nên ngồi chờ nó trong trại.",
      ], sources: [{ page: "Seasons/World", label: "Mùa trong DST" }] },
      { id: "deerclops", title: "Deerclops: đón ở ngoài trại", steps: [
        "Khi nghe tiếng cảnh báo, mang đồ rời căn cứ đến sân đã chọn. Đừng đợi nó xuất hiện trong kho rồi mới chạy.",
        "Dụ cú vung tay bằng cách tiến gần, lùi đủ xa cho đòn trượt, rồi quay lại đánh ngắn. Đòn rộng hơn nhiều quái thường; đứng sát sau lưng cũng không phải bảo đảm an toàn.",
        "Nếu bị trúng và nhiễm lạnh, ưu tiên thoát chuỗi đòn, giữ nhiệt rồi hồi phục. Theo dõi Sanity để tránh vừa đánh boss vừa bị quái bóng vây.",
        "Nhặt Deerclops Eyeball và dành cho Eyebrella; đừng ăn mất nguyên liệu chính chỉ vì thấy nó hồi máu.",
      ], tips: ["Khi chưa quen, một vòng né sạch đáng giá hơn vài hit tham. Sân có ánh sáng và nhiệt ổn định giúp bạn tập trung vào động tác boss."], sources: [{ page: "Deerclops" }, { page: "Guides/Preparing_for_Deerclops", label: "Chuẩn bị Deerclops" }] },
      { id: "eyebrella", title: "Đổi phần thưởng mùa đông thành đồ đi mùa xuân", paragraphs: [
        "Tại Alchemy Engine, dùng 1 Deerclops Eyeball + 15 Twigs + 4 Bone Shards để làm Eyebrella. Nó che mưa và làm chậm quá nhiệt; giữ Sewing Kit để sửa thay vì chế lại mỗi mùa.",
        "Eyebrella nằm ở ô đầu. Khi dùng nó trong trận, hãy kiểm tra giáp thân; nếu đổi sang mũ giáp thì nhớ xử lý mưa bằng phương án khác. Bảo vệ thời tiết và chống đòn là hai nhu cầu khác nhau.",
      ], sources: [{ page: "Eyebrella/DST", label: "Eyebrella trong DST" }] },
      { id: "moose", title: "Moose/Goose và đàn Moslings", steps: [
        "Tìm các tổ Moose/Goose trên bản đồ vào xuân. Không phải tổ nào cũng có mẹ; đánh dấu tổ có trứng hoặc con non để quay lại.",
        "Khi đánh mẹ, dụ đòn húc rồi phản công. Để ý tiếng honk có thể làm rơi vật đang cầm: nhặt và trang bị lại khi an toàn, không đứng đánh tay không mà không nhận ra.",
        "Đàn Moslings có thể gọi mẹ khi bị đánh. Nếu mẹ đã chết, chúng nổi giận và xoáy lao; chạy ngang đường lao, chờ chúng chóng mặt rồi xử lý từng con.",
        "Thu Down Feathers. Giữ một phần để làm Weather Pain cho các trận cần dọn mục tiêu phụ, thay vì dùng hết ngay.",
      ], tips: ["Đừng chồng trận này với mưa ếch hoặc một nhóm quái đang đuổi. Nếu sân quá hỗn loạn, dọn mối nguy ngoài trước rồi mới gọi giao chiến."], sources: [{ page: "Moose/Goose/DST" }, { page: "Mosling" }, { page: "Weather_Pain" }] },
      { id: "kinh-sa-mac", title: "Chuẩn bị kính và làm mát để tìm Antlion", steps: [
        "Tìm Oasis Desert — sa mạc có hồ Oasis, khác khu dung nham Dragonfly. Vào hè, câu ở hồ bằng Fishing Rod để kiếm Crumpled Packages có thể chứa blueprint Desert Goggles.",
        "Học Fashion Goggles tại Science Machine, rồi dùng nó cùng Pig Skin để chế Desert Goggles sau khi đã học blueprint. Fashion Goggles đơn thuần không chống bão cát.",
        "Chuẩn bị Thermal Stone lạnh ở Ice Box hoặc gần lửa lạnh, cùng phương án làm mát dự phòng. Đừng để cả hành trình dài làm đá trở lại nhiệt độ thường trước lúc kích hoạt boss.",
      ], sources: [{ page: "Desert_Goggles" }, { page: "Thermal_Stone" }] },
      { id: "antlion", title: "Antlion: kích hoạt rồi né gai cát", steps: [
        "Tìm Antlion trong Oasis Desert vào hè. Bình thường nó là NPC nhận cống phẩm; đưa Thermal Stone lạnh cóng hoặc đủ nóng để chuyển sang trạng thái boss.",
        "Di chuyển khỏi vị trí gai sắp mọc, rồi trở lại tấn công ở khoảng trống. Máu thấp làm mật độ gai nguy hiểm hơn; đừng tham đánh khi đường thoát đang bị chặn.",
        "Không bỏ gây sát thương quá lâu vì nó có thể tự hồi máu. Tuy vậy, vẫn ưu tiên né và hồi phục; đừng đứng yên chịu gai để giữ nhịp đánh.",
        "Nhận Desert Stones và blueprint The Lazy Deserter/Turf-Raiser Helm. Sau khi bị hạ, nó trở lại mùa hè tiếp theo theo mặc định.",
      ], tips: ["Nếu chưa muốn đánh, cống phẩm có thể trì hoãn phá hoại. Khi có cảnh báo sinkhole hoặc đá rơi, rời công trình quan trọng ngay."], sources: [{ page: "Antlion" }] },
      { id: "bearger", title: "Bearger: học nhịp đập đất và tránh mất vũ khí", steps: [
        "Khi có cảnh báo, rời căn cứ. Chọn khu trống xa rương và bếp vì Bearger tìm thức ăn và phá công trình.",
        "Nó mở giao chiến bằng cú đập đất; sau ba đòn cận chiến lại có đập đất. Dụ đòn rồi đánh ngắn, dành khoảng cách lớn hơn cho cú đập.",
        "Nếu bị hất vật cầm tay, lùi và trang bị lại trước khi quay vào. Chạy quá xa có thể dẫn đến cú đuổi lao, nên quan sát boss thay vì mặc định càng xa càng an toàn.",
        "Nếu đánh lúc nó ngủ đông/xuân, tính thêm tiếng ngáp gây ngủ. Đừng áp nguyên nhịp đánh mùa thu cho mọi tình huống.",
      ], tips: ["Gợi ý: để đồ hồi phục trong túi dễ dùng và tránh quay trận đánh về nơi cất đồ. Lần đầu không cần kết hợp vừa đánh vừa nhờ boss khai thác rừng."], sources: [{ page: "Bearger/DST" }] },
      { id: "danh-lai", title: "Đánh lại và chuyển sang boss đột biến", paragraphs: [
        "Sau mỗi trận, sửa trang bị rồi đánh dấu mùa/mục tiêu chưa hoàn thành. Moose/Goose có thể xuất hiện ở nhiều tổ; Antlion theo mùa hè, còn những lần sinh boss khác phụ thuộc thiết lập thế giới.",
        "Khi Lunar Rift đã mở, Deerclops và Bearger thường có thể dẫn sang dạng đột biến sau khi chết. Chỉ gọi trận khi nhóm còn đủ giáp planar, hồi máu và ánh sáng để xử lý phần tiếp nối; xem guide Lunar trước khi trở lại farm chúng.",
      ], sources: [{ page: "Crystal_Deerclops" }, { page: "Armored_Bearger" }] },
    ],
    rewards: [
      { name: "Deerclops Eyeball → Eyebrella", use: "Giữ mắt để chế đồ chống mưa và giảm quá nhiệt, giúp những chuyến săn sau ổn định hơn.", page: "Eyebrella/DST" },
      { name: "Down Feathers → Weather Pain", use: "Lông từ nhánh Moose/Goose là nguyên liệu công cụ lốc đánh diện rộng, hữu ích ở Toadstool và Fuelweaver.", page: "Weather_Pain" },
      { name: "Thick Fur", use: "Nguyên liệu từ Bearger cho đồ như Hibearnation Vest và Insulated Pack; chọn công dụng theo nhu cầu chuyến đi.", page: "Thick_Fur" },
      { name: "Desert Stones & blueprint", use: "Nhánh Antlion mở công cụ The Lazy Deserter; đây không phải gậy The Lazy Explorer của Ruins.", page: "The_Lazy_Deserter" },
    ],
    mistakes: [
      { question: "Đã tới ngày dự kiến mà không thấy boss?", answer: "Kiểm tra đúng mùa, thiết lập spawn, thời gian ở hang và khu vực cần tìm. Đừng áp lịch ngày cố định của save khác cho thế giới của mình." },
      { question: "Đội kính rồi vẫn bị bão cát làm chậm?", answer: "Kiểm tra đó có phải Desert Goggles không. Fashion Goggles chỉ là nguyên liệu trung gian, không cho cùng hiệu ứng." },
      { question: "Không đánh được Antlion?", answer: "Nó có thể vẫn ở trạng thái nhận cống phẩm. Dùng Thermal Stone đủ nóng hoặc lạnh; đá trở lại bình thường không khởi động trận như mong muốn." },
      { question: "Boss chết nhưng vẫn chưa an toàn?", answer: "Moose có đàn con cần xử lý; khi Lunar Rift hoạt động, một số xác boss có thể bị nhập và biến đổi. Giữ đồ chiến đấu cho tới khi khu vực thật sự yên." },
    ],
    next: [{ label: "Klaus trong mùa đông", href: "/bosses/klaus" }, { label: "Dragonfly ở sa mạc", href: "/bosses/dragonfly" }, { label: "Boss đột biến Lunar", href: "/lunar-rift#boss" }],
  },
  {
    slug: "ocean",
    title: "Boss biển: Malbatross & Frostjaw",
    description: "Từ đóng thuyền và câu cá đến Malbatross, Frostjaw: giữ thuyền nổi, né bộ đòn và đổi phần thưởng sau trận.",
    difficulty: "Giữa game",
    location: "Đại dương",
    summary: "Hai mục tiêu độc lập: Malbatross xuất hiện quanh đàn Deep Bass ngoài biển; Frostjaw được gọi bằng việc câu tại Ice Fishing Hole trên Ice Sheet. Crab King thuộc tuyến Lunar và được liên kết ở cuối bài.",
    preparations: [
      "Làm quen điều khiển thuyền gần bờ trước: có Oar dự phòng, Anchor để dừng, ánh sáng và đủ vật liệu sửa. Kiểm tra máu thuyền chứ không chỉ máu nhân vật.",
      "Sea Fishing Rod và mồi/phao phù hợp. Fishing Rod câu ao không thay thế cần câu biển để gọi Frostjaw.",
      "Vũ khí, giáp, hồi máu, chống lạnh/ướt. Đừng xếp kín boong bằng rương khiến không còn chỗ né.",
      "Chuẩn bị hành lý cứu hộ ở bờ. Với Malbatross, nên dùng thuyền chiến đấu riêng thay vì mang cả căn cứ nổi quý giá vào trận.",
    ],
    sections: [
      { id: "dong-thuyen", title: "Đóng thuyền và chuẩn bị sửa chữa", steps: [
        "Dựng Think Tank, tìm nhóm chế tạo Seafaring, làm Boat Kit rồi hạ xuống biển. Mang Oar để chèo, lắp Anchor để giữ vị trí.",
        "Chuẩn bị Boat Patches để xử lý lỗ thủng và gỗ/ván sửa máu thuyền. Để chúng trong ô dễ lấy; máu nhân vật đầy không cứu được thuyền đang chìm.",
        "Dùng đèn hoặc nguồn lửa có cấu trúc an toàn như Fire Pit. Không đặt Campfire trần trên thuyền gỗ vì có thể gây cháy.",
        "Thử neo, nhổ neo và quay lại bờ. Gợi ý chia việc nhóm: một người sửa/điều khiển khi cần, những người còn lại giữ boss và nhặt đồ.",
      ], sources: [{ page: "Seafaring_Filter" }, { page: "Boat" }] },
      { id: "cau-ca", title: "Câu biển trước khi tìm boss", paragraphs: [
        "Sea Fishing Rod có chỗ lắp phao và mồi; lure giúp cá cắn hiệu quả hơn. Chuẩn bị cần trước chuyến đi và tập câu ở vùng dễ kiểm soát, thay vì học thao tác trong lúc boss áp sát.",
        "Sau khi cá mắc câu, quan sát cần: lúc cần dựng cao và cá vùng vẫy thì ngừng kéo; khi cần hạ và cá bơi về phía mình thì kéo tiếp. Cố kéo khi dây căng có thể làm đứt dây và mất mồi/phao; buông quá lâu khi dây chùng lại để cá thoát.",
        "Giữ cá sống nếu định đổi phần thưởng Frostjaw. Phân biệt cá biển còn sống với Fish Morsel hoặc cá đã nấu; món ăn chế biến không thay thế đúng vật trao đổi.",
      ], tips: ["Gợi ý: chừa ô trống trong túi, đem thêm bộ mồi và phao dự phòng. Đừng dùng hết vật liệu câu ở điểm săn Malbatross rồi mới đi tìm đảo băng."], sources: [{ page: "Lures" }, { page: "Sea_Fishing_Rod" }] },
      { id: "malbatross", title: "Tìm và gọi Malbatross", steps: [
        "Tìm Deep Bass Shoal có biểu tượng đàn cá trên bản đồ. Không phải mọi đàn đều gọi boss khi bạn vừa đến.",
        "Câu Deep Bass ở đàn để có cơ hội gặp nó. Nếu không xuất hiện, đánh dấu vị trí, kiểm tra đàn khác hoặc quay lại sau; không cần bấm lại liên tục một nơi.",
        "Khi đã sẵn sàng, giữ thuyền neo và khoảng trống trên boong. Việc câu ở đàn khi Malbatross có mặt có thể khiến nó nổi giận.",
      ], sources: [{ page: "Malbatross" }] },
      { id: "danh-malbatross", title: "Malbatross: vừa né, vừa giữ thuyền", steps: [
        "Dụ đòn sát mép tầm rồi chuyển sang khoảng boong trống để né; phản công khi nó còn trong tầm. Đừng chạy dồn tất cả đồng đội vào cùng một góc.",
        "Khi boss lặn/rời xa, xử lý sóng và kiểm tra thuyền, không chỉ mải đuổi theo để thêm hit.",
        "Giai đoạn cuối có cú sà phá Mast. Thuyền chiến đấu dùng mái chèo, không chở cột buồm quý, giảm thứ có thể mất trong trận.",
      ], tips: ["Nếu thuyền nguy cấp, ngừng tham sát thương để sửa. Trận đầu nên luyện cách giữ vị trí và đổi vai sửa thuyền; bạn có thể trở lại săn khi đã có hành trang ổn định."], sources: [{ page: "Malbatross" }, { page: "Boat" }] },
      { id: "tim-frostjaw", title: "Ice Sheet: tìm đảo băng và câu ba con cá", steps: [
        "Khám phá Rough Ocean để tìm Ice Sheet với Mini Glaciers và Ice Fishing Hole. Mặt băng lớn hơn vào đông và nhỏ lại vào xuân.",
        "Đỗ thuyền để còn đường về, chuẩn bị giáp và chống lạnh rồi lên băng. Tránh chạy trượt liên tục sát mép.",
        "Dùng Sea Fishing Rod câu đủ 3 Deep Bass từ Ice Fishing Hole để gọi Frostjaw. Nó ban đầu trung lập; chỉ bắt đầu đánh sau khi nhóm đã sẵn sàng.",
      ], sources: [{ page: "Ice_Sheet" }, { page: "Frostjaw" }] },
      { id: "danh-frostjaw", title: "Frostjaw: nhận biết ba lượt tấn công", steps: [
        "Cận chiến: né hết hai cú quạt rồi cú đuôi hất lùi, sau đó mới vào phản công.",
        "Tường băng: rời hướng đường lao giữa hai hàng gai; không đứng chặn đường chỉ vì đang có giáp.",
        "Bơi dưới băng: quan sát vây, tiếp tục di chuyển để tránh điểm bật lên và điểm đáp. Giữ vị trí gần vùng băng trung tâm.",
      ], tips: ["Mép đảo có thể vỡ trong trận, đặc biệt trên đảo lớn mùa đông. Đừng nhảy lên mảnh Ice Boat đang trôi để cố né vì nó chỉ tồn tại tạm thời."], sources: [{ page: "Frostjaw" }, { page: "Ice_Sheet" }] },
      { id: "doi-ca", title: "Sau chiến thắng: đổi cá trước khi rời đi", paragraphs: [
        "Frostjaw chịu thua và chuyển lại trung lập, không phải chết thành một đống loot thông thường. Đưa cá biển hợp lệ cho nó để nhận Bootleg Getaway; cá nặng có phần thưởng tốt hơn. Giữ các Deep Bass đã câu là lựa chọn dễ nhớ.",
        "Bootleg Getaway tạo cặp cổng biển tạm thời. Đứng trên thuyền/bè, dùng vật phẩm rồi chọn vùng biển đã khám phá trên bản đồ. Chọn khoảng nước đủ trống ở cả hai đầu để thuyền đi qua.",
        "Đừng rời vùng rồi mới quay lại tìm NPC đổi đồ. Ice Sheet tan sau chiến thắng; theo mặc định, khu này xuất hiện lại ở vị trí ngẫu nhiên sau 20 ngày. Hãy kiểm tra bản đồ khi muốn đánh lại.",
      ], sources: [{ page: "Frostjaw" }, { page: "Bootleg_Getaway" }, { page: "Ice_Sheet" }] },
      { id: "ve-bo", title: "Mang loot về và chọn chuyến biển tiếp", paragraphs: [
        "Nhặt Malbatross Bill để chèo, giữ Malbatross Feathers cho Feathery Canvas và Winged Sail. Lắp buồm tốt trên thuyền hành trình sau khi đã sửa chữa, thay vì đưa ngay vào trận tiếp theo.",
        "Gợi ý sau chuyến đầu: bổ sung gỗ, vá hết rò, cất đồ quý và chụp/ghi dấu các điểm biển đã gặp. Malbatross có hồi sinh, nhưng không phải quay đúng một chỗ là sẽ gặp ngay.",
        "Crab King nằm trong lộ trình lấy bàn thờ Mặt Trăng. Nếu mục tiêu là Celestial Champion, đọc kỹ bước Pearl’s Pearl trước khi gọi Crab King để không phải làm lại vì thiếu điều kiện nhiệm vụ.",
      ], sources: [{ page: "Malbatross_Bill" }, { page: "Mast", label: "Winged Sail" }, { page: "Crab_King" }] },
    ],
    rewards: [
      { name: "Malbatross Bill", use: "Mái chèo tốt cho các chuyến khám phá biển tiếp theo.", page: "Malbatross_Bill" },
      { name: "Malbatross Feathers", use: "Chế Feathery Canvas, dùng cho Winged Sail.", page: "Feathery_Canvas" },
      { name: "Bootleg Getaway", use: "Đổi cá với Frostjaw sau chiến thắng để lấy vật phẩm tạo cổng biển tạm thời tới vùng đã khám phá.", page: "Bootleg_Getaway" },
    ],
    mistakes: [
      { question: "Câu ở biển mãi mà Frostjaw không lên?", answer: "Phải câu tại Ice Fishing Hole trên Ice Sheet, không phải một đàn Deep Bass bất kỳ. Hai boss sử dụng cá nhưng khác địa điểm gọi." },
      { question: "Boss chưa giết được tôi mà tôi vẫn thất bại?", answer: "Thuyền có thanh máu riêng. Bịt rò và sửa ván là phần bắt buộc của khâu chuẩn bị; một người giữ vai trò sửa khi đi nhóm sẽ dễ kiểm soát hơn." },
      { question: "Frostjaw ngừng đánh mà không rơi phần thưởng?", answer: "Nó đã chịu thua. Tiếp cận để đổi cá hợp lệ lấy Bootleg Getaway trước khi rời khu vực." },
      { question: "Không thấy Ice Sheet ở vị trí cũ?", answer: "Sau lần hạ Frostjaw, đảo tan và lần tái xuất hiện có thể ở nơi khác. Khám phá lại biển khi hết thời gian chờ." },
    ],
    next: [{ label: "Pearl và Crab King", href: "/lunar-rift#truoc-rift" }, { label: "Klaus để săn loot", href: "/bosses/klaus" }, { label: "Tất cả tuyến boss", href: "/bosses" }],
  },
];
