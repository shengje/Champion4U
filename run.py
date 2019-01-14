import json
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import scale
import craw 

def rank_check(data, rank_list):
    rank_num = []
    for r in rank_list:
        rank_num.append(len(data[r].keys()))
    return rank_num

def read_json(name, rank_list):
    name = name+'.json'
    f = open(name, 'r')
    for line in reversed(f.readlines()):
        json_data = line
        break
    f.close()
    data = json.loads(json_data)
    rank_num = rank_check(data, rank_list)
    return data, rank_num

def user_matrix(user, champ_list, proper='kda'):
    thres = 5
    n = 0

    champ_winrate = []
    champ_kda = []
    champ_cs = []
    champ_gold = []
    champ_damage = []
    champ_tank = []
    champ_proper = []
    user_basic = []
    
    for champ in champ_list:
        
        if champ[0] not in user['champions']:
            champ_winrate.append(0)
            champ_kda.append(0)
            champ_cs.append(0)
            champ_gold.append(0)
            champ_damage.append(0)
            champ_tank.append(0)
        elif (int(user['champions'][champ[0]]['win']) + int(user['champions'][champ[0]]['lose'])) <thres:
            champ_winrate.append(0)
            champ_kda.append(0)
            champ_cs.append(0)
            champ_gold.append(0)
            champ_damage.append(0)
            champ_tank.append(0)
            n += 1
        else:
            champ_kda.append(user['champions'][champ[0]]['KDA'])
            champ_winrate.append(user['champions'][champ[0]]['winrate'])
            champ_cs.append(user['champions'][champ[0]]['cs'])
            champ_gold.append(user['champions'][champ[0]]['gold'])
            champ_damage.append(user['champions'][champ[0]]['damage'])
            champ_tank.append(user['champions'][champ[0]]['tank'])
    user_basic.append(int(user['basic']['win_ratio']))
    #user_basic.append(int(user['basic']['wins']))
    #user_basic.append(int(user['basic']['losses']))
    #print(n)
    #champ_cs = np.array(champ_cs)
    #print(type(champ_cs))
    if proper == 'winrate':
        return champ_winrate
    elif proper == 'kda':
        return champ_kda
    elif proper == 'cs':
        return champ_cs
    elif proper == 'gold':
        return champ_gold
    elif proper == 'damage':
        return champ_kda
    elif proper == 'tank':
        return champ_tank
    elif proper == 'all':
        champ_proper.append(champ_winrate)
        champ_proper.append(champ_kda)
        champ_proper.append(champ_cs)
        champ_proper.append(champ_gold)
        champ_proper.append(champ_damage)
        champ_proper.append(champ_tank)
        return champ_proper


def user_road(n, user, champ_road, champ_list, road_dict):
    rate = 0.4
    thes = 5
    user_play = 0
    #user_play = int(user['basic']['wins']) + int(user['basic']['losses'])
    for champ in champ_list:
        if champ[0] in user['champions']:
            user_play += (int(user['champions'][champ[0]]['win']) + 
                            int(user['champions'][champ[0]]['lose']))
    if user_play == 0:
        print(n)
        user_play += 1
    road = ['Top', 'Jungle', 'Middle', 'Bottom', 'Support']
    for i in range(5):
        cham_play = 0
        road_champ = champ_road[road[i]]
        for r in road_champ:
            champion = champ_list[r][0]
            #print(champion)
            if champion in user['champions']:
                game = (int(user['champions'][champion]['win']) + 
                        int(user['champions'][champion]['lose']))
                if game > thes:
                     cham_play += game 
        if (cham_play / user_play) > rate:
            if cham_play > user_play:
                print(n, cham_play, user_play)
            road_dict[road[i]].append(n)
        break
    return road_dict

def isNaN(num):
    return num != num

def user_data(file_list, proper, rank_list, champ_list):
    #file_list = ['summoner1', 'summoner6']
    user_proper = []
    user_id = []
    user_n = 0
    for f in file_list:
        data, rank_num = read_json(f, rank_list)
        for i, r in enumerate(rank_num):
            if r != 0:
                rank = rank_list[i]
                user_name = data[rank].keys()
                for n, user in enumerate(user_name):
                    user_proper.append(user_matrix(data[rank][user], champ_list, proper=proper))
                    #road_dict = user_road(user_n, data[rank][user], champ_road, champ_list, road_dict)       
                    user_n +=1
                user_name = list(user_name)
                user_id = user_id + user_name
    user_proper = np.array(user_proper)
    #print(len(user_id))
    #print(user_proper.shape)
    return user_id, user_proper

def champion_name(name):
    champ_list = pd.read_csv('name.csv', header=None).values
    if name in champ_list:
        return True
    

def main(user_id, proper):
    
    road_dict = {'Top':[], 'Jungle':[], 'Middle':[], 'Bottom':[], 'Support':[]}
    rank_list = ['Challenger', 'Grandmaster', 'Master', 
             'Diamond 1', 'Diamond 2', 'Diamond 3', 
             'Diamond 4', 'Platinum 1', 'Platinum 2', 
             'Platinum 3', 'Platinum 4', 'Gold 1']
    champ_list = pd.read_csv('name.csv', header=None).values

    champ_dict = {}
    for i,c in enumerate(champ_list):
        champ_dict[c[0]] = i
    champ_road = {}
    road = ['Top', 'Jungle', 'Middle', 'Bottom', 'Support']
    road_data = pd.read_csv('champion_road.csv', header=None, index_col=0)
    for r in road:
        champ = []
        for i in road_data.loc[r]:
            if isNaN(i) == False:
                champ.append(champ_dict[i])
        champ_road[r] = champ
    
    # read file
    file_list = ['summoner1', 'summoner6']
    user_name, user_proper = user_data(file_list, 'kda', rank_list, champ_list)
    X = user_proper
    svd = TruncatedSVD(n_components=10, n_iter=5, random_state=42)
    P = svd.fit_transform(X)
    Q = svd.components_
    #X_n = np.dot(P, Q)
    try:
        test_x = craw.get_player(user_id)
    except:
        return 'error'

    test_x = np.array(user_matrix(test_x, champ_list, proper='kda'))
    test_P = svd.transform(test_x.reshape(1,-1))
    test_user = np.dot(test_P, Q)

    n_sort = np.argsort(test_user[0])
    user_recommend = []
    for i in range(5):
        user_recommend.append(champ_list[n_sort][-i-5:][0][0])

    return user_recommend



if __name__ == "__main__":
    user_id = 'TF'
    proper = 'kda'
    recommend = main(user_id, proper)
    print(recommend)


