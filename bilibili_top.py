import time
import requests
import json
import jsonpath
# import datetime
import pymongo
from queue import Queue, Empty
import threading


class BibiliItem(object):
    # 种类:rid
    # rid1:全站 动画 国创相关 音乐 舞蹈 游戏 科技 数码 生活 鬼畜 时尚 娱乐 影视,rid2:番剧 国产动画 纪录片 电影 电视剧
    rid = ''
    # 排名URL
    rank_url = ''
    # 榜单类型:type_
    # type1:全站榜 原创榜 新人榜,type2:新番榜 影视榜
    type_ = ''
    # 排名:rank
    rank = ''
    # 标题:title
    title = ''
    # 播放量:play
    play = ''
    # 投币数:coins
    coins = ''
    # 重新播放数:video_review
    video_review = ''
    # 作者昵称:author
    author_name = ''
    # 作者url:'https://space.bilibili.com/{}'.format(mid)
    author_url = ''
    # 视频url:'https://www.bilibili.com/video/av{}/'.format(aid)
    video_url = ''


class BiliBiliTop(object):
    def __init__(self):
        # 链接mongodb，获取操作集合的对象
        self.client = pymongo.MongoClient(host='mongodb://127.0.0.1', port=27017)
        self.collection = self.client['bilibili']['top']
        # 创建队列
        self.queue = Queue()
        # 线程锁
        self.lock = threading.RLock()
        # 线程数
        self.thread_num = 8
        # 线程列表
        self.thread_list = []
        # 保存信息的数量
        self.count = 0
        self.type1_dict = {
            '1': '全站榜',
            '2': '原创榜',
            '3': '新人榜',
        }
        self.rid1_dict = {
            '0': '全站',
            '1': '动画',
            '3': '音乐',
            '4': '游戏',
            '5': '娱乐',
            '36': '科技',
            '119': '鬼畜',
            '129': '舞蹈',
            '155': '时尚',
            '160': '生活',
            '168': '国创相关',
            '181': '影视',
            '188': '数码',
        }
        self.type2_dict = {
            '1': '新番榜',
            '4': '新番榜',
            '2': '影视榜',
            '3': '影视榜',
            '5': '影视榜',
        }
        self.rid2_dict = {
            '1': '番剧',
            '2': '电影',
            '3': '纪录片',
            '4': '国产动画',
            '5': '电视剧',
        }

    def save_item(self, item):
        # 若存在，则修改。若不存在，则插入
        filter = {
            'type_': item.type_,
            'rid': item.rid,
            'video_url': item.video_url,
        }
        if self.collection.find_one(filter):
            self.collection.update_one(filter, {'$set': item.__dict__})
        else:
            self.collection.insert_one(item.__dict__)
            self.count += 1
            print('已保存第{}条记录:{}'.format(self.count, item.__dict__))

    def get_rank(self):
        with self.lock:
            while not self.queue.empty():
                headers = {
                    'User-Agent': requests.get('http://127.0.0.1:8888/headers').text,
                    'Referer': 'https://www.bilibili.com/'
                }
                # 从队列中取出url信息
                url_info = self.queue.get()
                # 发送请求
                response = requests.get(url=url_info['url'], headers=headers)
                # 加载json格式数据
                data = json.loads(response.text)
                data_list = jsonpath.jsonpath(data, '$..list')
                data_list = data_list[0] if data_list else ''
                for index, item in enumerate(data_list):
                    # 创建item对象
                    bilibili = BibiliItem()
                    bilibili.type_ = url_info['type_']
                    bilibili.rid = url_info['rid']
                    bilibili.rank_url = url_info['url']
                    # 下标则为排名
                    bilibili.rank = index + 1
                    bilibili.title = item['title']
                    bilibili.coins = item['coins'] if 'coins' in item else '0'
                    bilibili.video_review = item['video_review'] if 'video_review' in item else '0'
                    if 'play' in item:
                        bilibili.play = item['play']
                    else:
                        bilibili.play = item['stat']['view']
                    if 'author' in item:
                        bilibili.author_name = item['author']
                        bilibili.author_url = 'https://space.bilibili.com/{}'.format(item['mid'])
                    else:
                        bilibili.author_name = '大会员抢先看'
                        bilibili.author_url = ''
                    if 'aid' in item:
                        bilibili.video_url = 'https://www.bilibili.com/video/av{}/'.format(item['aid'])
                    else:
                        bilibili.video_url = item['url']
                    self.save_item(bilibili)
            self.thread_list.remove(threading.current_thread())
            self.queue.task_done()

    def get_urls_info(self):
        # 获取当前星期几
        # day = datetime.datetime.now().weekday() + 1
        day = 3
        for type_key in self.type1_dict.keys():
            for rid_key in self.rid1_dict.keys():
                # https://api.bilibili.com/x/web-interface/ranking?rid=1&day=3&type=1
                # type_: 全站榜 原创榜 新人榜
                # rid:全站 动画 国创相关 音乐 舞蹈 游戏 科技 数码 生活 鬼畜 时尚 娱乐 影视
                # day:未知
                base_url = 'https://api.bilibili.com/x/web-interface/ranking?rid={}&day={}&type={}'
                url_dict = {
                    'type_': self.type1_dict[type_key],
                    'rid': self.rid1_dict[rid_key],
                    'url': base_url.format(rid_key, day, type_key),
                }
                self.queue.put_nowait(url_dict)
        for rid_key in self.rid2_dict.keys():
            # https://api.bilibili.com/pgc/web/rank/list?day={}&season_type={1,2,3,4,5}
            # type_:番剧 国产动画 纪录片 电影 电视剧
            # day:星期x
            base_url = 'https://api.bilibili.com/pgc/web/rank/list?day={}&season_type={}'
            url_dict = {
                'type_': self.type2_dict[rid_key],
                'rid': self.rid2_dict[rid_key],
                'url': base_url.format(day, rid_key),
            }
            self.queue.put_nowait(url_dict)

    def run(self):
        start_time = time.time()
        # 获取所有url
        self.get_urls_info()
        print('已获取{}个url'.format(self.queue.qsize()))
        # 创建若干线程
        for i in range(self.thread_num):
            thread = threading.Thread(target=self.get_rank)
            thread.start()
            self.thread_list.append(thread)
        # 创建阻塞
        for thread in self.thread_list:
            thread.join()
        while True:
            # 若子线程均执行完毕
            if len(self.thread_list) == 0:
                self.client.close()
                print('耗时：{:.2f}s,共保存{}条记录'.format(time.time() - start_time, self.count))
                break

    def __del__(self):
        self.client.close()


if __name__ == '__main__':
    top = BiliBiliTop()
    top.run()
