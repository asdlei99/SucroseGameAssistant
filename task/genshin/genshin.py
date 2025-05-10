from .main import *
from ..default_task import Task


class Genshin(Task):
    def __init__(self):
        super().__init__()
    
    def tp_fontaine1(self):
        self.home()
        self.indicate("前往枫丹:\n  枫丹廷凯瑟琳锚点")
        self.open_sub("地图")
        click((1839,1012)) #点击区域选择
        wait(500)
        click_text("枫丹",(1293,83,1890,611)) #点击枫丹
        wait(500)
        click((959,539)) #点击传送点
        wait(1000)
        self.tp_point()
        self.indicate("到达枫丹:\n  枫丹廷凯瑟琳锚点")
        
    # 打开esc主界面
    def home(self):
        m = 0
        while m >= 0:
            m += 1
            wait(1500)
            if "好友" in ocr((480, 442, 540, 481))[0]:
                m = -1
            else:
                press("esc")
            if m == 15:
                self.indicate("error:打开主界面超时\n")
                raise RuntimeError("原神:打开主界面超时")

    #检查游戏是否登录成功
    def world(self):
        i = 1
        while i > 0:
            i += 1
            wait(1000)
            pos, val = find_pic(r"assets\genshin\picture\world.png", (25, 998, 179, 1075))
            if val >= 0.6:
                i = 0
                self.indicate("已加载到世界")
            elif i == 90:
                self.indicate("error:加载世界超时\n")
                raise RuntimeError("原神:加载世界超时")

    # 从主界面打开子界面
    def open_sub(self, cho):
        if click_text(cho, (117, 346, 742, 1052)):
            self.indicate("打开" + cho)
            wait(2500)
            return True
        else:
            return False

    # 从秘境传送
    def tp_domain(self, domain):
        self.indicate("尝试传送到秘境:\n  " + domain)
        pos = wait_text("冒险之证", (117, 346, 742, 1052))
        pos = clickto(pos, 2500, ("秘境", (256, 416, 345, 469), 0))
        click((301, 442))
        wait(800)
        m = ["圣遗物", "武器突破素材", "天赋培养素材"]
        n = m.index(self.task["秘境"][0])
        click((555,n*100+230))
        wait(800)
        if domain == "椛染之庭":
            _t = "染之庭"
        elif domain == "菫色之庭":
            _t = "色之庭"
        elif domain == "无妄引咎密宫":
            _t = "无妄引"
        elif domain == "华池岩岫":
            _t = "华池"
        elif domain == "褪色的剧场":
            _t = "色的剧场"
        else:
            _t = domain
        for num in range(18):
            wait(300)
            _list = ocr((764, 243, 1058, 847), mode=1)
            if res := find_text(_t, (764, 243, 1058, 847)):
                wait(800)
                clickto((1555, res[1] + 40), 2000, ("传送", (1641, 980, 1749, 1034), 0))
                return True
            if num <= 16:
                roll((1116, 296), -24)
            else:
                self.indicate("error:\n  未识别到秘境 " + domain)
                raise RuntimeError("原神:秘境识别异常")

    # 选择确认传送锚点图标并开始传送，最后判断传送成功
    def tp_point(self, num=0):
        if "传送" in ocr((1638, 983, 1749, 1035))[0]:
            pass
        else:

            _p, val = find_pic(r"assets\genshin\picture\maps\%s.png" % num, (1270, 649, 1327, 961))
            if val >= 0.75:
                clickto(_p, 800, ("传送", (1641, 980, 1749, 1034), 0))
            else:
                raise RuntimeError("原神:传送识别异常")
        clickto((1634, 1003), 3000, (r"assets\genshin\picture\world.png", (57, 998, 179, 1075), 0.7))

    def check_overdue(self):
        if "物品过期" == ocr((869, 269, 1057, 333))[0]:
            self.indicate("识别到物品过期")
            click((971, 758))
            wait(2000)

    def isonline(self):
        t0 = ocr((1289, 993, 1428, 1046))[0]
        if "编队" not in t0:
            return False
        else:
            return True

    #退出ESC菜单
    def turn_world(self):
        m = 0
        while m >= 0:
            m += 1
            pos, val = find_pic(r"assets\genshin\picture\world.png", (25, 998, 179, 1075))
            if val >= 0.6:
                m = -1
            else:
                press("esc")
                wait(1500)
            if m == 15:
                self.indicate("error:打开主界面超时\n")
                raise RuntimeError("原神:打开主界面超时")
            
    #切换到第n支队伍
    def team_change_to(self,n):
        self.home()
        self.open_sub("队伍配置")
        if not self.isonline():
            self.indicate("处于联机/尘歌壶模式,更换队伍前进行状态初始化")
            self.tp_fontaine1()
            self.open_sub("队伍配置")
            if self.isonline():
                raise RuntimeError("处于联机模式,请退出联机后再试")
        clickto((77, 1016), 800, ("管理队伍", (27, 17, 170, 75), 0))
        roll((580, 224), 80)
        wait(500)
        if "出战" in ocr((559, 180*n-15, 657, 90+180*n))[0]:
            self.turn_world()
            press("1")
            wait(300)
            return True
        click((559, 180*n+30))
        wait(300)
        click((328, 1016))
        wait(500)
        click_change((1557, 1020), (1650, 997, 1746, 1042))
        self.turn_world()
        press("1")
        wait(300)
        press("1")
        wait(300)
