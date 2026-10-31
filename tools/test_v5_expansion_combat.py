# -*- coding: utf-8 -*-
"""Comprehensive combat verification for 4 new expansion plants and 5 new elite zombies:
Plants:
- cobcannon (玉米加农炮)
- magicshroom (魔术菇)
- agave (龙舌兰)
- laserbean (激光豆)
Zombies:
- gargantuar (巨人僵尸)
- imp (小鬼僵尸)
- balloon (气球僵尸)
- jackbox (小丑僵尸)
- digger (矿工僵尸)
"""

import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
screen = pygame.display.set_mode((1200, 760))

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pvz_ten_levels as pvz

def test_expansion_combat():
    print("=== 开始测试 V5 扩展新植物与精英僵尸核心战斗机制 ===")
    game = pvz.Game(screen, headless=True)
    game.start_level(15) # 无尽关卡环境
    game.mode = "playing"

    # --- 1. 测试玉米加农炮 (Cob Cannon) 核弹轰炸 ---
    print("\n--- 1. 测试玉米加农炮核弹轰炸 ---")
    cannon = pvz.Plant("cobcannon", col=0, row=2, hp=1200, max_hp=1200, cell_h=game.cell_h)
    game.plants.append(cannon)
    # 放置 3 只铁桶僵尸在 row 2, x=500, 520, 540
    z1 = pvz.Zombie("bucket", row=2, x=500, hp=470, max_hp=470, speed=15.0, damage=34, cell_h=game.cell_h)
    z2 = pvz.Zombie("bucket", row=2, x=530, hp=470, max_hp=470, speed=15.0, damage=34, cell_h=game.cell_h)
    game.zombies = [z1, z2]
    # 更新让加农炮锁定发射
    game.update(0.1)
    # 检查生成了 cob_missile
    cobs = [p for p in game.projectiles if p.bullet_type == "cob_missile"]
    assert len(cobs) > 0, "玉米加农炮未能发射玉米核弹！"
    missile = cobs[0]
    print(f"玉米核弹已升空，目标: ({missile.target_x}, {missile.target_y})")
    # 推进直到核弹爆炸
    for _ in range(30):
        game.update(0.05)
    # 检查铁桶僵尸被 1800 毁灭伤害瞬秒
    assert z1.dead or z1.hp <= 0, "铁桶僵尸 1 未被加农炮核弹秒杀"
    assert z2.dead or z2.hp <= 0, "铁桶僵尸 2 未被加农炮核弹秒杀"
    print("玉米加农炮高爆范围核弹轰杀验证通过！(PASS)")

    # --- 2. 测试魔术菇 (Magic-shroom) 扑克牌与魔术奇迹 ---
    print("\n--- 2. 测试魔术菇扑克牌机制 ---")
    game.plants.clear()
    game.zombies.clear()
    game.projectiles.clear()
    magic = pvz.Plant("magicshroom", col=1, row=1, hp=300, max_hp=300, cell_h=game.cell_h)
    magic.action_timer = 2.0
    game.plants.append(magic)
    z_target = pvz.Zombie("cone", row=1, x=500, hp=290, max_hp=290, speed=17.0, damage=30, cell_h=game.cell_h)
    game.zombies.append(z_target)
    # 更新发射扑克牌
    game.update(0.1)
    cards = [p for p in game.projectiles if p.bullet_type == "magic_card"]
    assert len(cards) > 0, "魔术菇未能发射魔术扑克牌"
    print(f"魔术扑克牌飞出，花色: {cards[0].suit}")
    # 让扑克牌飞抵并命中僵尸
    cards[0].x = z_target.x - 5
    game.update(0.05)
    assert z_target.hp < 290, f"魔术扑克牌未能伤害僵尸: {z_target.hp}"
    print("魔术菇飞牌与奇迹伤害验证通过！(PASS)")

    # --- 3. 测试龙舌兰 (Agave) 蓄力剑斩与绝杀 ---
    print("\n--- 3. 测试龙舌兰蓄力剑斩 ---")
    game.plants.clear()
    game.zombies.clear()
    game.projectiles.clear()
    agave = pvz.Plant("agave", col=2, row=3, hp=600, max_hp=600, cell_h=game.cell_h)
    game.plants.append(agave)
    z_agave = pvz.Zombie("cone", row=3, x=agave.x + 80, hp=290, max_hp=290, speed=15.0, damage=30, cell_h=game.cell_h)
    game.zombies.append(z_agave)
    # 蓄力达到 0.8s
    agave.agave_timer = 0.75
    game.update(0.1)
    assert z_agave.hp <= 140.0, f"龙舌兰未施展双段剑斩: {z_agave.hp}"
    # 残血直接绝杀测试
    z_agave.hp = 80.0
    agave.agave_timer = 0.75
    game.update(0.1)
    assert z_agave.dead or z_agave.hp <= 0, "龙舌兰残血绝杀失败"
    print("龙舌兰近战蓄力剑斩与绝杀验证通过！(PASS)")

    # --- 4. 测试激光豆 (Laser Bean) 整行穿透 ---
    print("\n--- 4. 测试激光豆整行激光穿透 ---")
    game.plants.clear()
    game.zombies.clear()
    game.projectiles.clear()
    laser = pvz.Plant("laserbean", col=0, row=0, hp=300, max_hp=300, cell_h=game.cell_h)
    game.plants.append(laser)
    z_l1 = pvz.Zombie("basic", row=0, x=350, hp=170, max_hp=170, speed=18.0, damage=28, cell_h=game.cell_h)
    z_l2 = pvz.Zombie("basic", row=0, x=650, hp=170, max_hp=170, speed=18.0, damage=28, cell_h=game.cell_h)
    game.zombies = [z_l1, z_l2]
    laser.laser_timer = 1.55
    game.update(0.1)
    assert z_l1.hp < 170 and z_l2.hp < 170, f"激光未能同时贯通全行僵尸: z1={z_l1.hp}, z2={z_l2.hp}"
    print("激光豆全屏整行高能激光贯通验证通过！(PASS)")

    # --- 5. 测试巨人僵尸 (Gargantuar) 一锤秒杀与半血投掷小鬼 ---
    print("\n--- 5. 测试巨人僵尸巨锤重砸与抛掷小鬼 ---")
    game.plants.clear()
    game.zombies.clear()
    nut = pvz.Plant("wallnut", col=3, row=2, hp=1500, max_hp=1500, cell_h=game.cell_h)
    game.plants.append(nut)
    garg = pvz.Zombie("gargantuar", row=2, x=nut.x + 25, hp=3000, max_hp=3000, speed=11.0, damage=1500, cell_h=game.cell_h)
    game.zombies.append(garg)
    # 巨人重砸坚果墙
    game.update(1.1)
    assert not nut.alive or nut.hp <= 0, f"巨人巨锤未能一锤粉碎植物: {nut.hp}"
    # 模拟巨人生命值低于 1500
    garg.hp = 1400
    game.update(0.1)
    assert not garg.has_imp, "巨人未抛出背上的小鬼"
    imps = [z for z in game.zombies if z.ztype == "imp"]
    assert len(imps) > 0, "小鬼僵尸未能在草坪腹地成功生成！"
    print("巨人重击粉碎与抛掷小鬼机制验证通过！(PASS)")

    # --- 6. 测试气球僵尸 (Balloon Zombie) 浮空与击破 ---
    print("\n--- 6. 测试气球僵尸浮空与防空击破 ---")
    game.plants.clear()
    game.zombies.clear()
    game.projectiles.clear()
    balloon = pvz.Zombie("balloon", row=1, x=600, hp=140, max_hp=140, speed=17.0, damage=28, cell_h=game.cell_h)
    game.zombies.append(balloon)
    # 发射普通地面豌豆
    pea = pvz.Projectile(595, pvz.lane_ground(1, cell_h=game.cell_h) - 40, row=1, damage=20, bullet_type="pea")
    game.projectiles.append(pea)
    game.update(0.05)
    # 气球僵尸应避开地面直线豌豆
    assert balloon.hp == 140, "普通地面豌豆不应击中浮空气球僵尸！"
    # 发射卷心菜高抛弹
    cabbage = pvz.Projectile(595, pvz.lane_ground(1, cell_h=game.cell_h) - 40, row=1, damage=40, bullet_type="cabbage")
    game.projectiles.append(cabbage)
    game.update(0.05)
    assert not balloon.flying, "高抛投掷弹未能击破气球！"
    print("气球僵尸浮空避让与防空击破落地验证通过！(PASS)")

    # --- 7. 测试玩偶匣小丑僵尸 (Jack-in-the-box) 八音盒自爆 ---
    print("\n--- 7. 测试小丑八音盒自爆 ---")
    game.plants.clear()
    game.zombies.clear()
    p_near = pvz.Plant("peashooter", col=2, row=2, hp=300, max_hp=300, cell_h=game.cell_h)
    game.plants.append(p_near)
    jack = pvz.Zombie("jackbox", row=2, x=p_near.x + 20, hp=240, max_hp=240, speed=28.0, damage=30, cell_h=game.cell_h)
    jack.jackbox_timer = 0.05
    game.zombies.append(jack)
    game.update(0.1)
    assert jack.dead or jack.hp <= 0, "小丑八音盒未自爆死亡"
    assert not p_near.alive, "小丑八音盒自爆未摧毁附近植物"
    print("小丑八音盒倒计时范围自爆验证通过！(PASS)")

    # --- 8. 测试矿工僵尸 (Digger Zombie) 遁地潜行破土 ---
    print("\n--- 8. 测试矿工僵尸遁地潜行 ---")
    game.plants.clear()
    game.zombies.clear()
    digger = pvz.Zombie("digger", row=1, x=600, hp=220, max_hp=220, speed=22.0, damage=30, cell_h=game.cell_h)
    game.zombies.append(digger)
    # 处于潜行中发射子弹
    digger.digging = True
    pea = pvz.Projectile(595, pvz.lane_ground(1, cell_h=game.cell_h) - 40, row=1, damage=20, bullet_type="pea")
    game.projectiles.append(pea)
    game.update(0.05)
    assert digger.hp == 220, "矿工潜行中应免疫地面子弹！"
    # 让矿工潜行到最左侧破土
    digger.x = pvz.GRID_X + 15
    game.update(0.05)
    assert digger.emerged and not digger.digging, "矿工到达最左侧未成功破土而出！"
    assert digger.speed < 0, "矿工破土后未掉头反向向右啃咬！"
    print("矿工遁地潜行与后方反向突袭验证通过！(PASS)")

    print("\n=== 全部 4 种新植物与 5 种精英僵尸核心机制 100% 验证通过！ ===")

if __name__ == "__main__":
    test_expansion_combat()
