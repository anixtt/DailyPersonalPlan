#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3

# 比较懒 把每个都写了个建表语句

# 插入tag数据
def inserttagintoDB(tagnum, labeltext):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS tags(
      id int(11) PRIMARY KEY UNIQUE NOT NULL,
      tag varchar(20) DEFAULT NULL UNIQUE
    )"""
    )
    c.execute("insert into tags values (?, ?)", [int(tagnum), labeltext])
    conn.commit()
    conn.close()

# 查询tag数据
def gettagdatatfromDB():
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
            """CREATE TABLE IF NOT EXISTS tags(
          id int(11) PRIMARY KEY UNIQUE NOT NULL,
          tag varchar(20) DEFAULT NULL UNIQUE
        )"""
    )
    sql = "SELECT * FROM tags ORDER BY id ASC"
    try:
        # 执行SQL语句
        c.execute(sql)
        # 获取所有记录列表
        results = c.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    conn.close()

# 修改tag数据
def updatetagdatatoDB(id, text):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS tags(
      id int(11) PRIMARY KEY UNIQUE NOT NULL,
      tag varchar(20) DEFAULT NULL UNIQUE
    )"""
    )
    c.execute("UPDATE tags SET tag = ? WHERE id = ?", [text, id])
    conn.commit()
    conn.close()

# 删除tag数据
def deletetagdatatoDB(id):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS tags(
      id int(11) PRIMARY KEY UNIQUE NOT NULL,
      tag varchar(20) DEFAULT NULL UNIQUE
    )"""
    )
    try:
        # 执行SQL语句
        c.execute("DELETE FROM tags WHERE id = ?", [id])
        # 提交修改
        conn.commit()
    except:
        # 发生错误时回滚
        conn.rollback()

    # 关闭连接
    conn.close()

# 插入plan数据
def insertplanintoDB(id, plantext, date, starttime, endtime):
   conn = sqlite3.connect('personalplan.db')
   c = conn.cursor()
   c.execute(
           """CREATE TABLE IF NOT EXISTS p(
         id int NOT NULL PRIMARY KEY UNIQUE ,
         plan varchar(20) DEFAULT NULL,
         plandate text NOT NULL,
         starttime text DEFAULT NULL,
         endtime text DEFAULT NULL,
         planstate text NOT NULL DEFAULT 'unfinished'
       )"""
   )
   c.execute("insert into plan values (?, ?, ?, ?, ?, ?)", [id, plantext,
                                                            date, starttime, endtime, 'unfinished'])
   print "Insert successfully"
   conn.commit()
   conn.close()

# 获取所有plan数据
def getallplandatafromDB():
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS plan(
      id int NOT NULL PRIMARY KEY UNIQUE ,
      plan varchar(20) DEFAULT NULL,
      plandate text NOT NULL,
      starttime text DEFAULT NULL,
      endtime text DEFAULT NULL,
      planstate text NOT NULL DEFAULT 'unfinished'
    )"""
    )
    sql = "SELECT * FROM plan ORDER BY id ASC"
    try:
        # 执行SQL语句
        c.execute(sql)
        # 获取所有记录列表
        results = c.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    conn.close()

# 通过日期获取plan数据
def getplandatafromDBdate(date):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS plan(
      id int NOT NULL PRIMARY KEY UNIQUE ,
      plan varchar(20) DEFAULT NULL,
      plandate text NOT NULL,
      starttime text DEFAULT NULL,
      endtime text DEFAULT NULL,
      planstate text NOT NULL DEFAULT 'unfinished'
    )"""
    )
    try:
        # 执行SQL语句
        c.execute("SELECT * FROM plan WHERE ? = plandate ORDER BY id ASC", [date])
        # 获取所有记录列表
        results = c.fetchall()
        return results
    except:
        print "Error: unable to fecth data"
    conn.close()

# 修改plan数据
def updateplandatatoDB(id, state):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS p(
      id int NOT NULL PRIMARY KEY UNIQUE ,
      plan varchar(20) DEFAULT NULL,
      plandate text NOT NULL,
      starttime text DEFAULT NULL,
      endtime text DEFAULT NULL,
      planstate text NOT NULL DEFAULT 'unfinished'
    )"""
    )
    # SQL 查询语句
    c.execute("UPDATE plan SET planstate = ? WHERE id = ?", [state, id])
    conn.commit()
    conn.close()

# 删除plan数据
def deleteplandatatoDB(id):
    conn = sqlite3.connect('personalplan.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS p(
      id int NOT NULL PRIMARY KEY UNIQUE ,
      plan varchar(20) DEFAULT NULL,
      plandate text NOT NULL,
      starttime text DEFAULT NULL,
      endtime text DEFAULT NULL,
      planstate text NOT NULL DEFAULT 'unfinished'
    )"""
    )
    try:
        # 执行SQL语句
        c.execute("DELETE FROM plan WHERE id = ?", [id])
        # 提交修改
        conn.commit()
    except:
        # 发生错误时回滚
        conn.rollback()

    # 关闭连接
    conn.close()