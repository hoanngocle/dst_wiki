# Phàm Nhân Tu Tiên — Lam Phượng Luyện Khí Đài UI

Replaced the old narrow strengthening panel with the approved horizontal silver/blue layout, reusing the installed forge frame and controls with native tinting. Uses bundled Noto Serif Medium throughout. Native equipment slot retains drag/drop; enhancement stones are consumed directly from inventory as before.

The panel shows current/next level, damage or armor absorption, passive count, success probability, available/required stones and failure consequences. Protection/magic charm state comes from the server. Empty, missing-stone, pending, stale-item and maximum-level states disable the action. Unenhanced items now receive the preview before the first action, including their base stats. Probability display is capped at 100% when luck bonuses exceed it.

Added server snapshot revision and network item identity. Strengthening validates the open station, its slot, distance and supplied revision; a duplicate request cannot reuse the revision. Older RPC callers without a revision retain compatibility but must satisfy station access checks. Costs, success/failure rules, charm effects and save/prefab IDs are unchanged. Updated the original strengthening smoke fixture to open the container and insert its equipment before calling the handler.

Verification: widget state tests, existing strengthening mechanics tests and Thần Binh Phổ widget regression checks pass. Dedicated server smoke covers first-level preview, costs, duplicate request rejection, maximum level, failure tiers, both charms and legacy save migration; evidence is `mods/solo-assets-work/lam-phuong/ui-smoke.log`.

Previews in `artifacts/lam-phuong-ui/` render the actual Lua widget, installed bitmap font and textures with illustrative item/stat data. Checked normal, protected, empty and maximum-level layouts. These are not game-client screenshots; live client visual/input QA remains unperformed.
