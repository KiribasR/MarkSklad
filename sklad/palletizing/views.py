import os.path

from django.shortcuts import render
from modules import queryDB, ping
import re
from .forms import *


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
    print (listLines)
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


def addPalletNumber(request):
    """"""
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            print(request.POST)
            form = AggregateForm()
            curPalletNumber = request.POST['palletField']
            #print(f'Это код агрегата - {request.POST["aggregateField"]}')
            checkFile(curPalletNumber)
            return render(request, 'palletizing/fillingPallet.html', {'form': form, 'curPalletNumber': curPalletNumber})

    else:
        form = PalletForm()

    data = {
        'form': form,
    }
    return render(request, 'palletizing/palletNumberForm.html', data)


def checkFile(curPalletNumber):
    """Проверка существоания файла"""
    print(curPalletNumber)
    fileExist = os.path.isfile('D:\PythonProject\MarkSklad\sklad\palletFiles' + curPalletNumber)
    if fileExist:
        print('файл существует')
        pass
    else:
        createPalletFile(curPalletNumber)
        print('файл не существует')


def createPalletFile(curPalletNumber):
    """Создание нового файла паллета"""
    newFile = open(f'D:\PythonProject\MarkSklad\sklad\palletFiles\\{curPalletNumber}.csv', 'w')
    #newFile.write('номер паллета,номер маркировки, марка, дата паллетирования\n')
    newFile.close


def addAggregateNumber(request):
    """Добавление кода аггрегата"""
    if request.method == 'POST':
        form = AggregateForm(request.POST)
        if form.is_valid():
            print(request.POST)
            form = AggregateForm()
            curAggregateNumber = request.POST['aggregateField']
            #print(f'Это код агрегата - {request.POST["aggregateField"]}')
            #checkFile(curAggregateNumber)
            return render(request, 'palletizing/fillingPallet.html', {'form': form})

    else:
        form = AggregateForm()

    data = {
        'form': form,
    }
    return render(request, 'palletizing/fillingPallet.html', data)
