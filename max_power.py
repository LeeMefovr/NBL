import numpy as np
from itertools import product
from itertools import permutations
from collections import Counter

def generate_fleets(medals):
    fleets = []
    for num_1 in range(medals[0] + 1):
        for num_2 in range(medals[1] + 1):
            for num_3 in range(medals[2] + 1):
                for num_4 in range(medals[3] + 1):
                    for num_5 in range(medals[4] + 1):
                        num_t = num_1 + num_2 + num_3 + num_4 + num_5
                        if  num_t <= 8:
                            fleet = [0] * (8 - num_t) + [1] * num_1 + [2] * num_2 + [
                                3] * num_3 + [4] * num_4 + [5] * num_5
                            fleets.extend(set(permutations(fleet)))
    final_fleets = list()
    dp = []
    for index, fleet in enumerate(fleets):
        counter = Counter(fleet)
        tp = sorted(list(zip(counter.keys(), counter.values())), key=lambda x: x[0])
        if tp in dp:
            continue
        else:
            dp.append(tp)
            final_fleets.append(fleet)
    return final_fleets

def generate_stake_NBLs(stake_NBL):
    stake_NBL = [int(key) for key in stake_NBL.keys()]
    all_stake_NBL = sorted(list(product(stake_NBL, repeat=8)), key=lambda x:sum(x))
    return all_stake_NBL

def generate_starships_up():
    all_starship_up = sorted(list(product([0, 1, 2, 3], repeat=8)), key=lambda x:sum(x))
    return all_starship_up

def max_power_optimized(medals, N, ex_fee, up_fee, start_power, fm_fee, fm_power,
                        medals_slot_fee, medals_slot_power, stake_NBL):
    mining_power = 0  # 维护一个全局最大算力
    # 生成所有可能的编队情况
    fleets = generate_fleets(medals)
    starships_stake_NBLs = generate_stake_NBLs(stake_NBL) # 所有可能的质押NBL情况
    starships_up = generate_starships_up() # 所有可能的升级星舰的情况
    nums = len(fleets) # 总的运行次数
    cal = 0  # 计数器
    for fleet in fleets:
        cal += 1
        print("-" * 10 + f"当前进度{(cal / nums) * 100}%" + "-" * 10)
        total_cost = 0 # 初始化当前编队花费NBL
        starships_up_fee = 0 # 初始化升级星舰的费用
        medals_slot_cost = 0 # 初始化开勋章槽费用
        starships_num = np.count_nonzero(fleet) # 星舰数
        if starships_num < 1:
            continue
        if total_cost > N:
            print("NBL不足以兑换星舰")
            print("-" * 20)
            continue
        for medal_slot_num, medal_slot_fee in enumerate(medals_slot_fee[:min(starships_num + 1, 6)]):
            # if medal_slot_num < 1:
            #     continue
            if total_cost > N:
                print("NBL不足以开勋章槽")
                print("-" * 20)
                total_cost -= medals_slot_cost
                break
            for starship_up in starships_up:
                # if sum(starship_up) < 24:
                #     continue
                if total_cost > N:
                    print("NBL不足以升级星舰")
                    print("-" * 20)
                    total_cost -= starships_up_fee
                    break
                for starship_stake_NBL in starships_stake_NBLs:
                    # if sum(starship_stake_NBL) < 80000:
                    #     continue
                    flag = True
                    for m in range(8):
                        if fleet[m] == 0 and starship_stake_NBL[m] != 0:
                            flag = False
                            break
                    if flag == False:
                        continue
                    tp_mining_power = 0  # 初始化当前编队的算力
                    total_cost = 0
                    starships_ex_fee = sum(ex_fee[num] for num in fleet)  # 星舰兑换费用
                    starships_slot_fee = sum(fm_fee[:starships_num])  # 星舰开槽费用
                    medals_slot_cost = sum(medals_slot_fee[:medal_slot_num + 1]) # 开勋章槽费用
                    total_cost += (starships_ex_fee + starships_slot_fee)  # 初始化NBL花费 包括星舰兑换费用以及开槽费用
                    total_cost += medals_slot_cost  # 开勋章槽费用
                    starships_up_fee = sum(sum(up_fee[fleet[i]][:starship_up[i] + 1]) for i in range(8)) # 升级星舰的费用
                    total_cost += starships_up_fee
                    stake_NBL_fee = np.dot(np.int64(np.array(fleet) > 0), starship_stake_NBL) # 质押NBL的数量
                    total_cost += stake_NBL_fee
                    if total_cost > N:
                        # print("质押所需的NBL不足")
                        # print("-" * 20)
                        total_cost -= stake_NBL_fee
                        break

                    fm_coff = fm_power[starships_num - 1] # 编队加成系数
                    medals_select = sorted(fleet)[:medal_slot_num] # 按照勋章的等级从高到低质押
                    medal_power = sum(medals_slot_power[medal_select] for medal_select in medals_select) # 勋章算力加成
                    starships_power = sum((start_power[fleet[i]][starship_up[i]] + medal_power) \
                                       * fm_coff * stake_NBL[str(starship_stake_NBL[i])] for i in range(8)) # 编队各星舰算力
                    tp_mining_power += starships_power

                    if tp_mining_power > mining_power:
                        mining_power = tp_mining_power
                        print(f"星舰编队{fleet}")
                        print(f"对应等级{starship_up}")
                        print(f"对应质押NBL数量{starship_stake_NBL}")
                        print(f"星舰兑换费用以及开槽费用为{starships_ex_fee + starships_slot_fee}NBL")
                        print(f"升级星舰费用为{starships_up_fee}NBL")
                        print(f"开{medal_slot_num}个勋章槽，开勋章槽费用为{medals_slot_cost}NBL")
                        print(f"当前最佳方案如上，共消耗NBL{total_cost}，总算力为{mining_power}")
                        print('-' * 20)
    return mining_power




N = 3000  # NBL数量
medals = [5, 3, 0, 0, 0]  # 勋章数量
ex_fee = [0, 808, 1521, 2952, 4752, 6520]  # 兑换星舰的费用，这里做了兑换后必加速的假设
up_fee = np.array([[0, 0, 0, 0], [0, 40, 60, 85], [0, 75, 100, 125], [0, 100, 150, 200],
                   [0, 150, 200, 300], [0, 200, 300, 400]])  # 升级星舰的费用
fm_fee = [0, 70, 70, 105, 105, 140, 140, 210]  # 解锁编队槽费用
fm_power = [1, 1, 1.03, 1, 1.05, 1, 1.07, 1.1]  # 编队槽加成系数
start_power = np.array([[0, 0, 0, 0], [230, 320, 440, 610], [320, 430, 580, 780], [480, 630, 830, 1090],
                        [630, 830, 1090, 1430], [900, 1180, 1550, 2040]])  # 星舰初始算力
medals_slot_fee = [0, 50, 63, 75, 88, 100]  # 解锁徽章槽费用
medals_slot_power = [0, 20, 30, 45, 60, 75]  # 每种徽章给每艘星舰提供的算力
stake_NBL = {"0": 1, "2100": 2, "5300": 4, "10800": 6, "16000": 8, "23000": 10}  # 质押NBL数量及加成系数

max_power = max_power_optimized(medals, N, ex_fee, up_fee, start_power, fm_fee, fm_power,
                        medals_slot_fee, medals_slot_power, stake_NBL)