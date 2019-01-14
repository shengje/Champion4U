from bs4 import BeautifulSoup
#from selenium import webdriver
import requests
import re
import time
import traceback


def get_soup(url):
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content, 'html.parser')
    return soup

def get_class(soup, clazz="", one=False):
    list_class = soup.find_all(class_=clazz)
    if one:
        return list_class[0]
    return list_class

def get_url(soup, clazz='', http=True):
    if clazz!='':
        url_list = soup.find_all(class_=clazz)
        url = url_list[0].find('a').get('href')
    else:
        try:
            url = soup.find('a').get('href')
        except:
            print('error in getting url')
            
    if not http:
        return url
    return "http:" + url

#decode, ignore
#ID, mode, date, result, length, champions_team1, champions_team2
def get_record(csv_writter, page):
    time.sleep(0.01)
    url_ladder = 'http://tw.op.gg/ranking/ladder/'
    url = url_ladder + 'page=' + str(page)
    soup = get_soup(url)
    url_list = get_class(soup, "ranking-table__row ")
    for player in url_list:
        url = player.find('a').get('href')
        list_game, player = get_games('http:' + url)
        print('player:', player)



        records = []
        summoners = {}

        for game in list_game:
            #time1 = time.process_time()
            game = game.div
            #id_summoner = game["data-summoner-id"]
            id_game = game["data-game-id"]
            result = game["data-game-result"]

            game = game.div
            game_ex = game.find(class_="GameType")
            type_game = re.findall('[^\n\t]+', game_ex.contents[0])
            if type_game[0]!='Ranked Solo':
                #print(type_game)
                continue
            game_ex = get_class(game, "FollowPlayers", True)
            players = get_class(game_ex, "ChampionImage")
            champions = []
            for player in players:
                champions.append(player.div.string)
            #print(champions)
            summoners_ex = []
            data_summoner = []
            i=0
            players = get_class(game_ex, "SummonerName")
            for p in players:
                try:
                    #print("")
                    id_summoner = p.find('a').string
                    #print(id_summoner, champions[i])
                    #print('test:', get_personal_champion_winrate(id_summoner, champions[i]))
                    data_summoner.append(get_personal_champion_winrate(id_summoner, champions[i]))
                    #print('okkkkkkkkkkkkkkkk')
                    i+=1
                    #summoners_ex.append([id_summoner, url_summoner])
                    #summoners[(id_summoner, url_summoner)] = 0
                except:
                    print('error:', p.find('a').string, champions[i])
                    data_summoner.append((0, 0, 0))
                    i+=1
                    id_summoner = "error"
                    url_summoner = "error"  
                    #summoners_ex.append([id_summoner, url_summoner])
            #time2 = time.process_time()
            #print('game record time:', time2-time1)

            #records.append([id_game, type_game[0], champions, result, summoners_ex])
            #print([id_game, type_game[0], champions, result, data_summoner])
            records.append([id_game, type_game[0], champions, result, data_summoner])
            dataset_building(records, csv_writter)
        #dataset_building(records, csv_writer)       
    #return records, summoners

def get_games(url_summoner):
    soup_summoner = get_soup(url_summoner)
    id_player = soup_summoner.find(class_="Name").string
    list_game = get_class(soup_summoner, "GameItemWrap")
    return list_game, id_player

def get_NO1():
    url_ladder = "http://tw.op.gg/ranking/ladder/"
    soup = get_soup(url_ladder)
    url_NO1 = get_url(soup, clazz="ranking-highest__item ranking-highest__item--big")
    return url_NO1

def dataset_building(records, csv_writer):
    #[id_game, type_game[0], champions, result, summoners_ex]
    for record in records:
        data=[]
        data.append(record[0])
        data.append(record[1])
        for r in record[2]:
            data.append(r)
        data.append(record[3])
        for r in record[4]:
            for x in r:
                data.append(x)
        csv_writer.writerow(data)

        
#input
#1.champion:英雄角色名字
    #格式--string
#output
#1.position_rate:走各路的機率, 格式為[上路, 打野, 中路, Bottom, 輔助]
    #格式--list[5]
#用途:線路判斷
def get_champion_position(champion):
    url = 'http://tw.op.gg/champion/' + champion + '/statistics'
    soup = get_soup(url)
    position = get_class(soup, "champion-stats-header__position__role")
    rate = get_class(soup, "champion-stats-header__position__rate")
    
    position_rate = [0, 0, 0, 0, 0]
    count = 0
    for p in position:
        if p.string=="Top":
            position_rate[0] = float(re.findall('[0-9]+', rate[count].string)[0])
        elif p.string=="Jungle":
            position_rate[1] = float(re.findall('[0-9]+', rate[count].string)[0])
        elif p.string=="Middle":
            position_rate[2] = float(re.findall('[0-9]+', rate[count].string)[0])
        elif p.string=="Bottom":
            position_rate[3] = float(re.findall('[0-9]+', rate[count].string)[0])
        elif p.string=="Support":
            position_rate[4] = float(re.findall('[0-9]+', rate[count].string)[0])
        count+=1
            
    #test
    
    return position_rate
    
def get_champion_winrate(champion):
    url = 'http://tw.op.gg/champion/' + champion + '/statistics'
    soup = get_soup(url)
    position = get_class(soup, "champion-stats-header__position__role")
    winrate = []
    for p in position:
        soup2 = get_soup(url + '/' + p.string)
        winrate.append(get_class(soup2, "champion-stats-trend-rate", True))
    #test
    
    return position, winrate

def get_player(summoner_id): 
    summoner = {}
    url = 'http://tw.op.gg/summoner/userName=' + summoner_id
    soup = get_soup(url)
    try:
        soup_rank = get_class(soup, "SummonerRatingMedium", True)
    except:
        try:
            url = 'http://tw.op.gg/summoner/userName=' + summoner_id
            soup = get_soup(url)
            time.sleep(1)
            soup_rank = get_class(soup, "SummonerRatingMedium", True)
        except:
            print('error:', summoner_id)
            #return 'error'
    #print(soup_rank)
    rank = get_class(soup_rank, "tierRank", True).string
    # if rank=="Gold 1":
    #     page=last_page+1
    rank_point = re.findall('[\S]+', get_class(soup_rank, "LeaguePoints", True).string)[0]
    soup_winlose = get_class(soup_rank, "WinLose", True)
    wins = re.findall('[0-9]+', get_class(soup_winlose, "wins", True).string)[0]
    losses = re.findall('[0-9]+', get_class(soup_winlose, "losses", True).string)[0]
    win_ratio = re.findall('[0-9]+', get_class(soup_winlose, "winratio", True).string)[0]
    #print(summoner_id, ':' , rank, rank_point, wins, losses, win_ratio)

    summoner['basic'] = {'rank':rank, 'rank_point':rank_point, 'wins':wins, 'losses':losses, 'win_ratio':win_ratio}
    summoner['champions'] = {}

    url = 'http://tw.op.gg/summoner/champions/userName=' + summoner_id
    soup = get_soup(url)
    champion_list1 = get_class(soup, "Row TopRanker")
    champion_list2 = get_class(soup, "Row ")
    champion_list = champion_list1 + champion_list2

    for c in champion_list:
        champion_name = get_class(c, "ChampionName Cell", True).get('data-value')
        winrate =  float(get_class(c, "RatioGraph Cell", True).get('data-value'))
        if winrate==0:
            win = 0
            lose = int(re.findall('[0-9]+',get_class(c, "Text Right", True).string)[0])
        elif winrate==100:
            win = int(re.findall('[0-9]+',get_class(c, "Text Left", True).string)[0])
            lose = 0
        else:
            win = int(re.findall('[0-9]+',get_class(c, "Text Left", True).string)[0])
            lose = int(re.findall('[0-9]+',get_class(c, "Text Right", True).string)[0])
        c_KDA = get_class(c, "KDA", True)
        kill = float(get_class(c, "Kill", True).string)
        death = float(get_class(c, "Death", True).string)
        assist = float(get_class(c, "Assist", True).string)
        if death==0:
            KDA = kill+assist
        else:
            KDA = (kill+assist)/death
        c_value = get_class(c, "Value Cell")
        try:
            gold = float(re.findall('[0-9]+', c_value[0].string)[0])*1000+float(re.findall('[0-9]+', c_value[0].string)[1])
        except:
            gold = float(re.findall('[0-9]+', c_value[0].string)[0])
        cs = float(re.findall('[0-9]+', c_value[1].string)[0])
        try:
            damage = float(re.findall('[0-9]+', c_value[4].string)[0])*1000+float(re.findall('[0-9]+', c_value[4].string)[1])
        except:
            try:
                damage = float(re.findall('[0-9]+', c_value[4].string)[0])
            except:
                damage = 0
        try:
            tank = float(re.findall('[0-9]+', c_value[5].string)[0])*1000+float(re.findall('[0-9]+', c_value[5].string)[1])
        except:
            try:
                tank = float(re.findall('[0-9]+', c_value[5].string)[0])
            except:
                tank = 0


        #print(champion_name, ':', win, lose, winrate, kill, death, assist, KDA, gold, cs, damage, tank)
        summoner['champions'][champion_name] = {}
        
        
        
        
        summoner['champions'][champion_name] = {'win':win, 'lose':lose, 'winrate':winrate, 'kill':kill, 'death':death, 'assist':assist, 'KDA':KDA, 'gold':gold, 'cs':cs, 'damage':damage, 'tank':tank}
    
    return summoner


if __name__ == "__main__":
    summoner = get_player('娉婷裊娜')
    print(summoner)
        