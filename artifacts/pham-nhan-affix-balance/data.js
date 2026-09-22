(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AffixBalanceCatalog = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const rows = [];
  const SOURCE_ENCHANT = 'scripts/enums/hh_enchant.lua';
  const SOURCE_EFFECTS = 'scripts/enums/hh_effects.lua';
  const SOURCE_DUNGEON = 'scripts/components/hh_dungeon_effects.lua';
  const SOURCE_ALCHEMY = 'scripts/components/ttk_alchemy_effects.lua';

  function add(row) {
    rows.push({
      numericId: '',
      family: row.name,
      slot: 'Mọi trang bị',
      exclusiveGroup: '',
      cap: '',
      source: SOURCE_ENCHANT,
      decision: row.status === 'Đang có' ? 'Giữ và cân lại' : 'Đánh giá',
      note: '',
      ...row,
      key: row.key || row.code,
    });
  }

  function existingTierFamily(def) {
    for (const entry of def.entries) {
      add({
        family: def.family,
        code: entry.code,
        numericId: String(entry.id ?? ''),
        name: entry.name,
        tier: entry.tier,
        category: def.category,
        slot: def.slot,
        status: 'Đang có',
        effectKey: def.effectKey,
        current: entry.value,
        proposed: entry.value,
        cap: def.cap || '',
        exclusiveGroup: def.exclusiveGroup || '',
        source: entry.source || SOURCE_ENCHANT,
        note: entry.note || def.note || '',
      });
    }
  }

  function proposalFamily(def) {
    const tiers = ['I', 'II', 'III', 'IV', 'V'];
    tiers.forEach((tier, index) => add({
      family: def.family,
      code: `${def.code}_${tier.toLowerCase()}`,
      name: `${def.family} ${tier}`,
      tier,
      category: def.category,
      slot: def.slot,
      status: def.status,
      effectKey: def.effectKey,
      current: 'Chưa có',
      proposed: def.values[index],
      cap: def.cap || '',
      exclusiveGroup: def.exclusiveGroup || '',
      source: def.source,
      note: def.note || '',
    }));
  }

  function utility(def) {
    add({
      family: def.name,
      code: def.code,
      name: def.name,
      tier: 'UTILITY',
      category: 'Tiện ích',
      slot: def.slot || 'Mọi trang bị',
      status: def.status || 'Đề xuất - adapter',
      effectKey: def.effectKey,
      current: 'Chưa có',
      proposed: def.value,
      cap: def.cap || '1 hiệu ứng',
      exclusiveGroup: def.exclusiveGroup || 'utility',
      source: def.source,
      decision: def.decision || 'Đánh giá',
      note: def.note || '',
    });
  }

  // Catalog hiện hành: 59 khai báo trực tiếp và 12 affix sinh theo tier.
  add({ code:'follow_reduce_damage', numericId:'96', name:'Trợ Thủ-PT', family:'Trợ thủ phòng thủ', tier:'IV', category:'Đệ tử', slot:'Mọi trang bị', status:'Đang có', effectKey:'addFollowReduceDamage', current:'Giảm 5-10 ST đệ tử nhận', proposed:'Giảm 5-10 ST đệ tử nhận', source:SOURCE_ENCHANT });
  add({ code:'follow_add_damage', numericId:'95', name:'Trợ Thủ-TC', family:'Trợ thủ tấn công', tier:'IV', category:'Đệ tử', slot:'Mọi trang bị', status:'Đang có', effectKey:'addFollowDamage', current:'Tăng 10-20 ST đệ tử', proposed:'Tăng 10-20 ST đệ tử', source:SOURCE_ENCHANT });
  add({ code:'fast_act', numericId:'94', name:'Tháo Vát-TH', family:'Tương tác nhanh', tier:'UTILITY', category:'Tiện ích', slot:'Mọi trang bị', status:'Đang có', effectKey:'fast_act', current:'Tăng tốc thu hoạch, xây, đổi, chế tạo, nấu', proposed:'Giữ nguyên', source:SOURCE_ENCHANT });
  add({ code:'work_speed', numericId:'93', name:'Tháo Vát-KT', family:'Khai thác nhanh', tier:'UTILITY', category:'Tiện ích', slot:'Mọi trang bị', status:'Đang có', effectKey:'workAddSpeed', current:'Gấp đôi tốc độ làm việc', proposed:'Gấp đôi tốc độ làm việc', source:SOURCE_ENCHANT });
  add({ code:'shadow_camp', numericId:'92', name:'Phục Ma-BT', family:'Thân thiện Shadow', tier:'UTILITY', category:'Tiện ích', slot:'Mọi trang bị', status:'Đang có', effectKey:'shadowCamp', current:'Sinh vật shadow không tấn công', proposed:'Giữ nguyên', source:SOURCE_ENCHANT });
  add({ code:'moon_camp', numericId:'91', name:'Phục Ma-VĐ', family:'Thân thiện Gestalt', tier:'UTILITY', category:'Tiện ích', slot:'Mọi trang bị', status:'Đang có', effectKey:'moonCamp', current:'Sinh vật gestalt không tấn công', proposed:'Giữ nguyên', source:SOURCE_ENCHANT });
  add({ code:'add_speed', numericId:'89', name:'Nhanh Nhẹn', family:'Tốc chạy', tier:'III', category:'Cơ động', slot:'Vũ khí', status:'Đang có', effectKey:'addSpeedPercent', current:'5-25%', proposed:'5-25%', source:SOURCE_ENCHANT });
  add({ code:'add_light', numericId:'90', name:'☆Phổ Độ', family:'Phát sáng', tier:'UTILITY', category:'Tiện ích', slot:'Mọi trang bị', status:'Đang có', effectKey:'add_light', current:'Phát sáng khi trang bị', proposed:'Giữ nguyên', source:SOURCE_ENCHANT });

  existingTierFamily({ family:'Bền Bỉ', category:'Độ bền', slot:'Trang bị có độ bền', effectKey:'add_max_use', entries:[
    {tier:'I', code:'add_max_use_small', id:87, name:'Bền Bỉ I', value:'+20-80 độ bền'},
    {tier:'II', code:'add_max_use_big', id:88, name:'Bền Bỉ II', value:'+40-160 độ bền'},
  ]});
  existingTierFamily({ family:'Bạo Kích', category:'Tấn công', slot:'Không phải giáp', effectKey:'criticalHitRate + criticalHitEffect', entries:[
    {tier:'I', code:'add_critical_hit_rate_small', id:79, name:'Bạo Kích I', value:'+1-10% tỷ lệ và ST chí mạng'},
    {tier:'II', code:'add_critical_hit_rate_med', id:80, name:'Bạo Kích II', value:'+1-20% tỷ lệ và ST chí mạng'},
    {tier:'III', code:'add_critical_hit_rate_big', id:77, name:'☆Bạo Kích III', value:'+1-30% tỷ lệ và ST chí mạng'},
    {tier:'IV', code:'add_critical_hit_rate_special', id:78, name:'★Bạo Kích IV', value:'+1-50% tỷ lệ và ST chí mạng'},
  ]});
  existingTierFamily({ family:'Liên Kích', category:'Tấn công', slot:'Vũ khí', effectKey:'atk_speed', exclusiveGroup:'attack_speed', entries:[
    {tier:'I', code:'atk_speed_small', id:75, name:'Liên Kích I', value:'+5-10% tốc đánh'},
    {tier:'II', code:'atk_speed_med', id:76, name:'Liên Kích II', value:'+15-25% tốc đánh'},
    {tier:'III', code:'atk_speed_big', id:73, name:'☆Liên Kích III', value:'+30-45% tốc đánh'},
    {tier:'IV', code:'atk_speed_special', id:74, name:'★Liên Kích IV', value:'+50-70% tốc đánh'},
  ]});
  existingTierFamily({ family:'Gia Trì', category:'Độ bền', slot:'Trang bị có độ bền', effectKey:'durabilityRegen', entries:[
    {tier:'I', code:'restore_use_10s_1use', id:71, name:'Gia Trì I', value:'Hồi 1 độ bền mỗi 10 giây'},
    {tier:'II', code:'restore_use_5s_1use', id:72, name:'Gia Trì II', value:'Hồi 1 độ bền mỗi 5 giây'},
    {tier:'III', code:'restore_use_3s_1use', id:69, name:'☆Gia Trì III', value:'Hồi 1 độ bền mỗi giây', note:'Tên code còn ghi 3s nhưng mô tả và runtime dùng 1s.'},
    {tier:'IV', code:'restore_use_1s_2_percent', id:70, name:'★Gia Trì IV', value:'Hồi 2% độ bền mỗi giây'},
  ]});
  existingTierFamily({ family:'Hộ Giáp', category:'Độ bền', slot:'Giáp', effectKey:'armorDurability', entries:[
    {tier:'I', code:'add_max_use_armor_01', id:67, name:'Hộ Giáp I', value:'+200-500 độ bền giáp'},
    {tier:'II', code:'add_max_use_armor_02', id:68, name:'Hộ Giáp II', value:'+500-1000 độ bền giáp'},
    {tier:'III', code:'add_max_use_armor_03', id:65, name:'☆Hộ Giáp III', value:'+1000-3000 độ bền giáp'},
    {tier:'IV', code:'armor_immune_amount', id:66, name:'★Hộ Giáp IV', value:'Giáp không mất độ bền', note:'value_range 10-80 không tham gia hiệu ứng chính.'},
  ]});
  existingTierFamily({ family:'Xuyên Giáp', category:'Tấn công', slot:'Vũ khí', effectKey:'trueDamageNum', cap:'Tổng 40%', exclusiveGroup:'armor_pierce', entries:[
    {tier:'I', code:'true_damage_small', id:63, name:'Xuyên Giáp I', value:'3-5% ST đòn chính bỏ qua giáp'},
    {tier:'II', code:'true_damage_med', id:64, name:'Xuyên Giáp II', value:'6-10% ST đòn chính bỏ qua giáp'},
    {tier:'III', code:'true_damage_big', id:61, name:'☆Xuyên Giáp III', value:'11-15% ST đòn chính bỏ qua giáp'},
    {tier:'IV', code:'true_damage_special', id:62, name:'★Xuyên Giáp IV', value:'16-20% ST đòn chính bỏ qua giáp'},
  ]});
  add({ code:'blood_outburst', numericId:'50', name:'Nghịch Cảnh-Máu', family:'Nghịch Cảnh', tier:'III', category:'Tấn công', slot:'Vũ khí', status:'Đang có', effectKey:'bloodOutburst', current:'Máu càng thấp, ST càng cao, tối đa 50%', proposed:'Tối đa 50%', cap:'Chỉ 1 loại Nghịch Cảnh', exclusiveGroup:'adversity', source:SOURCE_ENCHANT });
  add({ code:'spirit_fade', numericId:'48', name:'Nghịch Cảnh-Não', family:'Nghịch Cảnh', tier:'III', category:'Tấn công', slot:'Vũ khí', status:'Đang có', effectKey:'spiritFade', current:'Tinh thần càng thấp, ST càng cao, tối đa 50%', proposed:'Tối đa 50%', cap:'Chỉ 1 loại Nghịch Cảnh', exclusiveGroup:'adversity', source:SOURCE_ENCHANT });
  add({ code:'hunger_assault', numericId:'47', name:'Nghịch Cảnh-Đói', family:'Nghịch Cảnh', tier:'III', category:'Tấn công', slot:'Vũ khí', status:'Đang có', effectKey:'hungerAssault', current:'Độ no càng thấp, ST càng cao, tối đa 50%', proposed:'Tối đa 50%', cap:'Chỉ 1 loại Nghịch Cảnh', exclusiveGroup:'adversity', source:SOURCE_ENCHANT });
  existingTierFamily({ family:'Thanh Long', category:'Tấn công', slot:'Vũ khí', effectKey:'addComDamagePercent', exclusiveGroup:'dragon_damage', entries:[
    {tier:'I', code:'add_damage_small', id:33, name:'Thanh Long I', value:'+3-5% ST đòn chính'},
    {tier:'II', code:'add_damage_med', id:34, name:'Thanh Long II', value:'+6-10% ST đòn chính'},
    {tier:'III', code:'add_damage_big', id:31, name:'☆Thanh Long III', value:'+11-15% ST đòn chính'},
    {tier:'IV', code:'special_bhtg', id:32, name:'★Thanh Long IV', value:'+16-20% ST; Trọng Thương 3%, Boss 1%', note:'Trọng Thương tính theo máu hiện tại.'},
  ]});
  existingTierFamily({ family:'Bạch Hổ-G', category:'Phòng thủ', slot:'Mọi trang bị', effectKey:'absorbDamage', cap:'Tổng 80%', entries:[
    {tier:'I', code:'absorb_small', id:27, name:'Bạch Hổ-G1', value:'Giảm 1-5% ST nhận'},
    {tier:'II', code:'absorb_mid', id:28, name:'Bạch Hổ-G2', value:'Giảm 1-15% ST nhận'},
    {tier:'III', code:'absorb_big', id:25, name:'Bạch Hổ-G3', value:'Giảm 1-25% ST nhận'},
    {tier:'IV', code:'absorb_special', id:26, name:'☆Bạch Hổ-G4', value:'Giảm 1-35% ST nhận'},
  ]});
  existingTierFamily({ family:'Bạch Hổ', category:'Phòng thủ', slot:'Giáp', effectKey:'absorbDamage', cap:'Tổng 80%', entries:[
    {tier:'I', code:'reduce_damage_small', id:23, name:'Bạch Hổ I', value:'Giảm 1-5% ST nhận'},
    {tier:'II', code:'reduce_damage_mid', id:24, name:'Bạch Hổ II', value:'Giảm 5-15% ST nhận'},
    {tier:'III', code:'reduce_damage_big', id:21, name:'☆Bạch Hổ III', value:'Giảm 10-25% ST nhận'},
    {tier:'IV', code:'special_sgsy', id:22, name:'★Bạch Hổ IV', value:'Giảm cố định 80% ST và miễn Giảm Hồi Máu', note:'value_range 1-1000 không được dùng bởi runtime.'},
  ]});

  add({ code:'add_immune_cold', numericId:'20', name:'Huyền Vũ-Lạnh', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneCold', current:'Miễn lạnh cóng', proposed:'Miễn lạnh cóng', source:SOURCE_ENCHANT });
  add({ code:'add_immune_hot', numericId:'19', name:'Huyền Vũ-Nóng', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneHot', current:'Miễn quá nhiệt', proposed:'Miễn quá nhiệt', source:SOURCE_ENCHANT });
  add({ code:'add_immune_poison', numericId:'18', name:'Huyền Vũ-Độc', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immunePoison', current:'Miễn trúng độc', proposed:'Miễn trúng độc', source:SOURCE_ENCHANT });
  add({ code:'add_immune_freeze', numericId:'17', name:'Huyền Vũ-Băng', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneFreeze', current:'Miễn đóng băng', proposed:'Miễn đóng băng', source:SOURCE_ENCHANT });
  add({ code:'immunity_moisture', numericId:'16', name:'Huyền Vũ-Ướt', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immunityMoisture', current:'Miễn ẩm ướt', proposed:'Miễn ẩm ướt', source:SOURCE_ENCHANT });
  add({ code:'immunity_reduce_speed', numericId:'15', name:'Huyền Vũ-Chậm', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneReduceSpeed + porter', current:'Miễn làm chậm', proposed:'Miễn làm chậm', source:SOURCE_ENCHANT, note:'value_range 10-80 hiện không được dùng.' });
  add({ code:'immune_sleep', numericId:'13', name:'Huyền Vũ-Ngủ', family:'Huyền Vũ', tier:'II', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immunitySleep', current:'Miễn ru ngủ', proposed:'Miễn ru ngủ', source:SOURCE_ENCHANT });
  add({ code:'immune_suppress', numericId:'11', name:'Miễn Giảm Hồi Máu', family:'Huyền Vũ', tier:'III', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneSuppressNum', current:'Miễn Giảm Hồi Máu', proposed:'Miễn Giảm Hồi Máu', source:SOURCE_ENCHANT });
  add({ code:'immune_debuff', numericId:'12', name:'☆Huyền Vũ-TT', family:'Huyền Vũ tổ hợp', tier:'III', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneHot + immuneCold + immunityMoisture', current:'Miễn nóng, lạnh và ướt', proposed:'Miễn nóng, lạnh và ướt', source:SOURCE_ENCHANT });
  add({ code:'immune_debuff_2', numericId:'9', name:'☆Huyền Vũ-KC', family:'Huyền Vũ tổ hợp', tier:'III', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'immuneFreeze + immunePoison + immuneReduceSpeed + immunitySleep', current:'Miễn băng, độc, chậm và ngủ', proposed:'Miễn băng, độc, chậm và ngủ', source:SOURCE_ENCHANT });
  add({ code:'special_zqrf', numericId:'10', name:'★Huyền Vũ-BX', family:'Huyền Vũ tổ hợp', tier:'IV', category:'Kháng hiệu ứng', slot:'Mọi trang bị', status:'Đang có', effectKey:'allStatusImmunity', current:'Miễn nóng, lạnh, băng, độc, ướt, chậm và ngủ', proposed:'Giữ nguyên', source:SOURCE_ENCHANT });
  add({ code:'health_suppress_num', numericId:'3', name:'Giảm Hồi Máu', family:'Giảm Hồi Máu', tier:'I', category:'Tấn công', slot:'Vũ khí', status:'Đang có', effectKey:'addSuppressAddHealth', current:'10-50% xác suất gây Giảm Hồi Máu', proposed:'10-50%', source:SOURCE_ENCHANT });
  add({ code:'atk_blood_suck', numericId:'1', name:'☆Chu Tước-HM', family:'Chu Tước', tier:'III', category:'Hồi phục', slot:'Vũ khí', status:'Đang có', effectKey:'bloodSuck', current:'Hút 1-3% ST hợp lệ', proposed:'1-3%', source:SOURCE_ENCHANT });
  add({ code:'special_xwsh', numericId:'2', name:'★Chu Tước-TM', family:'Chu Tước', tier:'IV', category:'Hồi phục', slot:'Vũ khí', status:'Đang có', effectKey:'bloodSuck + addSuppressAddHealth', current:'Hút 2-5% ST và gây Giảm Hồi Máu', proposed:'2-5%', source:SOURCE_ENCHANT });

  existingTierFamily({ family:'Bạo Phát', category:'Tấn công', slot:'Vũ khí', effectKey:'moreDamage proc', exclusiveGroup:'burst', entries:[
    {tier:'I', code:'more_damage_30_150', id:97, name:'Bạo Phát I', value:'30% gây x1,5 ST đòn chính'},
    {tier:'II', code:'more_damage_20_200', id:98, name:'Bạo Phát II', value:'20% gây x2 ST đòn chính'},
    {tier:'III', code:'more_damage_15_300', id:99, name:'Bạo Phát III', value:'10% gây x3 ST đòn chính', note:'ID lịch sử còn ghi 15 nhưng runtime dùng 10%.'},
    {tier:'IV', code:'more_damage_8_500', id:100, name:'Bạo Phát IV', value:'8% gây x5 ST đòn chính'},
  ]});
  existingTierFamily({ family:'Hạ Độc', category:'Hiệu ứng đòn đánh', slot:'Vũ khí', effectKey:'atkAddPoisonChance', exclusiveGroup:'poison', note:'Tối đa 5 tầng. Mỗi tầng gây 20% ST đòn đánh mỗi 2 giây trong 10 giây.', entries:[
    {tier:'I', code:'atk_add_poison_small', id:101, name:'Hạ Độc I', value:'10% xác suất'},
    {tier:'II', code:'atk_add_poison_med', id:102, name:'Hạ Độc II', value:'20% xác suất'},
    {tier:'III', code:'atk_add_poison_big', id:103, name:'Hạ Độc III', value:'30% xác suất'},
    {tier:'IV', code:'atk_add_poison_special', id:104, name:'Hạ Độc IV', value:'40% xác suất'},
  ]});
  existingTierFamily({ family:'Đóng Băng', category:'Hiệu ứng đòn đánh', slot:'Vũ khí', effectKey:'atkChanceAddFreeze', exclusiveGroup:'freeze', note:'Đóng băng 2 giây. Boss bị chậm 20% trong 2 giây. Hồi nội bộ 5 giây.', entries:[
    {tier:'I', code:'atk_add_freeze_small', id:105, name:'Đóng Băng I', value:'5% xác suất'},
    {tier:'II', code:'atk_add_freeze_med', id:106, name:'Đóng Băng II', value:'10% xác suất'},
    {tier:'III', code:'atk_add_freeze_big', id:107, name:'Đóng Băng III', value:'15% xác suất'},
    {tier:'IV', code:'atk_add_freeze_special', id:108, name:'Đóng Băng IV', value:'20% xác suất'},
  ]});

  // Family đề xuất: tất cả chỉ tồn tại khi trang bị món đồ.
  proposalFamily({ family:'Ảnh Bộ', code:'equip_dodge', effectKey:'chanceDodgeAttack', category:'Phòng thủ', slot:'Giày, giáp hoặc phụ kiện', status:'Đề xuất - dùng ngay', values:['2%','4%','6%','9%','12%'], cap:'Tổng né 70%; phần từ đá nên tối đa 20%', exclusiveGroup:'dodge', source:`${SOURCE_EFFECTS} + scripts/components/hh_player.lua`, note:'Runtime né đã có và đang clamp tổng ở 70%.' });
  proposalFamily({ family:'Chấn Kích', code:'equip_splash', effectKey:'addSplashDamageAOE', category:'Tấn công', slot:'Vũ khí', status:'Đề xuất - dùng ngay', values:['5%','8%','12%','18%','25%'], cap:'Tổng 60%', exclusiveGroup:'splash', source:`${SOURCE_EFFECTS} + scripts/combat/hh_combat_status.lua`, note:'Sát thương lan trong bán kính 3, không đánh đồng minh.' });
  proposalFamily({ family:'Trợ Kích', code:'equip_follower_crit', effectKey:'addFollowCritical', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - dùng ngay', values:['3%','5%','8%','12%','18%'], cap:'Tổng 40%', exclusiveGroup:'follower_crit', source:`${SOURCE_EFFECTS} + main/hh_api.lua`, note:'Cơ chế crit cho quái đi theo đã chạy trong runtime.' });
  proposalFamily({ family:'Đoạt Mệnh', code:'equip_execute', effectKey:'killUnderThreshold', category:'Tấn công', slot:'Vũ khí', status:'Đề xuất - adapter', values:['3% máu','5% máu','7% máu','10% máu','15% máu'], cap:'Không áp dụng Boss', exclusiveGroup:'finisher', source:'scripts/combat/hh_combat_status.lua', note:'Code hiện coi effect là boolean và kết liễu cố định ở 15%. Cần đọc giá trị tier.' });
  proposalFamily({ family:'Trảm Yêu', code:'equip_boss_damage', effectKey:'bossDamagePercent', category:'Tấn công', slot:'Vũ khí', status:'Đề xuất - adapter', values:['3%','5%','8%','12%','18%'], cap:'Tổng 30%', exclusiveGroup:'boss_damage', source:SOURCE_DUNGEON, note:'Chuyển cơ chế Beru Săn Boss thành modifier cho người chơi.' });
  proposalFamily({ family:'Phá Cương', code:'equip_armor_break', effectKey:'armorBreakChance', category:'Hiệu ứng đòn đánh', slot:'Vũ khí', status:'Đề xuất - adapter', values:['5%','8%','12%','16%','20%'], cap:'Debuff cố định 10%, 5 giây', exclusiveGroup:'armor_break', source:'scripts/enums/hh_monster.lua', note:'Mượn cơ chế atkAddArmorReduceBuff của quái. Cần cooldown nội bộ.' });
  proposalFamily({ family:'Lôi Linh', code:'equip_lightning_proc', effectKey:'lightningProcDamage', category:'Hiệu ứng đòn đánh', slot:'Vũ khí', status:'Đề xuất - adapter', values:['15 ST','30 ST','50 ST','75 ST','110 ST'], cap:'15% proc; hồi nội bộ 1 giây', exclusiveGroup:'element_proc', source:SOURCE_ALCHEMY, note:'Không dùng mức 180 ST trên mọi đòn của đan dược.' });
  proposalFamily({ family:'Nhật Sát', code:'equip_day_damage', effectKey:'dayDamagePercent', category:'Tấn công điều kiện', slot:'Vũ khí', status:'Đề xuất - adapter', values:['4%','7%','10%','15%','22%'], cap:'Chỉ hoạt động ban ngày', exclusiveGroup:'time_damage', source:'scripts/enums/hh_monster.lua', note:'Mượn cơ chế sunlightStrike của quái.' });
  proposalFamily({ family:'Dạ Sát', code:'equip_night_damage', effectKey:'nightDamagePercent', category:'Tấn công điều kiện', slot:'Vũ khí', status:'Đề xuất - adapter', values:['4%','7%','10%','15%','22%'], cap:'Chỉ hoạt động ban đêm', exclusiveGroup:'time_damage', source:'scripts/enums/hh_monster.lua', note:'Mượn cơ chế nightMenace của quái.' });
  proposalFamily({ family:'Hộ Mệnh', code:'equip_max_health', effectKey:'equipMaxHealthPercent', category:'Sinh tồn', slot:'Giáp hoặc phụ kiện', status:'Đề xuất - adapter', values:['5%','8%','12%','16%','22%'], cap:'Tổng từ đá 35%', exclusiveGroup:'max_health', source:SOURCE_DUNGEON, note:'Dùng external health modifier và hoàn nguyên đúng khi tháo đồ.' });
  proposalFamily({ family:'Sinh Cơ', code:'equip_health_regen', effectKey:'equipHealthRegen', category:'Hồi phục', slot:'Giáp hoặc phụ kiện', status:'Đề xuất - adapter', values:['0,2 HP/s','0,4 HP/s','0,7 HP/s','1 HP/s','1,5 HP/s'], cap:'Tổng 2 HP/s', exclusiveGroup:'health_regen', source:`${SOURCE_DUNGEON} + ${SOURCE_ALCHEMY}`, note:'Dùng hồi phẳng để không phình theo máu tối đa.' });
  proposalFamily({ family:'Linh Hải', code:'equip_max_mana', effectKey:'equipMaxMana', category:'Mana', slot:'Mũ hoặc phụ kiện', status:'Đề xuất - adapter', values:['+10','+20','+30','+45','+65'], cap:'Tổng từ đá +100 mana', exclusiveGroup:'mana_pool', source:'scripts/components/hh_mana.lua', note:'Cần cộng nguồn trang bị vào RecalculateMax.' });
  proposalFamily({ family:'Tụ Linh', code:'equip_mana_regen', effectKey:'equipManaRegen', category:'Mana', slot:'Mũ hoặc phụ kiện', status:'Đề xuất - adapter', values:['+0,1/s','+0,2/s','+0,35/s','+0,5/s','+0,75/s'], cap:'Tổng từ đá +1 mana/s', exclusiveGroup:'mana_regen', source:'scripts/components/hh_mana.lua', note:'Cộng vào GetRegenPerSecond, vẫn tôn trọng trì hoãn hồi mana.' });
  proposalFamily({ family:'Tiết Linh', code:'equip_mana_save', effectKey:'equipManaCostReduction', category:'Mana', slot:'Mũ hoặc phụ kiện', status:'Đề xuất - adapter', values:['3%','5%','8%','12%','18%'], cap:'Tổng giảm mana 50%', exclusiveGroup:'mana_cost', source:`scripts/components/hh_mana.lua + ${SOURCE_DUNGEON}`, note:'Áp dụng cho kỹ năng và chi phí duy trì, không cho chi phí bằng vật phẩm.' });
  proposalFamily({ family:'Ngộ Đạo', code:'equip_skill_cooldown', effectKey:'skillCooldownReduction', category:'Kỹ năng', slot:'Mũ hoặc phụ kiện', status:'Đề xuất - adapter', values:['2%','4%','6%','8%','12%'], cap:'Tổng 30%', exclusiveGroup:'cooldown', source:'scripts/components/hh_shadow_manager.lua + components kỹ năng', note:'Giảm phần cooldown mới tạo, không tua ngược timer đang chạy.' });
  proposalFamily({ family:'Hắc Sinh Mệnh', code:'equip_shadow_health', effectKey:'shadowHealthPercent', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['5%','8%','12%','16%','22%'], cap:'Tổng 40%', exclusiveGroup:'shadow_health', source:SOURCE_DUNGEON, note:'Cơ chế SetDungeonHealthMultiplier đã có trên shadow unit.' });
  proposalFamily({ family:'Hắc Công Kích', code:'equip_shadow_damage', effectKey:'shadowDamagePercent', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['4%','7%','10%','14%','20%'], cap:'Tổng 35%', exclusiveGroup:'shadow_damage', source:SOURCE_DUNGEON, note:'Áp dụng lên toàn bộ Shadow đang được triệu hồi.' });
  proposalFamily({ family:'Hắc Phòng Ngự', code:'equip_shadow_guard', effectKey:'shadowGuardPercent', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['3%','5%','8%','12%','16%'], cap:'Tổng 30%', exclusiveGroup:'shadow_guard', source:SOURCE_DUNGEON, note:'Dùng external absorb modifier của Shadow.' });
  proposalFamily({ family:'Hắc Tốc Hành', code:'equip_shadow_speed', effectKey:'shadowSpeedPercent', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['5%','8%','12%','16%','22%'], cap:'Tổng 35%', exclusiveGroup:'shadow_speed', source:SOURCE_DUNGEON, note:'Tăng tốc di chuyển, không thay đổi tầm đuổi mục tiêu.' });
  proposalFamily({ family:'Hắc Liên Kích', code:'equip_shadow_attack_speed', effectKey:'shadowAttackSpeed', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['3%','5%','8%','11%','15%'], cap:'Tổng 25%', exclusiveGroup:'shadow_attack_speed', source:SOURCE_DUNGEON, note:'Shadow unit đã có SetDungeonAttackSpeedMultiplier.' });
  proposalFamily({ family:'Hắc Tái Sinh', code:'equip_shadow_regen', effectKey:'shadowHealthRegen', category:'Đệ tử', slot:'Mọi trang bị', status:'Đề xuất - adapter', values:['0,1%/s','0,2%/s','0,3%/s','0,5%/s','0,75%/s'], cap:'Tổng 1% máu tối đa mỗi giây', exclusiveGroup:'shadow_regen', source:SOURCE_DUNGEON, note:'Tắt khi Shadow chết. Có thể cân nhắc chỉ hồi ngoài combat.' });
  proposalFamily({ family:'Quân Đoàn Ma', code:'equip_shadow_mana', effectKey:'shadowManaReduction', category:'Đệ tử', slot:'Mũ hoặc phụ kiện', status:'Đề xuất - adapter', values:['3%','5%','8%','12%','18%'], cap:'Tổng 40%', exclusiveGroup:'shadow_mana', source:`scripts/components/hh_mana.lua + ${SOURCE_DUNGEON}`, note:'Chỉ giảm mana triệu hồi và duy trì Shadow.' });

  utility({ name:'Nhiếp Vật', code:'utility_auto_pickup', effectKey:'utilityAutoPickup', value:'Tự nhặt trong bán kính 6', source:SOURCE_DUNGEON, note:'Mượn OrangeAmuletPickup. Không nhặt đồ đang cháy, trong container hoặc thuộc người khác.' });
  utility({ name:'Bền Lực', code:'utility_durability_save', effectKey:'utilityDurabilitySave', value:'25% không hao độ bền', source:SOURCE_DUNGEON, note:'Khác Bền Bỉ: đây là xác suất bảo toàn, không tăng dung lượng.' });
  utility({ name:'Bích Cốc', code:'utility_hunger_rate', effectKey:'utilityHungerRate', value:'Giảm 25% tốc độ hao đói', source:SOURCE_ALCHEMY, note:'Không dùng mức giảm 80% của Bích Cốc Đan.' });
  utility({ name:'Cường Kình', code:'utility_work_efficiency', effectKey:'utilityWorkEfficiency', value:'+35% hiệu suất chặt, đập và đào', source:SOURCE_ALCHEMY, note:'Không tăng tốc đào đất, hái hoặc thu hoạch.' });
  utility({ name:'Hàn Ngọc', code:'utility_cold_protection', effectKey:'utilityColdProtection', value:'+120 cách nhiệt mùa đông', source:SOURCE_ALCHEMY, note:'Là chống lạnh, không phải miễn nhiễm lạnh cóng.' });
  utility({ name:'Viêm Ngọc', code:'utility_heat_protection', effectKey:'utilityHeatProtection', value:'+120 cách nhiệt mùa hè', source:SOURCE_ALCHEMY, note:'Là chống nóng, không phải miễn nhiễm quá nhiệt.' });
  utility({ name:'Tĩnh Tâm', code:'utility_sanity_regen', effectKey:'utilitySanityRegen', value:'+0,5 tinh thần mỗi giây', source:SOURCE_ALCHEMY, note:'Thấp hơn nhiều so với Thanh Tâm Đan.' });
  utility({ name:'Học Giả', code:'utility_exp_gain', effectKey:'utilityExpGain', value:'+10% EXP ngoài Dungeon', source:SOURCE_DUNGEON, decision:'Cân nhắc', note:'Ảnh hưởng tốc độ progression. Không nên xuất hiện trong pool chiến đấu thông thường.' });

  return {
    rows,
    tiers: ['I', 'II', 'III', 'IV', 'V', 'UTILITY'],
    storageKey: 'pham-nhan-affix-balance:v1',
  };
});
