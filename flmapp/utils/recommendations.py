from math import sqrt
import numpy as np

# person1とperson2の距離を基にした類似性スコアを返す
# ユークリッド距離によるスコア
def sim_distance(prefs,person1,person2):
    # 二人とも評価しているアイテムのリストを得る
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1

    # 両者共に評価しているものが一つもなければ0を返す
    if len(si)==0: return 0

    # すべての差の平方を足し合わせる
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sum_of_squares)

# ピアソン相関によるスコア
def sim_pearson(prefs,p1,p2):
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

# ディクショナリprefsからpersonにもっともマッチするものたちを返す
# 結果の数と類似性関数はオプションのパラメータ
def topMatches(prefs,person,followed,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other)
            for other in prefs if other!=person and other not in followed]
    # 高スコアがリストの最初に来るように並び替える
    scores.sort()
    scores.reverse()
    u_recommend_id = np.array(scores)
    if len(u_recommend_id)>0:
        return u_recommend_id[0:3, 1]
    else:
        return None

# person以外のユーザーの評点の重み付き平均を行い、pesonへの推薦を算出する
def getRecommendations(prefs,person,on_display,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        # 自分自身とは比較しない
        if other==person: continue
        sim=similarity(prefs,person,other)

        # 0以下のスコアは無視する
        if sim<=0: continue

        for item in prefs[other]:
            # まだ見ていない商品の得点のみを算出
            if item not in prefs[person] or prefs[person][item]==0:
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
        recommend_id = np.array(rankings)
        if len(recommend_id)>0:
            return recommend_id[0:3, 1]
        else:
            return None
