# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
import codecs
import MySQLdb
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter


class WallpapercrawlerPipeline:
    def process_item(self, item, spider):
        return item


class WallpaperImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "image_url" in item:
            image_path = ""
            for ok, value in results:
                image_path = value['path']
            item['image_path'] = image_path
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
            insert into wallpaper_bh3(image_name, image_url, image_path, image_id)
            values (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE image_name=VALUES(image_name)
        """
        params = list()
        params.append(item.get('image_name', ""))
        params.append(",".join(item.get('image_url', [])))
        params.append(item.get('image_path', ""))
        params.append(item.get('image_id', ""))

        cursor.execute(insert_sql, tuple(params))
