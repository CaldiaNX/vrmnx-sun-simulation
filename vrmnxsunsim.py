__title__ = "太陽シミュレータ Ver.1.0"
__author__ = "Caldia (原作：C-PON)"
__update__  = "2022/06/01"

import vrmapi
import math
import datetime

# ファイル読み込みの確認用
vrmapi.LOG("import " + __title__)
# ウィンドウ描画フラグ
_drawEnable = True
# スプライト番号
sprite = 0

# main
def vrmevent(obj,ev,param):
    global _drawEnable
    if ev =='init':
        # 初期化
        init(obj)
        # フレームイベント登録
        obj.SetEventFrame()
        # pキー登録
        obj.SetEventKeyDown('P')
    elif ev == 'frame':
        if _drawEnable:
            # ImGui描画
            di = obj.GetDict()
            drawFrame(di)
            tokei(di)
            keisan(di)
            tenkyu(di)
    elif ev == 'keydown':
        # ウィンドウ描画のON/OFF
        if param['keycode'] == 'P':
            # 表示反転
            _drawEnable = not _drawEnable


def init(obj):
    # Dict定義
    di = obj.GetDict()
    di['RS_DAY']=1 # (昼)天球リソース番号
    di['RS_EVE']=2 # (夕)天球リソース番号
    di['RS_NIG']=3 # (夜)天球リソース番号
    di['N_LAT'] =  34.701888  # 北緯(0- 90,マイナスで南緯)
    di['E_LON'] = 135.4949722 # 東経(0-180,マイナスで西経)
    di['UTC'] = 9  # タイムゾーン(-12 - +14)
    di['mon'] = 6  # 月(1-12)
    di['day'] = 20 # 日(1-31)
    di['hor'] = 12 # 時(0-23)
    di['min'] = 0  # 分(0-59)
    di['sec'] = 0  # 秒(0-59)
    di['season'] = 0 # 季節
    di['lon'] = 0   # 経度
    di['lat'] = 50  # 緯度
    di['iro'] = 0
    di['now'] = vrmapi.LAYOUT().SYSTEM().GetRealTime()
    di['move'] = True
    di['SPD'] = 120 # 加速度(1で現実速度)
    # 太陽と天球のアニメーション速度(秒) 現実速度1なら10分で動作
    di['ANIME'] = 1200 / di['SPD']
    # 季節計算
    seasonCalc(di)


# 日付と季節計算
def seasonCalc(di):
    m = di['mon']
    d = di['day']
    # 月計算
    if m > 12:
        m = 1
    elif m < 1:
        m = 12
    # 日計算
    if d < 1:
        if m == 1:
            m = 12
            d = 31
        elif m == 3:
            m = 2
            d = 29
        elif m == 5 or m == 7 or m == 10 or m == 12:
            d = 30
            m -= 1
        else:
            d = 31
            m -= 1
    if d > 31:
        d = 32
    if d > 29 and m == 2:
        d = 1
        m = 3
    elif d == 31 and ( m == 4 or m == 6 or m == 9 or m == 11):
        d = 1
        m += 1
    elif m == 12 and d == 32:
        m = 1
        d = 1
    elif d == 32:
        m += 1
        d = 1
    # 季節計算
    s = d - 20
    if m == 1:
        s -= 31
    elif m < 3:
        s -= 28
    elif m > 3:
        s -= 31
    elif m > 4:
        s += 30
    elif m > 5:
        s += 31
    elif m > 6:
        s += 30
    elif m > 7:
        s += 31
    elif m > 8:
        s += 31
    elif m > 9:
        s += 30
    elif m > 10:
        s += 31
    elif m > 11:
        s += 30

    di['mon'] = m
    di['day'] = d
    di['season'] = s


# ウィンドウ描画
def drawFrame(di):
    global __title__
    # ImGui定義
    g = vrmapi.ImGui()
    g.Begin("sunsim" ,__title__)

    if g.CollapsingHeader("cltree","カレンダー"):
        g.PushItemWidth(90.0)

        mm = [di['mon']]
        if g.InputInt("mon","月", mm):
            di['mon'] = mm[0]
            seasonCalc(di)

        g.SameLine()
        dd = [di['day']]
        if g.InputInt("day","日", dd):
            di['day'] = dd[0]
            seasonCalc(di)

        g.Separator()
        hh = [di['hor']]
        if g.InputInt("hor","時",hh):
            di['hor'] = hh[0]

        g.SameLine()
        mi = [di['min']]
        if g.InputInt("min","分",mi):
            di['min'] = mi[0]

        g.PopItemWidth()
        if g.Button("syut","現在時刻取得"):
            dt_now = datetime.datetime.now()
            di['mon'] = dt_now.month
            di['day'] = dt_now.day
            di['hor'] = dt_now.hour
            di['min'] = dt_now.minute
            di['sec'] = dt_now.second
            seasonCalc(di)

        g.SameLine()
        g.Text(str(int(di['sec'])))
        if g.TreeNode("acc","時計動作"):
            chk = [di['move']]
            if g.Checkbox("chk1","",chk):
                di['move'] = chk[0]
                di['now'] = vrmapi.LAYOUT().SYSTEM().GetRealTime()
            g.SameLine()

            spd = [di['SPD']]
            if g.InputInt("spd","速度",spd):
                if spd[0] < 1:
                    spd[0] = 1
                elif spd[0] > 5184000:
                    spd[0] = 5184000
                di['SPD'] = spd[0]
            g.TreePop()

    if g.CollapsingHeader("lonlat","位置情報"):
        nlat = [di['N_LAT']]
        if g.InputFloat("nlat","緯度",nlat):
            if nlat[0] > 90:
                nlat[0] = 90
            elif nlat[0] < -90:
                nlat[0] = -90
            di['N_LAT'] = nlat[0]

        elon = [di['E_LON']]
        if g.InputFloat("elon","経度",elon):
            if elon[0] > 180:
                elon[0] = -180
            elif elon[0] < -180:
                elon[0] = 180
            di['E_LON'] = elon[0]

        g.PushItemWidth(90.0)
        zone = [di['UTC']]
        if g.InputFloat("zone","タイムゾーン",zone):
            zone[0] = round(zone[0] * 10) / 10
            if zone[0] > 14:
                zone[0] = 3
            elif zone[0] < -12:
                zone[0] = 11
            di['UTC'] = zone[0]

    g.PopItemWidth()
    if g.CollapsingHeader("datatree","太陽位置"):
        g.Text("方位:"+str(round(di['lon']*100)/100))
        g.Text("高度:"+str(round(di['lat']*100)/100))

    g.End()


# 時計
def tokei(di):
    if di['move']==True:
        di['sec']=di['sec']+di['SPD']*(vrmapi.LAYOUT().SYSTEM().GetRealTime()-di['now'])
        di['now']=vrmapi.LAYOUT().SYSTEM().GetRealTime()
    while di['sec']>=60:
        di['sec']=di['sec']-60
        di['min']=di['min']+1
    if di['min']<0:
        di['min']=59
        di['hor']=di['hor']-1
    while di['min']>59:
        di['min']=di['min']-60
        di['hor']=di['hor']+1
    if di['hor']<0:
        di['hor']=23
        di['day']=di['day']-1
        seasonCalc(di)
    while di['hor']>23:
        di['hor']=di['hor']-24
        di['day']=di['day']+1
        seasonCalc(di)


# 太陽計算
def keisan(di):
    jisa=(di['UTC']*15-di['E_LON'])*4
    delta=23.4*math.sin(math.radians(di['season']/365*360))
    lat = math.degrees(
        math.asin(
            math.sin(math.radians(di['N_LAT'])) * 
            math.sin(math.radians(delta)) + 
            math.cos(math.radians(15 * (di['hor']-12+(di['min']+jisa) / 60+di['sec']/3600))) *
            math.cos(math.radians(delta))*math.cos(math.radians(di['N_LAT']))
        )
    )
    if math.cos(math.radians(lat))!=0:
        long = 90 + math.degrees(
            math.asin(
                round(
                    math.cos(math.radians(delta)) * 
                    math.sin(math.radians(15*(di['hor']-12+(di['min']+jisa)/60+di['sec']/3600))) / 
                    math.cos(math.radians(lat))
                    ,5
                )
            )
        )
        tmp=math.sin(math.radians(delta))-(math.sin(math.radians(lat))*math.sin(math.radians(di['N_LAT'])))
        if abs(tmp)<1e-10:
            long=15*(di['hor']-12+(di['min']+jisa)/60+di['sec']/3600)+90
            if long>180:
                long=long-360
            if di['N_LAT']<0:
                long=-long
        elif tmp>0:
            long=-long
    di['lon']=long
    di['lat']=lat
    vrmapi.LAYOUT().SKY().SetSunPos(long, lat)


# 天球書き換え
def tenkyu(di):
    sky = vrmapi.LAYOUT().SKY()
    if di['lat'] < 18 and di['iro']==0:
        di['iro']=1
        sky.LoadSkyImage(1,di['RS_EVE'])
        sky.SetAnimeSkyFactor(1.0, di['ANIME'])
        sky.SetSunType(6, di['ANIME'])
    if di['lat'] < -6 and di['iro']==1:
        di['iro']=1.5
        sky.SetSunType(5, di['ANIME'])
    if di['lat'] < -10 and di['iro']!=2:
        di['iro']=2
        sky.LoadSkyImage(0,di['RS_NIG'])
        sky.SetAnimeSkyFactor(0, di['ANIME'])
        sky.SetSunType(3, di['ANIME'])
    if di['lat'] > -7 and di['iro']==2:
        di['iro']=1.8
        sky.LoadSkyImage(1,di['RS_EVE'])
        sky.SetAnimeSkyFactor(1, di['ANIME'])
        sky.SetSunType(1, di['ANIME'])
    if di['lat'] > 12 and di['iro']!=0:
        di['iro']=0
        sky.LoadSkyImage(0,di['RS_DAY'])
        sky.SetAnimeSkyFactor(0, di['ANIME'])
        sky.SetSunType(0, di['ANIME'])
