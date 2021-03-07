from math import sqrt
import numpy as np
import requests
import json

from flmapp.models.user import (
    User
)
from flmapp.models.reaction import (
    Likes, UserConnect, BrowsingHistory
)
from flmapp.models.trade import (
    Sell, Buy
)


def sim_pearson(prefs,p1,p2):
    """ピアソン相関によるスコア"""
    # 両者が互いに評価しているアイテムのリストを取得
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    
    # 要素の数を調べる
    n=len(si)

    # 共に評価しているアイテムがなければ0を返す
    if n==0: return 0

    # すべての嗜好を合計する
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])

    # 平方を合計する
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])

    # 積を合計する
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

    # ピアソンによるスコアを計算する
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r=num/den

    return r


def topMatches(c_userid):
    """
    ディクショナリprefsからc_useridにもっともマッチするものたちを返す
    """
    prefs = loadData()
    prefs.setdefault(c_userid,{})
    followed = UserConnect.select_follows_user_id_by_user_id(c_userid)
    # 一次元タプルに変換
    followed = sum(followed, ())

    # scores=[(sim_pearson(prefs,c_userid,other),other)
    #         for other in prefs if other!=c_userid and int(other) not in followed]

    scores = []
    for other in prefs:
        if other!=c_userid and int(other) not in followed:
            sim=sim_pearson(prefs,c_userid,other)
            if sim>0:
                scores.append([sim,other])

    # 高スコアがリストの最初に来るように並び替える
    scores.sort()
    scores.reverse()
    print("*"*100)
    print("ユーザーレコメンド")
    print(scores)
    print("*"*100)
    u_recommend_id = np.array(scores)
    if len(u_recommend_id)>0:
        if len(u_recommend_id) >= 3:
            #! X[start:end]endは含まれない
            return u_recommend_id[0:3, 1]
        if len(u_recommend_id) == 2:
            return u_recommend_id[0:2, 1]
        if len(u_recommend_id) == 1:
            return u_recommend_id[0:1, 1]
    else:
        return None


def getRecommendations(c_userid):
    """c_userid以外のユーザーの評点の重み付き平均を行い、c_useridへの推薦を算出する"""
    prefs = loadData()
    prefs.setdefault(c_userid,{})
    on_display = Sell.select_all_sell_by_deal_status(1)
    sell = Sell.select_sell_id_by_user_id(c_userid)
    followed = UserConnect.select_follows_user_id_by_user_id(c_userid)
    # 一次元タプルに変換
    on_display = sum(on_display, ())
    followed = sum(followed, ())
    sell = sum(sell, ())

    totals={}
    simSums={}

    for other in prefs:
        # 自分自身とは比較しない
        if other==c_userid:
            continue
        sim=sim_pearson(prefs,c_userid,other)

        # 0以下のスコアは無視する
        if sim<=0: continue

        for item in prefs[other]:
            # 評価が1か0かつ自分が出品した商品以外
            if (item not in prefs[c_userid] or prefs[c_userid][item]==0 or prefs[c_userid][item]==1) and int(item) not in sell:
                # 出品中の商品の特典のみを算出
                if int(item) in on_display:
                    # 類似度*スコア
                    totals.setdefault(item,0)
                    totals[item]+=prefs[other][item]*sim
                    # 類似度を合計
                    simSums.setdefault(item,0)
                    simSums[item]+=sim
        
    #正規化したリストを作る
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    # ソート済みのリストを返す
    rankings.sort()
    rankings.reverse()
    print("*"*100)
    print("アイテムレコメンド")
    print(rankings)
    print("*"*100)
    recommend_id = np.array(rankings)
    if len(recommend_id)>0:
        if len(recommend_id) >= 3:
            #! X[start:end]endは含まれない
            return recommend_id[0:3, 1]
        if len(recommend_id) == 2:
            return recommend_id[0:2, 1]
        if len(recommend_id) == 1:
            return recommend_id[0, 1]
    else:
        return None


def loadData():
    """データ整形"""
    # prefs={}
    # users = User.query.all()
    # items = Sell.query.all()
    # for user in users:
    #     userid = user.User_id
    #     prefs.setdefault(str(userid),{})
    #     for item in items:
    #         itemid = item.Sell_id
    #         rating = 0
    #         bought = Buy.buy_exists_user_id(userid, itemid)
    #         if bought:
    #             rating += 3
    #         else:
    #             b_history = BrowsingHistory.b_history_exists(userid, itemid)
    #             if b_history:
    #                 rating += 1
    #             liked = Likes.liked_exists_user_id(userid, itemid)
    #             if liked:
    #                 rating += 2
    #         prefs[str(userid)][str(itemid)] = rating
    # print("prefs"+"*"*100)
    # print(prefs)
    # ここから 高速化用API通信
    get_url = '{host}:{port}/get_prefs'.format(**{
        'host': 'http://127.0.0.1',
        'port': '8000'
    })
    res = requests.get(url=get_url)
    prefs = json.loads(res.text)
    # ここまで 高速化用API通信
    # ↓テスト用
    # prefs = {1: {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 3, 15: 3, 16: 2, 17: 0, 18: 1, 19: 0, 20: 3, 21: 0, 22: 3, 23: 3, 24: 0, 25: 3, 26: 0, 27: 2, 28: 2, 29: 0, 30: 0, 31: 3, 32: 0, 33: 3, 34: 3, 35: 0, 36: 1, 37: 0, 38: 2, 39: 3, 40: 0, 41: 0, 42: 3, 43: 2, 44: 3, 45: 1, 46: 1, 47: 1, 48: 0, 50: 3, 51: 0, 52: 0, 54: 3, 55: 0, 56: 0, 58: 1, 59: 0}, 2: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 3, 11: 0, 12: 3, 13: 0, 14: 0, 15: 0, 16: 0, 17: 1, 18: 3, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 3, 33: 2, 34: 0, 35: 3, 36: 0, 37: 1, 38: 3, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 3, 47: 0, 48: 0, 50: 3, 51: 0, 52: 0, 54: 3, 55: 0, 56: 0, 58: 0, 59: 0}, 3: {1: 0, 2: 3, 3: 0, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 2, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 3, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 50: 0, 51: 0, 52: 1, 54: 0, 55: 1, 56: 0, 58: 1, 59: 3}, 4: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 3, 12: 0, 13: 3, 14: 0, 15: 0, 16: 2, 17: 0, 18: 0, 19: 3, 20: 0, 21: 0, 22: 1, 23: 0, 24: 0, 25: 3, 26: 0, 27: 0, 28: 0, 29: 0, 30: 1, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 2, 42: 0, 43: 0, 44: 0, 45: 0, 46: 3, 47: 0, 48: 0, 50: 3, 51: 0, 52: 0, 54: 2, 55: 0, 56: 0, 58: 0, 59: 0}, 5: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 3, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 1, 19: 0, 20: 3, 21: 1, 22: 0, 23: 0, 24: 3, 25: 0, 26: 0, 27: 1, 28: 0, 29: 3, 30: 0, 31: 0, 32: 0, 33: 3, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 3, 40: 0, 41: 0, 42: 0, 43: 1, 44: 0, 45: 1, 46: 3, 47: 0, 48: 0, 50: 0, 51: 3, 52: 1, 54: 0, 55: 3, 56: 0, 58: 0, 59: 0}, 6: {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 1, 14: 0, 15: 0, 16: 1, 17: 1, 18: 0, 19: 0, 20: 0, 21: 1, 22: 1, 23: 0, 24: 3, 25: 3, 26: 0, 27: 0, 28: 0, 29: 3, 30: 0, 31: 0, 32: 3, 33: 0, 34: 0, 35: 0, 36: 0, 37: 1, 38: 0, 39: 0, 40: 0, 41: 3, 42: 0, 43: 0, 44: 0, 45: 3, 46: 0, 47: 0, 48: 2, 50: 3, 51: 0, 52: 0, 54: 0, 55: 3, 56: 3, 58: 0, 59: 3}, 7: {1: 0, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0, 7: 3, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 3, 19: 0, 20: 3, 21: 3, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 3, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 1, 47: 3, 48: 0, 50: 0, 51: 1, 52: 0, 54: 0, 55: 1, 56: 0, 58: 0, 59: 3}, 8: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 3, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 3, 21: 3, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 3, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 50: 0, 51: 0, 52: 0, 54: 0, 55: 3, 56: 3, 58: 0, 59: 3}, 9: {1: 0, 2: 3, 3: 3, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 3, 13: 1, 14: 3, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 3, 21: 0, 22: 0, 23: 0, 24: 1, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 1, 34: 0, 35: 0, 36: 0, 37: 0, 38: 3, 39: 3, 40: 0, 41: 0, 42: 0, 43: 0, 44: 3, 45: 0, 46: 0, 47: 0, 48: 0, 50: 0, 51: 0, 52: 0, 54: 0, 55: 0, 56: 0, 58: 0, 59: 3}, 10: {1: 3, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 3, 15: 3, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 2, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 2, 43: 0, 44: 2, 45: 1, 46: 0, 47: 1, 48: 0, 50: 0, 51: 2, 52: 0, 54: 0, 55: 2, 56: 0, 58: 0, 59: 3}, 11: {1: 3, 2: 3, 3: 3, 4: 3, 5: 0, 6: 0, 7: 0, 8: 3, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 3, 15: 1, 16: 0, 17: 3, 18: 0, 19: 0, 20: 0, 21: 2, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 1, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 3, 39: 0, 40: 3, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 50: 0, 51: 1, 52: 1, 54: 0, 55: 2, 56: 0, 58: 0, 59: 0}, 12: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 3, 11: 0, 12: 0, 13: 0, 14: 3, 15: 0, 16: 0, 17: 0, 18: 3, 19: 0, 20: 0, 21: 2, 22: 3, 23: 3, 24: 0, 25: 3, 26: 0, 27: 0, 28: 3, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 3, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 50: 3, 51: 1, 52: 0, 54: 0, 55: 0, 56: 3, 58: 0, 59: 0}, 13: {1: 0, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 1, 16: 0, 17: 0, 18: 1, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 3, 26: 3, 27: 0, 28: 3, 29: 3, 30: 0, 31: 0, 32: 3, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 3, 46: 0, 47: 0, 48: 0, 50: 0, 51: 0, 52: 3, 54: 0, 55: 0, 56: 0, 58: 0, 59: 0}, 14: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 3, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 3, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 1, 23: 0, 24: 0, 25: 3, 26: 1, 27: 0, 28: 1, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 3, 50: 0, 51: 0, 52: 0, 54: 0, 55: 0, 56: 0, 58: 0, 59: 0}, 15: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 3, 36: 0, 37: 3, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 2, 46: 0, 47: 3, 48: 0, 50: 3, 51: 0, 52: 1, 54: 0, 55: 0, 56: 0, 58: 0, 59: 0}}
    return prefs


def recommend(c_userid):
    """協調フィルタリングユーザーベースレコメンド"""
    # 商品レコメンド
    recommends = getRecommendations(str(c_userid))
    # ユーザーレコメンド
    u_recommends = topMatches(str(c_userid))
    r_item_list = []
    if recommends is not None:
        for recommend in recommends:
            recommend_id = int(recommend)
            r_item_list.append(Sell.select_sell_by_sell_id(recommend_id))
    elif recommends is None:
        r_item_list = []
    r_user_list = []
    if u_recommends is not None:
        for u_recommend in u_recommends:
            u_recommend_id = int(u_recommend)
            r_user_list.append(User.select_user_by_id(u_recommend_id))
    elif u_recommends is None:
        r_user_list = []
    return r_item_list,r_user_list


# アソシエーション・ルール・マイニング
from pymining import itemmining, assocrules

def associationRules(transactions,userid,followed=(),c_userid=None):
    relim_input = itemmining.get_relim_input(transactions)
    item_sets = itemmining.relim(relim_input, min_support=2)
    rules = assocrules.mine_assoc_rules(item_sets, min_support=2, min_confidence=0.5)

    recom_user = {}
    for rule_user in rules:
        if userid in rule_user[0] and not any(map(rule_user[1].__contains__, followed)) and not c_userid in rule_user[1]:
            # 支持度
            support = rule_user[2]/len(transactions)
            # リフト値 1より大きい場合は、Aが発生するとBが発生しやすくなると解釈できる
            lift = (rule_user[3]/support,)
            if lift[0] <= 1:
                continue
            rule_user += lift
            recom_user[rule_user[1]] = rule_user[4]
    recom_user_sorted = sorted(recom_user.items(), key=lambda x:x[1], reverse=True)
    print("*"*100)
    print("ユーザーレコメンド(バスケット分析)")
    print(recom_user_sorted)
    print("*"*100)
    rcom_userid_list = set()
    for rcom_userid in recom_user_sorted:
        rcom_userid_list = rcom_userid_list.union(rcom_userid[0])
    return list(rcom_userid_list)
