from sly import Lexer
from sly import Parser
from .executor import *


# SQL 词法分析器
class SqlLexer(Lexer):
    # 正则表达式规则

    tokens = {
        # 主关键词
        CREATE, SELECT, SHOW, USE,
        # 关键词
        IDENTIFIER, DATABASES, DATABASE, ORDER, WHERE, LIMIT, PRIMARY_KEY, NOT_NULL, NUMBER, OPERATOR,
        # 逻辑表达符
        DESC, FROM, TABLE, ASC, AND, OR,
        # 类型
        TIMESTAMP, DOUBLE, INT, VARCHAR, DECIMAL, FLOAT,

    }
    literals = {'(', ')', '{', '}', ',', '\''}

    # SQL 关键字
    PRIMARY_KEY = r'PRIMARY KEY'
    NOT_NULL = r'NOT NULL'
    # 标识符（数据库名、表名、列名等）
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['DATABASES'] = DATABASES
    IDENTIFIER['VARCHAR'] = VARCHAR
    IDENTIFIER['DECIMAL'] = DECIMAL
    IDENTIFIER['CREATE'] = CREATE
    IDENTIFIER['SELECT'] = SELECT
    IDENTIFIER['DATABASE'] = DATABASE
    IDENTIFIER['ORDER'] = ORDER
    IDENTIFIER['WHERE'] = WHERE
    IDENTIFIER['LIMIT'] = LIMIT
    IDENTIFIER['FLOAT'] = FLOAT
    IDENTIFIER['DOUBLE'] = DOUBLE
    IDENTIFIER['DESC'] = DESC
    IDENTIFIER['FROM'] = FROM
    IDENTIFIER['TABLE'] = TABLE
    IDENTIFIER['SHOW'] = SHOW
    IDENTIFIER['USE'] = USE
    IDENTIFIER['INT'] = INT
    IDENTIFIER['ASC'] = ASC
    IDENTIFIER['AND'] = AND
    IDENTIFIER['OR'] = OR

    # 常量（数字、字符串）
    NUMBER = r'[0-9]+(\.[0-9]+)?'  # 整数或浮点数

    # 操作符（比较符号和数学运算符）
    OPERATOR = r'(<=|>=|<>|!=|=|<|>|\+|-|\*|/|%)'

    # 忽略空白字符和换行符、行末分号
    ignore = ' ;\t\n'

    # 错误处理：未识别的字符
    def error(self, value):
        print(f"非法字符 '{value.value[0]}'，当前索引位置：{self.index}")
        self.index += 1


# SQL 语法分析器
class SqlUseParser(Parser):
    tokens = SqlLexer.tokens

    def __init__(self, db):
        self.db = db

    # 使用数据库
    @_('USE IDENTIFIER')
    def use_database(self, p):
        return {
            "type": "use_database",
            "database_name": p.IDENTIFIER
        }

    # 创建数据库


class SqlCreateParser(Parser):
    tokens = SqlLexer.tokens

    def __init__(self, db):
        self.db = db

    # 使用数据库
    @_('CREATE DATABASE IDENTIFIER')
    def create_database(self, p):
        return {
            "type": "create_database",
            "database_name": p.IDENTIFIER
        }



class SqlShowParser(Parser):
    tokens = SqlLexer.tokens

    def __init__(self, db):
        self.db = db

    # 显示数据库
    @_('SHOW DATABASES')
    def show_databases(self, p):
        return {
            "type": "show_databases"
        }
