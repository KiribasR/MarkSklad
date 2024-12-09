from django.shortcuts import render
from modules import queryDB, ping
import re


def mainPallet(request):
    """Переход на главную страницу паллетирования"""
    data = loadLine()
    print(data)
    return render(request, 'palletizing/mainPallet.html', {'data': data})


def loadLine():
    """Выгрузка списка линий
    и проверка подключения"""

    listDataLines = []
    listLines = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT * FROM serial.Lines', [])
    #Проверка Сетевого статуса линии
    for line in listLines:
        line_ID = line[0]
        line_Name = line[1]
        line_IP = line[2]

        state = ping.ping(line_IP)
        #state = 1
        if state == 1:
            line_Status = 'Доступна'
        else:
            line_Status = 'Недоступна'
        dictLine = {'ID': line_ID,
                    'Name': line_Name,
                    'Status': line_Status}
        listDataLines.append(dictLine)

    return listDataLines


def selectLine(request, arg):
    """Выбор линии для работы"""
    arg_to_dict = splitLine(arg)
    # Получение названия линии
    NameLine = arg_to_dict.get(' Name')
    #Получение ID линии для запроса IP
    IDLine = arg_to_dict.get('ID')
    IPLine = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT IP FROM serial.Lines where ID =?', IDLine)

    # Запрос доступных заданий на выбранной линии
    listOrderOnLine = queryDB.DatabaseConn('client_db', server=IPLine[0]).querySelectFetchone(
        'SELECT batch FROM serial.exchange_files', [])
    return render(request, 'palletizing/orderLine.html', {'NameLine': NameLine, 'Batch': listOrderOnLine})


def splitLine(sting):
    """Перевод параметра кнопки Линии в словарь"""
    arg = re.sub("[{|}|']", "", sting)
    dictionary = dict(subString.split(":") for subString in arg.split(","))
    return dictionary


def startPalleting(request):
    """Подтверждение начала паллета"""
    return render(request, 'palletizing/startPallet.html')
