from math import sqrt
import numpy as np
from functools import lru_cache

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

@lru_cache()
def topMatches(c_userid):
    """
    ディクショナリprefsからc_useridにもっともマッチするものたちを返す
    """
    prefs = loadData()
    followed = UserConnect.select_follows_user_id_by_user_id(c_userid)
    # 一次元タプルに変換
    followed = sum(followed, ())

    scores=[(sim_pearson(prefs,c_userid,other),other)
            for other in prefs if other!=c_userid and other not in followed]
    # 高スコアがリストの最初に来るように並び替える
    scores.sort()
    scores.reverse()
    print("*"*100)
    print("ユーザーレコメンド")
    print(scores)
    print("*"*100)
    u_recommend_id = np.array(scores)
    if len(u_recommend_id)>0:
        return u_recommend_id[0:3, 1]
    else:
        return None

@lru_cache()
def getRecommendations(c_userid):
    """c_userid以外のユーザーの評点の重み付き平均を行い、c_useridへの推薦を算出する"""
    prefs = loadData()
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
            if (item not in prefs[c_userid] or prefs[c_userid][item]==0 or prefs[c_userid][item]==1) and item not in sell:
                # 出品中の商品の特典のみを算出
                if item in on_display:
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
            return recommend_id[0:3, 1]
        else:
            return None


def loadData():
    """データ整形"""
    prefs={}
    users = User.query.all()
    items = Sell.query.all()
    for user in users:
        userid = user.User_id
        prefs.setdefault(userid,{})
        for item in items:
            itemid = item.Sell_id
            rating = 0
            bought = Buy.buy_exists_user_id(userid, itemid)
            if bought:
                rating += 3
            else:
                b_history = BrowsingHistory.b_history_exists(userid, itemid)
                if b_history:
                    rating += 1
                liked = Likes.liked_exists_user_id(userid, itemid)
                if liked:
                    rating += 2
            prefs[userid][itemid] = rating
    return prefs


def recommend(c_userid):
    """協調フィルタリングユーザーベースレコメンド"""
    # 商品レコメンド
    recommends = getRecommendations(c_userid)
    # ユーザーレコメンド
    u_recommends = topMatches(c_userid)
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

def associationRules(transactions,userid,followed):
    relim_input = itemmining.get_relim_input(transactions)
    item_sets = itemmining.relim(relim_input, min_support=2)
    rules = assocrules.mine_assoc_rules(item_sets, min_support=2, min_confidence=0.3)

    recom_user = {}
    for rule_user in rules:
        if userid in rule_user[0] and not any(map(rule_user[1].__contains__, followed)) and not userid in rule_user[1]:
            # 支持度
            support = rule_user[2]/len(transactions)
            # リフト値 1より大きい場合は、Aが発生するとBが発生しやすくなると解釈できる
            lift = (rule_user[3]/support,)
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
