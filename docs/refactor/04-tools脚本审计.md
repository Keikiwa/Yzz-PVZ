# 04 · `tools/` 85 个脚本审计

> 结论先行：**`tools/` 不是工具，是"补丁历史"的化石层。** 85 个脚本里 36 个是"字符串替换器"，它们串成一条一次性、不可重放的补丁链；12 个是资产生成器；17 个是测试；16 个是文档/启动器/推送生成器；4 个是一次性侦察脚本。
> 本文件回答"它们到底做了什么"，并给出**归档策略**（保留哪些、删除哪些、如何一次性迁移）。

---

## 1. 分类统计

| 类别 | 数量 | 是否属于"构建系统" |
|---|---:|---|
| (a) 源码改造器（改写 `pvz_ten_levels.py` / `pvz_graphics.py`） | **36** | ❌ 一次性历史产物 |
| (b) 资产生成/安装（下载 GIF、PIL 抠图、合成卡牌） | 12 | ⚠️ 半可复用 |
| (c) 测试/验证/性能 | 17 | ⚠️ 有价值但路径已失效 |
| (d) 文档 / `.bat` / git 推送生成器 | 16 | ❌ 一次性 |
| (e) 一次性侦察 | 4 | ❌ |
| 合计 | **85** | |

**全部 85 个文件**都在同一次首发提交（`11c4986`）或后续 4 次修复提交中入库；没有任何 `__init__.py`、没有 CI、没有 pinned runner。仓库根只有 `pygame>=2.6.1` 一个依赖。

---

## 2. (a) 源码改造器 —— 36 个，是最大的问题

它们的工作方式统一为：**读整份源码 → `content.replace(old_block, new_block)` → 写回**。

### 2.1 三代"整段重写"脚本（最危险）

| 脚本 | 做什么 | 锚定方式 | 现在再跑会怎样 |
|---|---|---|---|
| `apply_updates.py` | 重写整个 `PLANTS = {`…`LEVELS = [` 区间，以及整个 `Plant`…`Game` 类区间 | `re.compile(r'PLANTS = \{.*?LEVELS = \[.*?\]\n', re.DOTALL)` + `re.sub` | **灾难**：正则今天仍然匹配，会把手上的 23 植物/9 僵尸/16 关快照写回去，抹掉 v3–v6 全部工作 |
| `update_full_gameplay.py`（72 KB，最大） | 15 个编号段，替换 `Game.__init__`、`start_level`、`_build_waves`、`_spawn_wave_member`、`_update_plants`、`_update_zombies`、`_draw_menu`、`_draw_seed_select`、`setup_preview` 等 | 8 处 `.replace` + 7 处 `re.sub(r'def X\(...\).*?def Y', DOTALL)` | **灾难**：`def _update_plants…def _update_zombies` 的正则仍匹配 → 删掉全部 34 植物战斗逻辑 |
| `apply_v4_perfect_unlock_and_fonts.py` | 重写 `text()`、`UNLOCK_ORDER`、`LEVEL_REWARDS`、`available_plants`、选卡目录网格 | `re.sub` 无守卫 | **回退**：`UNLOCK_ORDER` 会从 34 项退回 33 项；`text()` 会退回无 `_TEXT_CACHE` 版本 |

这三个的共同特征：**正则 `.*?` 跨越整个函数体**，所以它们"永远匹配成功"，也永远会破坏当前代码。

### 2.2 断言型补丁（再跑即崩）

`apply_patch_v3.py`（12 个 `assert`）、`apply_hypno_and_perf_fixes.py`、`patch_visuals_autosun.py`、`patch_modest_game_text.py`（6 个 assert）、`patch_cattail_spike.py`（5 个 assert）、`update_graphics_sizes.py`、`update_overlays.py`、`patch_pvz_graphics.py`（4 个中 3 个已失效）。

**行为**：`assert old in text` 先失败 → 抛 `AssertionError` → **不写文件**。这类"再跑就崩"其实是最安全的失败方式，但代价是**完全无法表达"这次改动已经应用"**，所以每次都只能新写一个脚本。

### 2.3 静默型补丁（再跑即重复插入）

`add_flag_zombie.py`、`patch_start_level.py`、`patch_click.py`、`patch_balloon_and_digger.py`、`patch_zombie_skills.py`、`patch_pvz_graphics_hypno.py`、`patch_cobcannon_graphics.py`、`update_graphics.py`、`fix_art.py`、`apply_v5_expansion_all.py`、`apply_v5_expansion_perfect.py`。

**根因**：守卫写成 `if old in code: code = code.replace(old, new)`，而 **`old` 是 `new` 的前缀** → 守卫永远为真 → 每次运行都再插一遍。

已能在当前文件中看到的后果：
- `zombie` 定义区 `"flag"` 键出现两次（290 行附近，来自 `add_flag_zombie.py`）
- `artifacts` 的 `.union(getattr(self,"artifacts",set()))` 出现两次（1572、1658，来自 `fix_art.py`）
- `cannon_ready/agave_state/laser_timer` 若重跑会再插一遍 dataclass 字段

### 2.4 非上下文型改造器（最不可控）

| 脚本 | 机制 | 风险 |
|---|---|---|
| `fix_indent.py` | 按**硬编码行号** `if (i < 3750 or i > 3800)` 遍历全文，用 `startswith('            else:')` 之类改缩进，然后无条件写回 | 文件已 4436 行、目标区已漂移 → **会打烂全文件缩进** |
| `auto_fix_syntax.py` | 循环 50 次：`py_compile` → 从报错里正则抠 `line (\d+)` → 把该行缩进 ±4 空格 → 写回 | 若代码本身能编译则 no-op；否则**是"猜着改"** |

### 2.5 补丁链（关键证据：后一个补丁的 `old` 里嵌着前一个补丁的 `new`）

```
apply_updates ──> apply_game_updates ──> update_full_gameplay
      └─> apply_rewards_and_new_plants ──> apply_patch_v3 ──> apply_user_fixes
            └─> apply_perfect_pool_grid ──> apply_v4_perfect_unlock_and_fonts
                  └─> apply_v5_expansion_all ──> apply_v5_expansion_perfect
                        └─> update_graphics* / update_overlays / patch_*
                              └─> apply_warp_and_fix_topright ──> apply_v6_part2_game
                                    └─> apply_v6_full_fix ──> patch_v6_upgrades
                                          └─> patch_start_level / patch_visuals_autosun
                                                └─> patch_cattail_spike
```

硬依赖实例（可验证）：
1. `apply_v5_expansion_all.py:53-90` 的 `old_unlock_order` **逐字复现了** v4 的列表（连 `"threepeater"` 那行都在）。
2. `apply_warp_and_fix_topright.py:24` 产出 `topright_panel_rect=(915,10,275,80)`；`apply_v6_part2_game.py:32` 的 `old_hud_rects` **就是这一行**。
3. `patch_cattail_spike.py:24-26` 的 `old_proj_update` **嵌入了** `apply_v6_full_fix.py:109` 新增的三行 `if self.target_zombie ... target_x`。
4. `apply_hypno_and_perf_fixes.py:55` 的锚点是 `apply_v4` 产出的 `text()` 函数体。

→ **这条链只在一个特定的文件状态下成立。一次性、线性、不可重放、不可并行。** 这就是为什么"每加一个功能就要新写一个 `apply_xxx.py`"，也正是 `Game` 里出现"三张互相冗余的泳池常量表"的原因（`apply_perfect_pool_grid` 加两张，`apply_v6_part2_game` 又加一张）。

### 2.6 具体脆弱性示例（静默成功）

```python
# tools/apply_v6_full_fix.py:115-160 的 old_kernel_fire
old_kernel_fire = '''
                        is_butter = random.random() < 0.25
                        dmg = 40.0 if is_butter else 20.0
                        ... Projectile(..., apex_h=110.0,) ...
'''
code = code.replace(old_kernel_fire, new_kernel_fire)   # 无 if / 无 assert / 无日志
open(TARGET,'w').write(code)                              # 永远写回
```
只要有人把 `0.25` 调成 `0.30`（数值平衡），这段替换就**静默不生效**，而脚本仍打印成功并写回文件。

---

## 3. (b) 资产生成/安装 —— 12 个

| 脚本 | 输入 → 输出 |
|---|---|
| `install_all_authentic_plant_sprites.py` | 网络 GIF → `assets/plants/<key>/idle_N.png`（**先删旧 png**） |
| `extract_clean_frames.py` / `clean_plants_advanced.py` / `refine_cabbage.py` | GIF 帧 → 绿幕填充 + 紧裁 → 5 个投手目录 |
| `create_new_plants.py` / `create_v5_expansion_plants.py` | 用 PIL 画占位贴图 + 卡牌 |
| `install_magicshroom_and_agave.py` | 本地 PIL 合成 |
| `download_authentic_cards.py` / `download_sheet.py` / `fetch_wiki_assets.py` | 抓图/抓链接（`fetch_wiki_assets` 只打印不下载） |
| `replace_authentic_cards.py` / `fix_authentic_cards_with_sun.py` / `extract_sun_icon.py` | 合成卡牌 + 阳光徽章 |

**问题**：全部依赖 `download_cache/`（已被 `.gitignore` 排除且不存在）或网络；命名有 `idle_%d.png` 与 `frame_%02d.png` 两套；全部**无条件写 assets**。
**价值**：这是唯一"可复用"的一类，但目前不可重放（缺输入）。

---

## 4. (c) 测试 —— 17 个，事实上的"公共 API 冻结层"

这是重构时**唯一必须认真对待的既有契约**。

### 4.1 它们 import 哪些模块级名字

`PLANTS`、`ZOMBIES`、`LEVELS`、`LEVEL_REWARDS`、`UNLOCK_ORDER`、`SAVE_FILE`、`WIDTH/HEIGHT/GRID_X/GRID_Y/CELL_W`、`cell_center()`、`lane_ground()`、`text()`、`Game`、`Plant`、`Zombie`、`Projectile`、`SunToken`。

### 4.2 它们访问哪些 `Game` 家族成员

| 表面 | 使用方 |
|---|---|
| `start_level / level_index / mode / sun / is_pool / rows / cell_h / pool_rows / grid_bottom` | 大部分测试 |
| `plants / zombies / projectiles / suns / waves / artifacts / cooldowns / selected_seeds / selected_plant / shovel_selected / slot_capacity / available_plants()` | 全部 |
| **私有**：`_update_plants / _update_zombies / _update_projectiles / _damage_zombie / _remove_dead / _build_waves / _select_plant / _handle_click / _handle_key / _top_plant_at / _carrier_at / _draw_menu` | v3 / v6 / cattail / pool / warp |
| v6 新增：`canvas / is_fullscreen / scale / offset_x / offset_y / get_logical_mouse_pos() / get_cell_rect() / auto_sun_unlocked / auto_sun_enabled` | `test_v6_full_verification` |
| HUD 命中框：`topright_panel_rect / speed_rect / pause_rect / shovel_rect / audio_rect / skip_rect / warp_buttons` | `test_warp_and_topright` |
| 渲染：`draw() / update() / setup_preview() / time_value / banner_timer / wave_flash / overlay / overlay_age` | 截图生成器 |

### 4.3 已经坏了的测试（与重构无关的既有问题）

| 测试 | 失效原因 |
|---|---|
| `test_v4_unlock_and_clean.py` | 断言 `UNLOCK_ORDER[2:7] == [...5 项]`，v6 插入了 `threepeater` → 断言今天的代码就不过 |
| `test_in_game_fumeshroom_and_cards.py` | `Game()` 少传 `screen` → `TypeError` |
| `test_v6_full_verification.py`、`test_cattail_spike_fix.py`、`test_pool_planting_and_cards.py` | 用 `Path("10-pvz")` 找源码 → 目录不存在 |
| 另外 7 个 | 硬编码 `F:\Desktop\...` sys.path |
| `full_game_self_test.py`、`verify_features.py` | 会写真实 `SAVE_FILE`（测试污染存档） |

**统计**：11/17 有不可解析的路径；1/17 断言过时；1/17 少参数。**没有 CI 所以没人发现。**

### 4.4 结论

`tools/` 的测试层是**唯一值得抢救的部分**。它们揭示了真实的公开 API 形状（虽然大量依赖私有方法），可以作为重构后的回归基线——但必须先修路径与断言。

---

## 5. (d) 文档 / .bat / git 生成器 —— 16 个

| 类型 | 文件 | 问题 |
|---|---|---|
| Markdown 交付文档（5 个写同一文件名） | `write_doc.py`、`write_final_doc.py`、`write_final_doc_utf8bom.py`、`write_v5_doc.py`、`finalize_delivery.py` | 后写覆盖前写；全部输出到 `F:\Desktop\.DeskBox\...\文档\`（不存在）；约定 UTF-8+BOM |
| V6 报告（2 个） | `update_delivery_files.py`、`update_doc_cattail.py` | 后者有真正的内容守卫，是 85 个里唯一幂等的文档生成器 |
| 品牌改名 | `update_modest_branding.py` | 写完新名还 `os.remove` 旧名 |
| 截图生成 | `generate_deliverables.py`、`generate_warp_deliverables.py` | `Game(screen, headless=True)` 后 `draw()` 存 PNG |
| `.bat` 生成（7 处） | `create_bat.py` 等 | 两个文件名并存（`运行…` / `启动…`），全部 GBK+CRLF |
| 合规检查 | `verify_delivery_compliance.py` | 检查 BOM/CRLF/`@chcp 936` + `py_compile`，但路径全失效 |
| **git 推送** | `push_to_github.py` | `git init -b main` → `git remote set-url` → `git add .` → **固定 commit message** → **`git push -u origin main --force`**；硬编码 `F:\开发工具\Git\cmd\git.exe` 与旧仓库路径 |
| 字符审计 | `check_chars.py` | 只读，扫 `text()` 字面量里的非中文字形（唯一无害且仍可用的脚本之一） |

> `push_to_github.py` 的 `--force` + 固定 message + 绝对路径，意味着**任何一次误运行都会强推并覆盖远端历史**。建议立即从仓库移除或改为需要显式 `--yes` 保护。

---

## 6. 归档建议

### 6.1 立即删除（不可复用且有害）

```
apply_updates.py              # 正则整段回写，再跑即灾难
update_full_gameplay.py       # 同上，72KB
apply_v4_perfect_unlock_and_fonts.py
fix_indent.py                 # 硬编码行号改缩进
auto_fix_syntax.py            # 猜着改缩进
push_to_github.py             # --force 强推
```
以及其余 30 个 `apply_*/patch_*/update_*/clean_*/refine_*/add_*/fix_art.py`（全部已被应用，留着只会被误跑）。

### 6.2 移到 `tools/legacy/` 并加 `README.md` 说明"仅存档，禁止运行"

其余改造器 + 全部文档生成器 + 全部 `.bat` 生成器。目的：保留"当时怎么改的"这一历史信息，同时让误运行的概率趋零（可选加保护：文件头 `raise SystemExit("legacy: do not run")`）。

### 6.3 迁移进新仓库（清理后保留）

| 目标 | 内容 |
|---|---|
| `tests/` | 从 17 个测试里挑出仍有效的，改为 `pytest` + 相对路径 + 不写真实存档（用 `tmp_path`）。至少要保留：`test_v3_plants`(僵尸/水路)、`test_pool_planting_and_cards`(泳池种植)、`test_hypno_battle_and_performance`(魅惑互啃)、`test_cattail_spike_fix`(追踪弹)、`verify_features`(神器效果) |
| `tools/assets/` | 12 个资产生成器，并补一个 `download_cache/README.md` 说明所需输入 |
| `scripts/` | 一个真正幂等的 `bootstrap.bat` 生成器（替代 7 份 `.bat` 写入代码） |
| `docs/交付/` | 把 5 个 Markdown 生成器的**输出**存一份静态文档；删除生成器 |

### 6.4 关键动作：把"补丁链"替换为"版本控制"

现状是：改代码 = 写一个新 `apply_*.py` 然后跑它。
应当改为：**直接改源码 + git commit**。`tools/` 作为补丁引擎的存在，本质上是"没有用好 git diff"的产物。补丁脚本相对于直接编辑**没有任何优势**（它不能 review、不能 rebase、不能部分回滚、不能多人并行），却引入了 36 份不可重放的隐式历史。

---

## 7. 从 `tools/` 得到的重构硬约束

1. **不能保留任何"字符串替换"式迁移工具。** 重构必须走"一次大搬迁 + 回归测试"，而不是继续叠加 `apply_refactor.py`。
2. **`tools/` 里的 17 个测试是唯一可靠的既有契约**，重构过程中必须让它们（修好之后）全绿。
3. **必须补一个启动期一致性自检**，把 `tools/` 时代遗留的"命名靠约定"（`ZOMBIES` 顺序 == `LEVELS.mix` 位置、`ptype` == 资源目录名、`theme` == 地图文件名）变成显式断言——否则下一次改动仍会静默错位。
4. **`push_to_github.py` 应当立即删除**：它是唯一能把错误放大到远端历史的脚本。
