# EVA experimental game-test installation — 2026-09-22

Installed the seven files listed in `staged/package-manifest.json` into both:

- `C:/Users/NYX/company/dst_wiki/mods/PhamNhanTuTien`
- `C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/mods/PhamNhanTuTien`

All seven destination SHA-256 values were verified against the staged manifest after each copy. EVA archive SHA-256 is `9cae351ef02f17af4112d074fdddcd512b8dfa503f60ca8276545f949c3a14d8`.

`pre-install-backup` contains the previous three existing files, whose hashes were checked against both targets before copying. The other four files were absent before installation: `anim/ttk_eva_run_loop.zip` and the three `scripts/util/eva_*` modules in the manifest. No other runtime files or mods were copied. Restoring the three originals and removing only these four additions restores this runtime installation's baseline.

Restart the game before testing. Accepted hair is frozen. This is not final concept-fidelity acceptance: profile/rear running and other actions retain native matrices and visible attachment seams remain. The guarded front-run adapter still requires actual engine/multiplayer verification. Its unsupported diagnostic is `[EVA run route] EVA run retarget unavailable; native motion may mismatch`; native fallback is not a visual-fidelity guarantee.

Workspace-only source metadata `assets/source/eva_approved/rig-map.json` was also updated to the accurate Task2c v1 manifest (`b26e4f8df83a36775cd7709e053e6cc5b91e212c1837ac13bda0c7ea2ff8834a`). Its previous version is backed up as `pre-install-backup/rig-map.json`. This developer metadata is not required in Steam. Fresh installed-default tests: approved rig 6/6 and repack 2/2 pass.
