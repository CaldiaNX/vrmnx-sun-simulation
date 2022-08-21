import vrmapi
import math
import datetime
sprite=0
def init(obj):
    global sprite
    sprite = obj.CreateSprite()
    lodict=obj.GetDict()
    sprite.LoadSystemTexture(lodict['clrs'])
    lodict['tsuki']=6#月(1-12)
    lodict['nichi']=20#日(1-31)
    lodict['Jikan']=12#初期時刻(0-23)
    lodict['hun']=0#初期分(0-59)
    lodict['hayasa']=1#時間の加速度1で現実速度
    lodict['ido']=34.701888#北緯(0-90,マイナスで南緯)
    lodict['keido']=135.4949722#東経(0-180,マイナスで西経)
    lodict['zone']=9.0#タイムゾーン(-12-+14)
    lodict['kisetsu']=0
    lodict['long']=0
    lodict['lat']=50
    lodict['sec']=0
    lodict['move']=True
    lodict['stokei']=True
    lodict['iro']=0
    lodict['time']=vrmapi.LAYOUT().SYSTEM().GetRealTime()
    season(obj)

#日付と季節計算
def season(obj):
    lodict=obj.GetDict()
    tsuki=lodict['tsuki']
    nichi=lodict['nichi']
    if tsuki>12:
        tsuki=1
    if tsuki<1:
        tsuki=12
    if nichi<1:
        if tsuki==1:
            tsuki=12
            nichi=31
        elif tsuki==3:
            tsuki=2
            nichi=29
        elif tsuki==5 or tsuki==7 or tsuki==10 or tsuki==12:
            nichi=30
            tsuki=tsuki-1
        else:
            nichi=31
            tsuki=tsuki-1
    if nichi>31:
        nichi=32
    if nichi>29 and tsuki==2:
        nichi=1
        tsuki=3
    elif nichi==31 and (tsuki==4 or tsuki==6 or tsuki==9 or tsuki==11):
        nichi=1
        tsuki=tsuki+1
    elif tsuki==12 and nichi==32:
        tsuki=1
        nichi=1
    elif nichi==32:
        tsuki=tsuki+1
        nichi=1         
    kisetsu=nichi-20
    if tsuki==1:
        kisetsu=kisetsu-31
    if tsuki<3:
        kisetsu=kisetsu-28
    if tsuki>3:
        kisetsu=kisetsu+31
    if tsuki>4:
        kisetsu=kisetsu+30
    if tsuki>5:
        kisetsu=kisetsu+31
    if tsuki>6:
        kisetsu=kisetsu+30
    if tsuki>7:
        kisetsu=kisetsu+31
    if tsuki>8:
        kisetsu=kisetsu+31
    if tsuki>9:
        kisetsu=kisetsu+30
    if tsuki>10:
        kisetsu=kisetsu+31
    if tsuki>11:
        kisetsu=kisetsu+30
    lodict['tsuki']=tsuki
    lodict['nichi']=nichi
    lodict['kisetsu']=kisetsu

#操作ウィンドウ
def window(obj):
    lodict=obj.GetDict()
    g=vrmapi.ImGui()
    g.Begin("sunsim","太陽計算")
    if g.CollapsingHeader("cltree","カレンダー"):
       g.PushItemWidth(90.0)
       tsuki=[lodict['tsuki']]
       if g.InputInt("mon","月",tsuki):
           lodict['tsuki']=tsuki[0]
           season(obj)
       nichi=[lodict['nichi']]
       g.SameLine()
       if g.InputInt("dat","日",nichi):
           lodict['nichi']=nichi[0]
           season(obj)
       g.Separator()
       Jikan=[lodict['Jikan']]
       if g.InputInt("hou","時",Jikan):
           lodict['Jikan']=Jikan[0]
       g.SameLine()
       hun=[lodict['hun']]
       if g.InputInt("minu","分",hun):
           lodict['hun']=hun[0]
       g.PopItemWidth()
       if g.Button("syut","現在時刻取得"):
           dt_now = datetime.datetime.now()
           lodict['tsuki']=dt_now.month
           lodict['nichi']=dt_now.day
           lodict['Jikan']=dt_now.hour
           lodict['hun']=dt_now.minute
           lodict['sec']=dt_now.second
           season(obj)
       g.SameLine()
       g.Text(str(int(lodict['sec'])))
       if g.TreeNode("acc","時計動作"):
           chk=[lodict['move']]
           if g.Checkbox("chk1","",chk):
               lodict['move']=chk[0]
               lodict['time']=vrmapi.LAYOUT().SYSTEM().GetRealTime()
           g.SameLine()
           hayasa=[lodict['hayasa']]
           if g.InputInt("ksk","速度",hayasa):
               if hayasa[0]<1:
                   hayasa[0]=1
               if hayasa[0]>5184000:
                   hayasa[0]=5184000
               lodict['hayasa']=hayasa[0]
           g.TreePop()
    if g.CollapsingHeader("lonlat","位置情報"):
       ido=[lodict['ido']]
       if g.InputFloat("ido","緯度",ido):
           if ido[0]>90:
               ido[0]=90
           if ido[0]<-90:
               ido[0]=-90
           lodict['ido']=ido[0]
       keido=[lodict['keido']]
       if g.InputFloat("keido","経度",keido):
           if keido[0]>180:
               keido[0]=-180
           if keido[0]<-180:
               keido[0]=180
           lodict['keido']=keido[0]
       zone=[lodict['zone']]
       g.PushItemWidth(90.0)
       if g.InputFloat("zone","タイムゾーン",zone):
           zone[0]=round(zone[0]*10)/10
           if zone[0]>14:
               zone[0]=3
           if zone[0]<-12:
               zone[0]=11
           lodict['zone']=zone[0]
    g.PopItemWidth()
    if g.CollapsingHeader("datatree","太陽位置"):
        g.Text("方位:"+str(round(lodict['long']*100)/100))
        chk2=[lodict['stokei']]
        g.Text("高度:"+str(round(lodict['lat']*100)/100))
        if g.Checkbox("chk2","時計画像表示",chk2):
            lodict['stokei']=chk2[0]
    g.End()
    tokei(obj)
    if lodict['stokei']:
        stokei(obj)

#太陽計算
def keisan(obj):
    lodict=obj.GetDict()
    jisa=(lodict['zone']*15-lodict['keido'])*4
    delta=23.4*math.sin(math.radians(lodict['kisetsu']/365*360))
    lat=math.degrees(math.asin(math.sin(math.radians(lodict['ido']))*math.sin(math.radians(delta))+math.cos(math.radians(15*(lodict['Jikan']-12+(lodict['hun']+jisa)/60+lodict['sec']/3600)))*math.cos(math.radians(delta))*math.cos(math.radians(lodict['ido']))))
    if math.cos(math.radians(lat))!=0:
        long=90+math.degrees(math.asin(round(math.cos(math.radians(delta))*math.sin(math.radians(15*(lodict['Jikan']-12+(lodict['hun']+jisa)/60+lodict['sec']/3600)))/math.cos(math.radians(lat)),5)))
        tmp=math.sin(math.radians(delta))-(math.sin(math.radians(lat))*math.sin(math.radians(lodict['ido'])))
        if abs(tmp)<1e-10:
            long=15*(lodict['Jikan']-12+(lodict['hun']+jisa)/60+lodict['sec']/3600)+90
            if long>180:
                long=long-360
            if lodict['ido']<0:
                long=-long
        elif tmp>0:
            long=-long
    lodict['long']=long
    lodict['lat']=lat
    vrmapi.LAYOUT().SKY().SetSunPos(long, lat)
    tenkyu(obj)

#天球書き換え
def tenkyu(obj):
    lodict=obj.GetDict()
    if lodict['lat']<7 and lodict['iro']==0:
        lodict['iro']=1
        vrmapi.LAYOUT().SKY().LoadSkyImage(1,lodict['yuurs'])
        vrmapi.LAYOUT().SKY().SetAnimeSkyFactor(1.0, 100/lodict['hayasa'])
        vrmapi.LAYOUT().SKY().SetSunType(6, 100/lodict['hayasa'])
    if lodict['lat']<-6 and lodict['iro']==1:
        lodict['iro']=1.5
        vrmapi.LAYOUT().SKY().SetSunType(5, 100/lodict['hayasa'])
    if lodict['lat']<-12 and lodict['iro']!=2:
        lodict['iro']=2
        vrmapi.LAYOUT().SKY().LoadSkyImage(0,lodict['yorrs'])
        vrmapi.LAYOUT().SKY().SetAnimeSkyFactor(0, 100/lodict['hayasa'])
        vrmapi.LAYOUT().SKY().SetSunType(3, 100/lodict['hayasa'])
    if lodict['lat']>-12 and lodict['iro']==2:
        lodict['iro']=1.8
        vrmapi.LAYOUT().SKY().LoadSkyImage(1,lodict['yuurs'])
        vrmapi.LAYOUT().SKY().SetAnimeSkyFactor(1, 100/lodict['hayasa'])
        vrmapi.LAYOUT().SKY().SetSunType(1,100/lodict['hayasa'])
    if lodict['lat']>7 and lodict['iro']!=0:
        lodict['iro']=0
        vrmapi.LAYOUT().SKY().LoadSkyImage(0,lodict['hirrs'])
        vrmapi.LAYOUT().SKY().SetAnimeSkyFactor(0, 100/lodict['hayasa'])
        vrmapi.LAYOUT().SKY().SetSunType(0, 100/lodict['hayasa'])

#時計
def tokei(obj):
    lodict=obj.GetDict()
    if lodict['move']==True:
        lodict['sec']=lodict['sec']+lodict['hayasa']*(vrmapi.LAYOUT().SYSTEM().GetRealTime()-lodict['time'])
        lodict['time']=vrmapi.LAYOUT().SYSTEM().GetRealTime()
    while lodict['sec']>=60:
        lodict['sec']=lodict['sec']-60
        lodict['hun']=lodict['hun']+1
    if lodict['hun']<0:
        lodict['hun']=59
        lodict['Jikan']=lodict['Jikan']-1
    while lodict['hun']>59:
        lodict['hun']=lodict['hun']-60
        lodict['Jikan']=lodict['Jikan']+1
    if lodict['Jikan']<0:
        lodict['Jikan']=23
        lodict['nichi']=lodict['nichi']-1
        season(obj)
    while lodict['Jikan']>23:
        lodict['Jikan']=lodict['Jikan']-24
        lodict['nichi']=lodict['nichi']+1
        season(obj)
    keisan(obj)

#スプライト描画
def stokei(obj):
    global sprite
    lodict=obj.GetDict()
    sprite.SetUV(0,0,200,200)
    sprite.SetPos(10,10,210,10,10,210,210,210)
    sprite.SetColor(1,1,1,0.5)
    sprite.SetSprite()
    if lodict['Jikan']<12:
        sprite.SetUV(215,0,250,20)
    else:
        sprite.SetUV(215,23,250,43)
    sprite.SetTranslate(94,40)
    sprite.SetColor(1,1,1,0.4)
    sprite.SetSprite()
    if lodict['lat']>0:
        sprite.SetUV(214,45,248,79)
    else:
        sprite.SetUV(214,80,248,124)
    sprite.SetTranslate(93+math.sin(math.radians(lodict['long']+90))*10*(90-abs(lodict['lat']))/9,93-math.cos(math.radians(lodict['long']+90))*10*(90-abs(lodict['lat']))/9)
    sprite.SetColor(1,1,1,0.5)
    sprite.SetSprite()
    sprite.SetUV(200,115,218,172)
    sprite.SetTranslate(101,62)
    sprite.SetRotate(9,48,lodict['Jikan']*30+lodict['hun']/2+lodict['sec']/120)
    sprite.SetZoom(1,1)
    sprite.SetColor(1,1,1,0.5)
    sprite.SetSprite()
    sprite.SetUV(200,0,212,100)
    sprite.SetTranslate(104,20)
    sprite.SetRotate(6,90,lodict['hun']*6+lodict['sec']/10)
    sprite.SetZoom(1,1)
    sprite.SetColor(1,1,1,0.5)
    sprite.SetSprite()