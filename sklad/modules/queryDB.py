import pyodbc
import logging
import datetime

class DatabaseConn:
    """Класс для подключения к БД,
        вставки в бд и селекта информации о заказе"""
    # logDirect = configFile.Config().configParser.get('LOGS', "logDirect")
    # serverMain = configFile.Config().configParser.get('DATABASE', "server")
    # usernameMain = configFile.Config().configParser.get('DATABASE', "username")
    # passwordMain = configFile.Config().configParser.get('DATABASE', "password")

    """logging.basicConfig(
        filename=logDirect + datetime.date.today().strftime('%d.%m.%Y') + '.log',
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)"""

    def __init__(self, database, server='localhost', username='serial', password='serial'):
        """Инициализация атрибутов класса"""
        # self.list_km = []
        self.server = server  # 'localhost'  # localhost 192.168.250.100
        self.database = database  # 'marking_db'
        self.username = username  # 'serial'
        self.password = password  # 'serial'

        try:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=' + self.server + ';'
                'DATABASE=' + self.database +
                ';UID=' + self.username + ';PWD=' + self.password)

            self.cursor = conn.cursor()

        except pyodbc.DataError as err:
            print(err)
            logging.error(f'Ошибка подключения к БД {err}')
            print('Ошибка подключения')


    def querySelectFetchone(self, sql, value):
        """     """
        listFetchone = []
        try:
            self.cursor.execute(sql, value)
            row = self.cursor.fetchone()

            while row:
                listFetchone.append(row[0])
                row = self.cursor.fetchone()
            return listFetchone
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}, {err}')

    def querySelectFetchall(self, sql, value):
        """     """
        try:
            self.cursor.execute(sql, value)
            logging.info(f'Выполнен запрос {sql} ({value})')
            listFetchall = self.cursor.fetchall()
            return listFetchall
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}({value}), {err}')

    def queryInsert(self, sql, value):
        """Метод для  пакетной записи в БД"""
        try:
            self.cursor.execute(sql, value)
            self.cursor.commit()
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}, {err}')

    def queryInsertMany(self, sql, value):
        """Метод для  пакетной записи в БД"""
        try:
            self.cursor.executemany(sql, value)
            #print(value)
            self.cursor.commit()
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}, {err}')

    def queryUpdate(self, sql):
        """  """
        try:
            self.cursor.execute(sql)
            self.cursor.commit()
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}, {err}')

    def queryDelete(self, sql, value):
        """Метод для удаления из БД"""
        try:
            self.cursor.execute(sql, value)
            self.cursor.commit()
        except pyodbc.DataError as err:
            logging.error(f'ошибка запроса {sql}, {err}')