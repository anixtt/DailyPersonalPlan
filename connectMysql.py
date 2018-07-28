#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 建表语句
# CREATE DATABASE `pp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
# CREATE TABLE `plan` (
#   `id` int(11) NOT NULL,
#   `plan` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
#   `plandate` date NOT NULL,
#   `starttime` time DEFAULT NULL,
#   `endtime` time DEFAULT NULL,
#   `planstate` enum('finished','unfinished') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unfinished',
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `id_UNIQUE` (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
# CREATE TABLE `tags` (
#   `id` int(11) NOT NULL,
#   `tag` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `id_UNIQUE` (`id`),
#   UNIQUE KEY `tip_UNIQUE` (`tag`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



import MySQLdb

# 插入tag数据
def inserttagintoDB(tagnum, labeltext):
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8', use_unicode=True)
    # 之前unicode乱码可能和charset有关 改成utf8mb4
    # 把 zml替换成用户名
    # 把 密码替换成数据库密码
    cursor = db.cursor()
    sql = "insert into tags values ('%d', '%s')" % (int(tagnum), labeltext)
    cursor.execute(sql)
    db.commit()
    db.close()

# 查询tag数据
def gettagdatatfromDB():
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM tags ORDER BY id ASC"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    db.close()

# 修改tag数据
def updatetagdatatoDB(id, text):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "UPDATE tags SET tag = '%s' WHERE id = '%d'" % \
          (text, id)
    cursor.execute(sql)
    db.commit()
    db.close()

# 删除tag数据
def deletetagdatatoDB(id):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "DELETE FROM tags WHERE id = '%d'" % (id)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交修改
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    # 关闭连接
    db.close()

# 插入plan数据
def insertplanintoDB(id, plantext, date, starttime, endtime):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "insert into plan values ('%d', '%s', '%s', '%s', '%s', '%s')" % \
          (id, plantext, date, starttime, endtime, 'unfinished')
    cursor.execute(sql)
    db.commit()
    db.close()

# 获取所有plan数据
def getallplandatafromDB():
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM plan ORDER BY id ASC"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    db.close()

# 通过日期获取plan数据
def getplandatafromDBdate(date):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM plan a WHERE '%s' = a.plandate ORDER BY id ASC" % date
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    db.close()

# 修改plan数据
def updateplandatatoDB(id, state):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "UPDATE plan SET planstate = '%s' WHERE id = '%d'" % \
          (state, id)
    cursor.execute(sql)
    db.commit()
    db.close()

# 删除plan数据
def deleteplandatatoDB(id):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "zml", "zhou6573770", "pp", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    sql = "DELETE FROM plan WHERE id = '%d'" % (id)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交修改
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    # 关闭连接
    db.close()