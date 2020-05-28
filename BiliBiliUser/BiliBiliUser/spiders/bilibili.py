# -*- coding: utf-8 -*-
import scrapy
import time
import json
from jsonpath import jsonpath
from BiliBiliUser.items import BilibiliuserItem, ArticleItem, ChannelItem, ArchiveItem, AlbumItem


class BilibiliSpider(scrapy.Spider):
    name = 'bilibili'
    allowed_domains = ['api.bilibili.com', 'api.vc.bilibili.com', 'elec.bilibili.com']

    # start_urls = ['http://https://www.bilibili.com/']

    def get_json_data(self, json_data, json_partten):
        # 提取json数据
        result = jsonpath(json_data, json_partten)
        # 判断是否提取到有效数据
        if result:
            # 若是字符串，则删除多余的空白字符并返回。否则，返回提取到的第一条数据
            if isinstance(result[0], str):
                return result[0].replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '')
            else:
                return result[0]
        else:
            # 若无数据，则返回''
            return ''

    def get_format_time(self, time_str, format_type='%Y-%m-%d %H:%M:%S'):
        # 若有数据，则将unix时间戳格式化为标准时间格式
        if time_str:
            return time.strftime(format_type, time.localtime(int(time_str)))
        else:
            return ''

    def start_requests(self):
        # 重写start_requests方法，遍历若干获取若干用户信息
        for mid in range(0, 600000000):
            # 获取用户粉丝及关注的url
            info_url = 'https://api.bilibili.com/x/space/acc/info?mid={}'.format(mid)
            # 发送请求，获取用户的粉丝及关注信息
            yield scrapy.Request(callback=self.parse, url=info_url)

    def parse(self, response):
        # 将数据转为json格式
        result = json.loads(response.text)
        if result['code'] == 0:
            # 创建item对象
            item = BilibiliuserItem()
            # 获取用户的账号mid,昵称name,性别sex,头像url:face,个签sign,排名rank,等级level
            item['mid'] = self.get_json_data(result, '$..mid')
            item['name'] = self.get_json_data(result, '$..name')
            item['sex'] = self.get_json_data(result, '$..sex')
            item['face'] = self.get_json_data(result, '$..face')
            item['sign'] = self.get_json_data(result, '$..sign')
            item['rank'] = self.get_json_data(result, '$..rank')
            item['level'] = self.get_json_data(result, '$..level')
            # 获取用户粉丝及关注的url
            stat_url = 'https://api.bilibili.com/x/relation/stat?vmid={}'.format(item['mid'])
            # 发送请求，获取用户的粉丝及关注信息
            yield scrapy.Request(callback=self.parse_stat, url=stat_url, meta={'item': item})

    def parse_stat(self, response):
        # 获取item对象
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取用户的粉丝数follower,关注数following
        item['follower'] = self.get_json_data(result, '$..follower')
        item['following'] = self.get_json_data(result, '$..following')
        # 获取用户视频数，专栏数，收藏数的url
        navnum_url = 'https://api.bilibili.com/x/space/navnum?mid={}'.format(item['mid'])
        # 发送请求，获取用户视频数，专栏数，收藏数的信息
        yield scrapy.Request(callback=self.parse_navnum, url=navnum_url, meta={'item': item})

    def parse_navnum(self, response):
        # 获取item对象
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取用户的视频数video，专栏数channel，收藏数favourite
        item['video'] = self.get_json_data(result, '$..video')
        item['channel'] = self.get_json_data(result, '$..channel')
        item['favourite'] = self.get_json_data(result, '$..favourite')
        # 获取用户阅读量信息的url
        upstat_url = 'https://api.bilibili.com/x/space/upstat?mid={}'.format(item['mid'])
        # 发送请求，获取用户阅读量信息
        yield scrapy.Request(callback=self.parse_upstat, url=upstat_url, meta={'item': item})

    def parse_upstat(self, response):
        # 获取item对象
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取用户文章的播放数archive_view,阅读数article_view,喜欢数likes
        item['archive_view'] = self.get_json_data(result, '$..archive.view')
        item['article_view'] = self.get_json_data(result, '$..article.view')
        item['likes'] = self.get_json_data(result, '$..likes')
        # 获取用户文章信息的url
        article_url = 'https://api.bilibili.com/x/space/article?mid={}&pn=1'.format(item['mid'])
        # 发送请求，获取用户文章信息
        yield scrapy.Request(callback=self.parese_article, url=article_url, meta={'item': item})

    def parese_article(self, response):
        # 获取item对象
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # item['articles']类型为list，包含若干文章对象ArticleItem
        item['articles'] = []
        # 获取data并遍历，依次创建文章对象article并添加到item['articles']
        for data in self.get_json_data(result, '$..articles'):
            # 创建文章对象
            article = ArticleItem()
            # 获取文章的id,categories,title,summary,publish_time,stats,tags,words
            article['id'] = self.get_json_data(data, '$.id')
            article['categories'] = self.get_json_data(data, '$.categories')
            article['title'] = self.get_json_data(data, '$.title')
            article['summary'] = self.get_json_data(data, '$.summary')
            article['publish_time'] = self.get_format_time(self.get_json_data(data, '$.publish_time'))
            article['stats'] = self.get_json_data(data, '$.stats')
            article['tags'] = self.get_json_data(data, '$.tags')
            article['words'] = self.get_json_data(data, '$.words')
            # 将文章对象article添加到item的articles中
            item['articles'].append(article)
        # 获取用户专栏信息的url
        channel_url = 'https://api.bilibili.com/x/space/channel/index?mid={}'.format(item['mid'])
        # 发送请求，获取用户专栏信息
        yield scrapy.Request(callback=self.parse_channel, url=channel_url, meta={'item': item})

    def parse_channel(self, response):
        # 获取item
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # item['channels']类型为list，包含若干频道对象ChannelItem
        item['channels'] = []
        item['channels_index'] = 0
        # 获取data并遍历，依次创建频道对象channel并添加到item['channels']
        for index, data in enumerate(self.get_json_data(result, '$.data')):
            # 创建频道对象
            channel = ChannelItem()
            # 获取频道的编号cid,名字name,视频数量count
            channel['cid'] = self.get_json_data(data, '$.cid')
            channel['name'] = self.get_json_data(data, '$.name')
            channel['count'] = self.get_json_data(data, '$.count')
            # channel['archives']类型为list，包含若干视频对象ArchiveItem
            channel['archives'] = []
            # 获取用户该频道的视频的url，默认从第一页开始
            base_url = 'https://api.bilibili.com/x/space/channel/video?mid={}&cid={}&pn=' \
                           .format(item['mid'], channel['cid']) + '{}'
            archives_url = base_url.format(1)
            # 发送请求，获取用户该频道的视频信息
            yield scrapy.Request(url=archives_url, callback=self.parse_archives,
                                 meta={'item': item, 'base_url': base_url, 'channel': channel})
            # 将频道对象channel添加到item的channels中
            item['channels'].append(channel)
        # 相簿的起始页码及每页的数据量
        page_num, page_size = 0, 30
        # 获取用户相簿的url
        base_url = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid={}&page_num={}&page_size={}&biz=all'
        pictures_url = base_url.format(item['mid'], page_num, page_size)
        # 发送请求，获取用户相簿的信息
        yield scrapy.Request(url=pictures_url, callback=self.parse_pictures,
                             meta={'item': item, 'base_url': base_url, 'page_num': page_num, 'page_size': page_size})

    def parse_archives(self, response):
        # 获取item对象
        item = response.meta['item']
        # 获取用户该频道的视频的url，当有下一页时使用
        base_url = response.meta['base_url']
        # 获取频道对象channel
        channel = response.meta['channel']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取当前页信息，当前页码num，每页的数据量size，当前页所拥有的数据量count
        page_info = self.get_json_data(result, '$..page')
        # 获取archives并遍历，依次创建视频对象archive并添加到channel['archives']
        for data in self.get_json_data(result, '$..archives'):
            # 创建视频对象
            archive = ArchiveItem()
            # 获取视频的id,tid,tname,title,pubdate,desc,stat,dynamic
            archive['id'] = self.get_json_data(data, '$.aid')
            archive['tid'] = self.get_json_data(data, '$.tid')
            archive['tname'] = self.get_json_data(data, '$.tname')
            archive['title'] = self.get_json_data(data, '$.title')
            archive['pubdate'] = self.get_format_time(self.get_json_data(data, '$.pubdate'))
            archive['desc'] = self.get_json_data(data, '$.desc')
            archive['stat'] = self.get_json_data(data, '$.stat')
            archive['dynamic'] = self.get_json_data(data, '$.dynamic')
            # 将视频对象archive添加到channel的archives中
            channel['archives'].append(archive)
        # 判断用户该频道是否存在下一页
        if int(page_info['num']) * int(page_info['size']) < int(page_info['count']):
            # 拼接下一页视频信息url
            archives_url = base_url.format(int(page_info['num']) + 1)
            # 发送请求，获取用户该频道的下一页视频信息
            yield scrapy.Request(callback=self.parse_archives, url=archives_url,
                                 meta={'item': item, 'base_url': base_url, 'channel': channel})
        else:
            # 弱不存在，则证明该专栏已获取完毕
            item['channels_index'] += 1
        yield item

    def parse_pictures(self, response):
        # 获取item对象
        item = response.meta['item']
        # 获取用户相簿的url
        base_url = response.meta['base_url']
        # 获取当前相簿页码
        page_num = response.meta['page_num']
        # 获取当前相簿页大小
        page_size = response.meta['page_size']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取albums数据
        datas = self.get_json_data(result, '$..items')
        # item['albums']类型为list，包含若干相册对象AlbumItem
        item['albums'] = []
        # 遍历data，依次创建相册对象album并添加到item['albums']
        for data in datas:
            # 创建相册对象
            album = AlbumItem()
            # 获取相册的doc_id,title,description,pictures,count,ctime,view,like
            album['doc_id'] = self.get_json_data(data, '$.doc_id')
            album['title'] = self.get_json_data(data, '$.title')
            album['description'] = self.get_json_data(data, '$.description')
            album['pictures'] = self.get_json_data(data, '$.pictures')
            album['count'] = self.get_json_data(data, '$.count')
            album['ctime'] = self.get_format_time(self.get_json_data(data, '$.ctime'))
            album['view'] = self.get_json_data(data, '$.view')
            album['like'] = self.get_json_data(data, '$.like')
            # 将相册对象album添加到item的albums中
            item['albums'].append(album)
        # 判断该相册是否存在下一页
        if (int(page_num) + 1) * page_size <= len(datas):
            # 拼接下一页url
            base_url = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid={}&page_num={}&page_size={}&biz=all'
            pictures_url = base_url.format(item['mid'], page_num, page_size)
            # 发送请求，获取用户该相册的下一页信息
            yield scrapy.Request(callback=self.parse_pictures, url=pictures_url,
                                 meta={'item': item, 'base_url': base_url, 'page_num': page_num,
                                       'page_size': page_size})
        # 获取用户的充电信息的url
        charge_url = 'https://elec.bilibili.com/api/query.rank.do?mid={}'.format(item['mid'])
        # # 发送请求，获取用户的充电信息
        yield scrapy.Request(callback=self.parse_charge, url=charge_url, meta={'item': item})

    def parse_charge(self, response):
        # 获取item对象
        item = response.meta['item']
        # 将数据转为json格式
        result = json.loads(response.text)
        # 获取用户的充电信息并添加到item的charge_info中
        # 充电信息：current_time：统计时间，total_count：总充电数，current_month_count：当月充电数
        item['charge_info'] = {
            'current_time': self.get_format_time(time.time()),
            'total_count': self.get_json_data(result, '$..total_count'),
            'current_month_count': self.get_json_data(result, '$..count'),
        }
        # 将item对象交给pipelines
        yield item
