from sly import Lexer
from sly import Parser


# SQL 词法分析器
class SqlLexer(Lexer):
    # 正则表达式规则

    tokens = {
        # 主关键词
        CREATE, SELECT, SHOW, USE, INSERT,
        # 关键词
        IDENTIFIER, DATABASES, DATABASE, ORDER_BY, WHERE, LIMIT, PRIMARY_KEY, NOT_NULL, NUMBER, OPERATOR, INTO, VALUES,
        JOIN, IN, ON,
        # 逻辑表达符
        DESC, FROM, TABLE, ASC, AND, OR,
        # 类型
        TIMESTAMP, DOUBLE, INT, VARCHAR, DECIMAL, FLOAT,

    }
    literals = {'(', ')', '{', '}', ',', '\'', '*', '.'}

    # SQL 关键字
    PRIMARY_KEY = r'PRIMARY KEY'
    NOT_NULL = r'NOT NULL'
    ORDER_BY = r'ORDER BY'
    # 标识符（数据库名、表名、列名等）
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['DATABASES'] = DATABASES
    IDENTIFIER['VARCHAR'] = VARCHAR
    IDENTIFIER['DECIMAL'] = DECIMAL
    IDENTIFIER['CREATE'] = CREATE
    IDENTIFIER['SELECT'] = SELECT
    IDENTIFIER['INSERT'] = INSERT
    IDENTIFIER['DATABASE'] = DATABASE
    IDENTIFIER['VALUES'] = VALUES
    IDENTIFIER['WHERE'] = WHERE
    IDENTIFIER['LIMIT'] = LIMIT
    IDENTIFIER['FLOAT'] = FLOAT
    IDENTIFIER['DOUBLE'] = DOUBLE
    IDENTIFIER['INTO'] = INTO
    IDENTIFIER['JOIN'] = JOIN
    IDENTIFIER['DESC'] = DESC
    IDENTIFIER['FROM'] = FROM
    IDENTIFIER['TABLE'] = TABLE
    IDENTIFIER['SHOW'] = SHOW
    IDENTIFIER['USE'] = USE
    IDENTIFIER['INT'] = INT
    IDENTIFIER['ASC'] = ASC
    IDENTIFIER['AND'] = AND
    IDENTIFIER['OR'] = OR
    IDENTIFIER['IN'] = IN
    IDENTIFIER['ON'] = ON

    # 常量（数字、字符串）
    NUMBER = r'[0-9]+(\.[0-9]+)?'  # 整数或浮点数

    # 操作符（比较符号和数学运算符）
    OPERATOR = r'(<=|>=|<>|!=|=|<|>|\+|-|/|%)'

    # 忽略空白字符和换行符、行末分号
    ignore = ' ;\t\n'

    # 错误处理：未识别的字符
    def error(self, value):
        print(f"非法字符 '{value.value[0]}'，当前索引位置：{self.index}")
        self.index += 1


# SQL 语法分析器
class SqlParser(Parser):
    tokens = SqlLexer.tokens
    # AND 优先级高于 OR
    precedence = (
        ('left', OR),
        ('left', AND),
    )
    debugfile = 'parser.out'

    def __init__(self, db):
        self.db = db

    # 顶层规则
    @_('create_database')
    def statement(self, p):
        return p.create_database

    @_('create_table')
    def statement(self, p):
        return p.create_table

    @_('show_databases')
    def statement(self, p):
        return p.show_databases

    @_('use_database')
    def statement(self, p):
        return p.use_database

    @_('insert_data')
    def statement(self, p):
        return p.insert_data

    @_('select_data')
    def statement(self, p):
        return p.select_data

    # ****************************************************
    # 使用数据库
    @_('USE IDENTIFIER')
    def use_database(self, p):
        return {
            "type": "use_database",
            "database_name": p.IDENTIFIER
        }

    # ****************************************************
    # 显示数据库
    @_('SHOW DATABASES')
    def show_databases(self, p):
        return {
            "type": "show_databases"
        }

    # ****************************************************
    # 创建数据库表 (文法规约有两个conflict)
    @_('CREATE DATABASE IDENTIFIER')
    def create_database(self, p):
        return {
            "type": "create_database",
            "database_name": p.IDENTIFIER
        }

    # 创建表
    @_('CREATE TABLE IDENTIFIER "(" create_columns ")"')
    def create_table(self, p):
        return {
            "type": "create_table",
            "table_name": p.IDENTIFIER,
            "columns": p.create_columns
        }

    @_('create_column "," create_columns')
    def create_columns(self, p):
        return [p.create_column] + p.create_columns

    @_('create_column')
    def create_columns(self, p):
        return [p.create_column]

    @_('IDENTIFIER data_type constraints')
    def create_column(self, p):
        return {
            "name": p.IDENTIFIER,
            "data_type": p.data_type,
            "constraints": p.constraints
        }

    @_('INT')
    def data_type(self, p):
        return 'int'

    @_('VARCHAR "(" NUMBER ")"')
    def data_type(self, p):
        return f'varchar({p.NUMBER})'

    @_('DECIMAL "(" NUMBER "," NUMBER ")"')
    def data_type(self, p):
        return f'DECIMAL({p[2]}, {p[4]})'

    # 处理多个约束
    @_('constraint constraints')
    def constraints(self, p):
        return [p.constraint] + p.constraints  # 收集多个约束

    @_('constraint')
    def constraints(self, p):
        return [p.constraint]  # 单个约束

    @_('')  # 空处理
    def constraints(self, p):
        return []  # 返回空约束列表

    @_('PRIMARY_KEY')
    def constraint(self, p):
        return 'primary key'  # 返回单个约束

    @_('NOT_NULL')
    def constraint(self, p):
        return 'not null'  # 返回单个约束

    # ****************************************************
    # insert数据
    @_('INSERT INTO IDENTIFIER "(" data_columns ")" insert_clause')
    def insert_data(self, p):
        return {
            "type": "insert_data",
            "table_name": p.IDENTIFIER,
            "columns": p.data_columns,
            "insert_clause": p.insert_clause
        }

    @_('SELECT select_data')
    def insert_clause(self, p):
        return {
            "insert_type": p.SELECT,
            "values": p.select_data
        }

    @_('VALUES values_clause')
    def insert_clause(self, p):
        return {
            "insert_type": "values",
            "values": p.values_clause
        }

    @_('"(" datas ")" "," values_clause')
    def values_clause(self, p):
        return [p.datas] + p.values_clause

    @_('"(" datas ")"')
    def values_clause(self, p):
        return [p.datas]

    @_('datas "," data')
    def datas(self, p):
        return p.datas + [p.data]

    @_('data')
    def datas(self, p):
        return [p.data]

    @_('NUMBER')
    def data(self, p):
        return p.NUMBER

    @_('"\'" IDENTIFIER "\'"')
    def data(self, p):
        return p.IDENTIFIER

    # ****************************************************
    # select数据
    @_('select_all')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.select_all,
        }

    @_('simple_select')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.simple_select,
        }

    @_('conditional_select')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.conditional_select,
        }

    @_('ordered_select')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.ordered_select,
        }

    @_('join_select')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.join_select,
        }

    @_('subquery_select')
    def select_data(self, p):
        return {
            "type": "select_data",
            "select_info": p.subquery_select,
        }

    @_('SELECT "*" FROM IDENTIFIER')
    def select_all(self, p):
        return {
            "select_type": "select_all",
            "table_name": p.IDENTIFIER,
            "columns": ["*"]
        }

    @_('SELECT data_columns FROM IDENTIFIER')
    def simple_select(self, p):
        return {
            "select_type": "simple_select",
            "table_name": p.IDENTIFIER,
            "columns": p.data_columns
        }

    @_('SELECT data_columns FROM IDENTIFIER WHERE conditions')
    def conditional_select(self, p):
        return {
            "select_type": "conditional_select",
            "table_name": p.IDENTIFIER,
            "columns": p.data_columns,
            "conditions": p.conditions
        }

    @_('SELECT data_columns FROM IDENTIFIER ORDER_BY order_columns')
    def ordered_select(self, p):
        return {
            "table_name": p.IDENTIFIER,
            "select_type": "ordered_select",
            "columns": p.data_columns,
            "order_by": p.order_columns,
        }

    @_('IDENTIFIER ASC')
    def order_columns(self, p):
        return {
            "column": p.IDENTIFIER,
            "direction": "ASC"
        }

    @_('IDENTIFIER DESC')
    def order_columns(self, p):
        return {
            "column": p.IDENTIFIER,
            "direction": "DESC"
        }

    @_('SELECT data_columns FROM table_with_alias join_clause')
    def join_select(self, p):
        return {
            "table_name": p.table_with_alias,
            "select_type": "join_select",
            "columns": p.data_columns,
            "join": p.join_clause,
        }

    @_('SELECT data_columns FROM IDENTIFIER WHERE IDENTIFIER IN "(" select_data ")"')
    def subquery_select(self, p):
        return {
            "table_name": p[3],
            "select_type": "subquery_select",
            "columns": p.data_columns,
            "conditions": {
                "column": p[5],
                "operator": 'IN',
                "subquery": {
                    p.select_data
                }
            }
        }

    @_('data_column data_columns')
    def data_columns(self, p):
        return [p.data_column] + p.data_columns

    @_('')
    def data_columns(self, p):
        return []

    @_('IDENTIFIER ","')
    def data_column(self, p):
        return p.IDENTIFIER

    @_('IDENTIFIER')
    def data_column(self, p):
        return p.IDENTIFIER

    @_('condition conditions')
    def conditions(self, p):
        # return [p.condition] + p.conditions
        return (p.condition, p.conditions)

    @_('')
    def conditions(self, p):
        return []

    @_('condition AND condition_clause')
    @_('condition OR condition_clause')
    def condition(self, p):
        # "relation": p[1],  # p[1] 是 AND 或 OR
        # "content": [p.condition] + [p.condition_clause]
        return (p[1], p.condition, p.condition_clause)

    @_('condition_clause')
    def condition(self, p):
        # return [p.condition_clause]
        return p.condition_clause

    @_('IDENTIFIER OPERATOR value')
    def condition_clause(self, p):
        return {
            "column": p.IDENTIFIER,
            "operator": p.OPERATOR,
            "value": p.value
        }

    @_('IDENTIFIER "." IDENTIFIER OPERATOR IDENTIFIER "." IDENTIFIER')
    def condition_clause(self, p):
        return {
            "column": f"{p[0]}.{p[2]}",
            "operator": p.OPERATOR,
            "value": f"{p[4]}.{p[6]}"
        }

    @_('IDENTIFIER')
    def value(self, p):
        return p.IDENTIFIER

    @_('NUMBER')
    def value(self, p):
        return p.NUMBER

    @_('"\'" IDENTIFIER "\'"')
    def value(self, p):
        return p.IDENTIFIER

    @_('JOIN table_with_alias ON condition')
    def join_clause(self, p):
        return {
            "table_with_alias": p.table_with_alias,
            "on": p.condition
        }

    @_('IDENTIFIER IDENTIFIER')
    def table_with_alias(self, p):
        return p.IDENTIFIER + p.IDENTIFIER

    @_('IDENTIFIER')
    def table_with_alias(self, p):
        return p.IDENTIFIER
