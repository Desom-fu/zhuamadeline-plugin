# 草莓果园等级配置
# if_use_berry: 1=使用草莓升级, 0=使用能量升级
GARDEN_LEVELS = {
    1: {
        "if_use_berry": 1,
        "upgrade_berry": 1,
        "upgrade_energy": 1,
        "seed_cost": 10,
        "steal_cost": 15,
        "fert_energy": 1200,
        "basic_reward": 15,
        "max_steal_times": 1,
        "max_be_stolen": 1,
        "steal_min": 1,
        "steal_max": 50
    },
    2: {
        "if_use_berry": 0,
        "upgrade_berry": 3000,
        "upgrade_energy": 20000,
        "seed_cost": 15,
        "steal_cost": 15,
        "fert_energy": 2000,
        "basic_reward": 20,
        "max_steal_times": 1,
        "max_be_stolen": 1,
        "steal_min": 2,
        "steal_max": 55
    },
    3: {
        "if_use_berry": 0,
        "upgrade_berry": 4500,
        "upgrade_energy": 30000,
        "seed_cost": 20,
        "steal_cost": 15,
        "fert_energy": 2500,
        "basic_reward": 25,
        "max_steal_times": 2,
        "max_be_stolen": 1,
        "steal_min": 5,
        "steal_max": 60
    }
}

# 获取等级配置的辅助函数
def get_level_config(level):
    return GARDEN_LEVELS.get(level, GARDEN_LEVELS[1])  # 默认返回1级配置