# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class BilibiliUserPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        cls.MONGO_URL = crawler.settings.get('MONGO_URL')
        cls.MONGO_PORT = crawler.settings.get('MONGO_PORT')
        cls.MONGO_DB_NAME = crawler.settings.get('MONGO_DB_NAME')
        cls.MONGO_COLLECTION_NAME = crawler.settings.get('MONGO_COLLECTION_NAME')
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.MONGO_URL, port=self.MONGO_PORT)
        self.collection = self.client[self.MONGO_DB_NAME][self.MONGO_COLLECTION_NAME]

    def process_item(self, item, spider):
        # 判断信息是否获取完毕
        if item['channels_index'] == len(item['channels']):
            item_info = dict(item)
            # 删除无用的index信息
            item_info.pop('channels_index')
            if self.collection.find_one({'mid': item['mid']}):
                self.collection.update_one({'mid': item['mid']}, item_info)
                print('更新成功,id:{}'.format(item['mid']))
            else:
                self.collection.insert_one(item_info)
                print('插入成功,id:{}'.format(item['mid']))
        return item

    def close_spider(self, spider):
        self.client.close()
