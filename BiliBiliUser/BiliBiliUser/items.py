# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BilibiliuserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 账号
    mid = scrapy.Field()
    # 昵称
    name = scrapy.Field()
    # 性别
    sex = scrapy.Field()
    # 头像
    face = scrapy.Field()
    # 签名
    sign = scrapy.Field()
    # 排名
    rank = scrapy.Field()
    # 等级
    level = scrapy.Field()
    # 粉丝数
    follower = scrapy.Field()
    # 关注数
    following = scrapy.Field()
    # 视频数
    video = scrapy.Field()
    # 频道数
    channel = scrapy.Field()
    # 收藏数
    favourite = scrapy.Field()
    # 文章数
    article_num = scrapy.Field()
    # 相簿数
    album_info = scrapy.Field()
    # 播放数
    archive_view = scrapy.Field()
    # 阅读数
    article_view = scrapy.Field()
    # 获赞数
    likes = scrapy.Field()
    # 专栏
    articles = scrapy.Field()
    # 频道
    channels = scrapy.Field()
    # 当前爬取的第i个频道
    channels_index = scrapy.Field()
    # 相簿
    albums = scrapy.Field()
    # 总充电数
    charge_info = scrapy.Field()


class ArticleItem(scrapy.Item):
    # 文章id
    id = scrapy.Field()
    # 类别
    categories = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 简介
    summary = scrapy.Field()
    # 发布时间
    publish_time = scrapy.Field()
    # view：浏览量，favorite：收藏量，like：点赞量，reply：回复量，share：分享量，coin：硬币量
    stats = scrapy.Field()
    # 标签
    tags = scrapy.Field()
    # 字数
    words = scrapy.Field()


class ChannelItem(scrapy.Item):
    # 频道id
    cid = scrapy.Field()
    # 名称
    name = scrapy.Field()
    # 视频数量
    count = scrapy.Field()
    # 视频
    archives = scrapy.Field()
    # 视频类型数


class ArchiveItem(scrapy.Item):
    # 视频id
    id = scrapy.Field()
    # 类型id
    tid = scrapy.Field()
    # 类型名
    tname = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 发布时间
    pubdate = scrapy.Field()
    # 描述
    desc = scrapy.Field()
    # view：浏览量，favorite：收藏量，like：点赞量，reply：回复量，share：分享量，coin：硬币量
    stat = scrapy.Field()
    # 标签
    dynamic = scrapy.Field()


class AlbumItem(scrapy.Item):
    # 相册id
    doc_id = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 描述
    description = scrapy.Field()
    # 相册里的图片：img_src：图片url,img_width：图片宽度,img_height：图片高度,img_size：图片大小(单位Kb)
    pictures = scrapy.Field()
    # 图片数量
    count = scrapy.Field()
    # 发布时间
    ctime = scrapy.Field()
    # 浏览量
    view = scrapy.Field()
    # 喜欢数
    like = scrapy.Field()
