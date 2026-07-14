-- Vietnamese display-name patch for Tu Tien inventory items.
-- Apply with:
--   sqlite3 data/generated/wiki.sqlite < data/manual/update_vi_inventory_names.sql
--
-- Opaque skin suffixes are intentionally retained as stable variant codes when
-- the source mod does not expose a trustworthy human-readable name. This avoids
-- inventing translations while still giving every item a useful Vietnamese name.

.bail on
BEGIN IMMEDIATE;

CREATE TEMP TABLE vi_inventory_names (
    prefab_id TEXT PRIMARY KEY,
    name_vi TEXT NOT NULL CHECK (length(trim(name_vi)) > 0)
);

INSERT INTO vi_inventory_names (prefab_id, name_vi) VALUES
    ('gezhixing_amiaohouse', 'A Miêu Tiểu Ốc'),
    ('xd_backpack3_skin1', 'Bối Nang Tu Tiên · Ngoại Quan 1'),
    ('xd_backpack3_skin4', 'Bối Nang Tu Tiên · Ngoại Quan 4'),
    ('xd_backpack3_skin5', 'Bối Nang Tu Tiên · Ngoại Quan 5'),
    ('xd_backpack3_skin6', 'Bối Nang Tu Tiên · Ngoại Quan 6'),
    ('xd_crc_skins_hqyx', 'Trữ Nhục Thương · Ngoại Quan HQYX'),
    ('xd_dbg_skins_llt', 'Đa Bảo Các · Ngoại Quan LLT'),
    ('xd_dbg_skins_ybg', 'Đa Bảo Các · Ngoại Quan YBG'),
    ('xd_dc_skins_hh', 'Đăng Thải · Ngoại Quan HH'),
    ('xd_dy_tsfhd_1', 'Nhất Phẩm Thế Tử Phản Hồn Đan'),
    ('xd_dy_tsfhd_2', 'Nhị Phẩm Thế Tử Phản Hồn Đan'),
    ('xd_dy_tsfhd_3', 'Tam Phẩm Thế Tử Phản Hồn Đan'),
    ('xd_dy_tsfhd_4', 'Tứ Phẩm Thế Tử Phản Hồn Đan'),
    ('xd_dy_tsfhd_5', 'Ngũ Phẩm Thế Tử Phản Hồn Đan'),
    ('xd_flower_bmg_skins_srlg', 'Bạch Mân Côi · Ngoại Quan SRLG'),
    ('xd_flower_md_skins_rjfg', 'Mẫu Đơn · Ngoại Quan RJFG'),
    ('xd_flower_sfr_skins_fr', 'Thủy Phù Dung · Ngoại Quan FR'),
    ('xd_flower_sfr_skins_xy', 'Thủy Phù Dung · Ngoại Quan XY'),
    ('xd_ftys_skins_zjzy', 'Chuồng Dê Điện · Ngoại Quan ZJZY'),
    ('xd_gj_skins_lrq', 'Cam Tỉnh · Ngoại Quan LRQ'),
    ('xd_gjx_skins_jsth', 'Công Cụ Hạp · Ngoại Quan JSTH'),
    ('xd_hhlmz_skins_htjc', 'Hoàng Hoa Lê Mộc Trác · Ngoại Quan HTJC'),
    ('xd_hhlmz_skins_wfz', 'Hoàng Hoa Lê Mộc Trác · Ngoại Quan WFZ'),
    ('xd_hmsw_skins_bzxw', 'Hoán Miêu Thụ Ốc · Ngoại Quan BZXW'),
    ('xd_htz_spell', 'Hạo Thiên Tôn Pháp Thuật'),
    ('xd_hxyp_cd', 'Hộ Tâm Ngọc Bội · Hồi Phục'),
    ('xd_jwtcd_skins_hqy', 'Kim Ô Đằng Thải Đăng · Ngoại Quan HQY'),
    ('xd_jwtcd_skins_qzyc', 'Kim Ô Đằng Thải Đăng · Ngoại Quan QZYC'),
    ('xd_lbjlt_skins_zgrpt', 'Linh Bảo Tế Luyện Đài · Ngoại Quan ZGRPT'),
    ('xd_lgzbh_skins_jlyc', 'Lưu Quang Châu Bảo Hạp · Ngoại Quan JLYC'),
    ('xd_liandanlu_skins_ysx', 'Đan Lô · Ngoại Quan YSX'),
    ('xd_lyd_skins_fhgz', 'Liên Diệp Đông · Ngoại Quan FHGZ'),
    ('xd_mg_skins_qwg', 'Mật Quán · Ngoại Quan QWG'),
    ('xd_mglz_skins_hhyy', 'Giỏ Nấm · Ngoại Quan HHYY'),
    ('xd_mo_builder_skins_duanzui', 'Ma Kiếm · Đoạn Tội'),
    ('xd_mo_builder_skins_wendao', 'Ma Kiếm · Vấn Đạo'),
    ('xd_pflnw_skins_qns', 'Chuồng Bò Lai · Ngoại Quan QNS'),
    ('xd_qianyu_1', 'Tiêm Vũ · Nhất Thức'),
    ('xd_qianyu_2', 'Tiêm Vũ · Nhị Thức'),
    ('xd_qljq_skins_hlq', 'Quỳnh Lâu Kim Khuyết · Ngoại Quan HLQ'),
    ('xd_qwsk_xznw', 'Thiên Vị Thực Khám · Ngoại Quan XZNW'),
    ('xd_sgc_skins_wgc', 'Sơ Quả Thương · Ngoại Quan WGC'),
    ('xd_sj_by_skin1', 'Bích Vân Đồng Tử · Ngoại Quan 1'),
    ('xd_sj_cy_skin1', 'Thải Vân Đồng Tử · Ngoại Quan 1'),
    ('xd_skin_cgsh', 'Ngoại Quan Tu Tiên · CGSH'),
    ('xd_skin_clzgj', 'Ngoại Quan Tu Tiên · CLZGJ'),
    ('xd_skin_cxlt', 'Ngoại Quan Tu Tiên · CXLT'),
    ('xd_skin_cygh', 'Ngoại Quan Tu Tiên · CYGH'),
    ('xd_skin_fgy', 'Ngoại Quan Tu Tiên · FGY'),
    ('xd_skin_fhjd', 'Ngoại Quan Tu Tiên · FHJD'),
    ('xd_skin_flzr', 'Ngoại Quan Tu Tiên · FLZR'),
    ('xd_skin_fsfmg', 'Ngoại Quan Tu Tiên · FSFMG'),
    ('xd_skin_fshm', 'Ngoại Quan Tu Tiên · FSHM'),
    ('xd_skin_fyzz', 'Ngoại Quan Tu Tiên · FYZZ'),
    ('xd_skin_hasaki', 'Ngoại Quan Tu Tiên · Hasaki'),
    ('xd_skin_hyys', 'Ngoại Quan Tu Tiên · HYYS'),
    ('xd_skin_jj', 'Ngoại Quan Tu Tiên · JJ'),
    ('xd_skin_jj_skillbuild', 'Ngoại Quan Tu Tiên · JJ (Dạng Kỹ Năng)'),
    ('xd_skin_jydm', 'Ngoại Quan Tu Tiên · JYDM'),
    ('xd_skin_jypk', 'Ngoại Quan Tu Tiên · JYPK'),
    ('xd_skin_kt', 'Ngoại Quan Tu Tiên · KT'),
    ('xd_skin_kt_skillbuild', 'Ngoại Quan Tu Tiên · KT (Dạng Kỹ Năng)'),
    ('xd_skin_ly', 'Ngoại Quan Tu Tiên · LY'),
    ('xd_skin_lysy', 'Ngoại Quan Tu Tiên · LYSY'),
    ('xd_skin_mzhcd', 'Ngoại Quan Tu Tiên · MZHCD'),
    ('xd_skin_mzly', 'Ngoại Quan Tu Tiên · MZLY'),
    ('xd_skin_nczx', 'Ngoại Quan Tu Tiên · NCZX'),
    ('xd_skin_ny', 'Ngoại Quan Tu Tiên · NY'),
    ('xd_skin_nyhr', 'Ngoại Quan Tu Tiên · NYHR'),
    ('xd_skin_smy', 'Ngoại Quan Tu Tiên · SMY'),
    ('xd_skin_tf', 'Ngoại Quan Tu Tiên · TF'),
    ('xd_skin_wxj', 'Ngoại Quan Tu Tiên · WXJ'),
    ('xd_skin_wzsb', 'Ngoại Quan Tu Tiên · WZSB'),
    ('xd_skin_xgl', 'Ngoại Quan Tu Tiên · XGL'),
    ('xd_skin_xqc', 'Ngoại Quan Tu Tiên · XQC'),
    ('xd_skin_xuanyuan', 'Ngoại Quan Tu Tiên · Hiên Viên'),
    ('xd_skin_xyb', 'Ngoại Quan Tu Tiên · XYB'),
    ('xd_skin_yfcy', 'Ngoại Quan Tu Tiên · YFCY'),
    ('xd_skin_yfly', 'Ngoại Quan Tu Tiên · YFLY'),
    ('xd_skin_ylxh', 'Ngoại Quan Tu Tiên · YLXH'),
    ('xd_skin_ys', 'Ngoại Quan Tu Tiên · YS'),
    ('xd_skin_ysb', 'Ngoại Quan Tu Tiên · YSB'),
    ('xd_skin_ysb_skillbuild', 'Ngoại Quan Tu Tiên · YSB (Dạng Kỹ Năng)'),
    ('xd_skin_zste', 'Ngoại Quan Tu Tiên · ZSTE'),
    ('xd_skin_zsxm', 'Ngoại Quan Tu Tiên · ZSXM'),
    ('xd_skin_zw', 'Ngoại Quan Tu Tiên · ZW'),
    ('xd_skin_zw_skillbuild', 'Ngoại Quan Tu Tiên · ZW (Dạng Kỹ Năng)'),
    ('xd_skin_zyj', 'Ngoại Quan Tu Tiên · ZYJ'),
    ('xd_sudaji_redlantern_zyx', 'Ngư Long Đăng · Ngoại Quan ZYX'),
    ('xd_sudaji_sjpn_jssc', 'Thập Cẩm Bội Nang · Ngoại Quan JSSC'),
    ('xd_sudaji_tsmd_ykmd', 'Thế Thân Mộc Điêu · Ngoại Quan YKMD'),
    ('xd_sudaji_xyj', 'Tô Đát Kỷ · Phụ Kiện XYJ'),
    ('xd_sudaji_yhly_charged', 'Dưỡng Hồn Linh Ngọc · Đã Nạp'),
    ('xd_sudaji_yhly_yhm', 'Dưỡng Hồn Linh Ngọc · Ngoại Quan YHM'),
    ('xd_sudaji_yhly_yhm_charged', 'Dưỡng Hồn Linh Ngọc · Ngoại Quan YHM (Đã Nạp)'),
    ('xd_sudaji_ywfh_lxzy', 'Nhất Vũ Phương Hoa · Ngoại Quan LXZY'),
    ('xd_tianjiwu_skins_byj', 'Thiên Cơ Ốc · Ngoại Quan BYJ'),
    ('xd_tree_df_skins_zsyj', 'Đan Phong · Ngoại Quan ZSYJ'),
    ('xd_tree_xhs_skins_lgs', 'Hạnh Hoa Thụ · Ngoại Quan LGS'),
    ('xd_tree_yhs_skins_fd', 'Anh Đào Thụ · Ngoại Quan FD'),
    ('xd_tree_yxs_skins_jqs', 'Ngân Hạnh · Ngoại Quan JQS'),
    ('xd_wmz_md1', 'Mê Điệp · Nhất Giai'),
    ('xd_wmz_md2', 'Mê Điệp · Nhị Giai'),
    ('xd_wmz_md3', 'Mê Điệp · Tam Giai'),
    ('xd_wmz_md4', 'Mê Điệp · Tứ Giai'),
    ('xd_wmz_md5', 'Mê Điệp · Ngũ Giai'),
    ('xd_wmz_md6', 'Mê Điệp · Lục Giai'),
    ('xd_wmz_md7', 'Mê Điệp · Thất Giai'),
    ('xd_wmz_md8', 'Mê Điệp · Bát Giai'),
    ('xd_wmz_spell', 'Vương Ma Tử Pháp Thuật'),
    ('xd_wsjx_skins_yzjx', 'Vô Song Kiếm Hạp · Ngoại Quan YZJX'),
    ('xd_xcdf_skins_sysx', 'Tinh Thối Đan Phủ · Ngoại Quan SYSX'),
    ('xd_xianjian_builder_skins_duanzui', 'Tiên Kiếm · Đoạn Tội'),
    ('xd_xianjian_builder_skins_wendao', 'Tiên Kiếm · Vấn Đạo'),
    ('xd_xshj_bbzy', 'Tà Sát Hộ Giáp · Ngoại Quan BBZY'),
    ('xd_xshj_fhlh', 'Tà Sát Hộ Giáp · Ngoại Quan FHLH'),
    ('xd_xtbh_skins_wxxxh', 'Huyền Thiên Bảo Hồ · Ngoại Quan WXXXH'),
    ('xd_yaoarmor', 'Yêu Linh Chiến Giáp'),
    ('xd_yaohat', 'Yêu Linh Pháp Quan'),
    ('xd_yhbs_zmyh', 'Dưỡng Hồn Chủy Thủ · Ngoại Quan ZMYH'),
    ('xd_yhsyz_skins_qlyyz', 'Nguyệt Hoa Nhiếp Dược Chi · Ngoại Quan QLYYZ'),
    ('xd_ylxc_skins_qhnlc', 'Ngọc Lộ Huyền Thương · Ngoại Quan QHNLC'),
    ('xd_ylxq_skins_fynl', 'Ngọc Lộ Tiên Khu · Ngoại Quan FYNL'),
    ('xd_yunxiao_portableslot', 'Vân Tiêu Tùy Thân Trữ Vị'),
    ('xd_zcmj_jhxs', 'Tử Xá Diện Giáp · Ngoại Quan JHXS'),
    ('xd_zcmj_trxz', 'Tử Xá Diện Giáp · Ngoại Quan TRXZ'),
    ('xd_ztp_skins_lmxq', 'Chưởng Thiên Bình · Ngoại Quan LMXQ');

-- Fail atomically if the patch is incomplete or no longer matches the database.
CREATE TEMP TABLE patch_count_guard (
    expected_count INTEGER NOT NULL CHECK (expected_count = 127),
    matched_count INTEGER NOT NULL CHECK (matched_count = 127)
);

INSERT INTO patch_count_guard (expected_count, matched_count)
SELECT
    (SELECT count(*) FROM vi_inventory_names),
    count(*)
FROM entities AS e
JOIN vi_inventory_names AS p ON p.prefab_id = e.prefab_id
WHERE e.namespace = 'tu_tien'
  AND e.is_inventory_item = 1;

UPDATE entities
SET name_vi = (
    SELECT p.name_vi
    FROM vi_inventory_names AS p
    WHERE p.prefab_id = entities.prefab_id
)
WHERE namespace = 'tu_tien'
  AND prefab_id IN (SELECT prefab_id FROM vi_inventory_names);

-- Safe terminology normalization for display names only. Prose and character
-- quotes retain their original casing and voice.
UPDATE entities
SET name_vi = replace(
                  replace(
                      replace(
                          replace(
                              replace(
                                  replace(
                                      replace(
                                          replace(
                                              replace(
                                                  replace(
                                                      replace(name_vi, 'linh thạch', 'Linh Thạch'),
                                                      'Linh thạch', 'Linh Thạch'),
                                                  'pháp bảo', 'Pháp Bảo'),
                                              'Pháp bảo', 'Pháp Bảo'),
                                          'hạ phẩm', 'Hạ Phẩm'),
                                      'Hạ phẩm', 'Hạ Phẩm'),
                                  'trung phẩm', 'Trung Phẩm'),
                              'Trung phẩm', 'Trung Phẩm'),
                          'thượng phẩm', 'Thượng Phẩm'),
                      'Thượng phẩm', 'Thượng Phẩm'),
                  'cực phẩm', 'Cực Phẩm')
WHERE namespace = 'tu_tien'
  AND name_vi IS NOT NULL;

-- Clear translation corrections in explanatory prose. Character quotes live in
-- effects and are deliberately not touched.
UPDATE entities
SET description_vi = replace(
                         replace(
                             replace(
                                 replace(
                                     replace(
                                         replace(description_vi,
                                             'phú dư', 'ban cho'),
                                         'Phú dư', 'Ban cho'),
                                     'cụ bị', 'mang'),
                                 'một lượng tỷ lệ thành công', 'tỷ lệ thành công'),
                             'khi công địch sẽ phản bổ lại bản thân',
                             'khi tấn công kẻ địch sẽ bồi bổ lại bản thân'),
                         'Lôi Minh Cố', 'Lôi Minh Cô')
WHERE namespace = 'tu_tien'
  AND description_vi IS NOT NULL;

COMMIT;

SELECT 'patched_inventory_names' AS metric, count(*) AS value
FROM entities AS e
JOIN vi_inventory_names AS p ON p.prefab_id = e.prefab_id
WHERE e.namespace = 'tu_tien'
  AND e.name_vi = p.name_vi;

SELECT 'remaining_missing_inventory_names' AS metric, count(*) AS value
FROM entities
WHERE namespace = 'tu_tien'
  AND is_inventory_item = 1
  AND (name_vi IS NULL OR trim(name_vi) = '');
