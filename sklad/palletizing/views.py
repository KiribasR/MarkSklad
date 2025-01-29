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
    listOrderOnLine = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT uuid FROM serial.exchange_palletes where lineID = ?', IDLine)

    # Инкриментирование следующего номера задания для линия
    newTask = split_task_for_incriment(listOrderOnLine, IDLine)

    # Инициализация uid для создания нового задания
    initial_dict = {
        "taskField": newTask,
    }
    form = PalletTaskForm(initial=initial_dict)

    # Переход на страницу с заданиями паллетов
    return render(request, 'palletizing/taskPage.html', {'form': form, 'NameLine': NameLine, 'task': newTask, 'Batch': listOrderOnLine})


def split_task_for_incriment(listTaskInLine, IDLine):
    """Функция определяет последний (максимальный) номер задания и
     инкрементирует следующий номер"""
    listTasks = []
    for task in listTaskInLine:
        task_number = task[-3:]
        listTasks.append(task_number)

    lastNumber = max(listTasks)
    newNumberTask = int(lastNumber) + 1
    newTask = f'P{int(IDLine):02}-{newNumberTask:07}'

    return newTask


def splitLine(sting):
    """Перевод параметра кнопки Линии в словарь"""
    arg = re.sub("[{|}|']", "", sting)
    dictionary = dict(subString.split(":") for subString in arg.split(","))
    return dictionary


def startPalleting(request):
    """Подтверждение начала паллета"""
    return render(request, 'palletizing/startPallet.html')


def addPalletNumber(request):
    """Функция создает новую запись в таблице с заданием на паллет"""
    if request.method == 'POST':
        form = PalletTaskForm(request.POST)
        if form.is_valid():
            print(form)
            curTaskNumber = request.POST['taskField']
            createNewTask(curTaskNumber)
            initial_dict = {
                "taskField": curTaskNumber,
            }
            print(curTaskNumber)
            form = PalletForm(initial=initial_dict)
            #print(f'Это код агрегата - {request.POST["aggregateField"]}')
            #checkFile(curPalletNumber)
            return render(request, 'palletizing/palletNumberForm.html', {'form': form})

    else:
        print(request)

        #createNewTask(arg)
        '''curTaskNumber = request.POST['palletField']
        initial_dict = {
            "pallet": curPalletNumber,
        }'''
        form = PalletForm()

    data = {
        'form': form,
        #'task': arg
    }
    return render(request, 'palletizing/palletNumberForm.html', data)


def newPalletSetting(request):
    """"""
    """Функция создает новую запись в таблице с заданием на паллет"""
    # createNewTask(arg)
    print(PalletForm(request.POST))
    if request.method == 'POST':
        form = AggregateForm(request.POST)
        if form.is_valid():
            #print(form)
            curPalletNumber = request.POST['palletField']
            initial_dict = {
                "pallet": curPalletNumber,

            }
            form = AggregateForm(initial=initial_dict)
            # print(f'Это код агрегата - {request.POST["aggregateField"]}')
            checkFile(curPalletNumber)
            return render(request, 'palletizing/fillingPallet.html', {'form': form, 'curPalletNumber': curPalletNumber})

    else:

        form = AggregateForm()

    data = {
        'form': form,
    }
    return render(request, 'palletizing/palletNumberForm.html', data)


def createNewTask(newTask):
    """Функция проверяет существование записи в БД и создает новую запись"""
    uuid = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT * FROM serial.exchange_palletes where uuid = ?', newTask)
    print(uuid)
    lineID = int(newTask[1:3])
    print(lineID)
    if not len(uuid):
        queryDB.DatabaseConn('marking_db').queryInsert(
            'INSERT INTO serial.exchange_palletes (uuid, status, lineID) VALUES (?,?,?)', (newTask, 0, lineID))


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
    print(request.method)
    #print(pallet)
    if request.method == 'POST':
        form = AggregateForm(request.POST)
        if form.is_valid():
            print(request.POST)
            print(request.POST.get('pallet'))
            print(request.POST.get('aggregateField'))
            curPalletNumber = request.POST.get('pallet')
            curAggregateNumber = request.POST.get('aggregateField')
            initial_dict = {
                "pallet": curPalletNumber,
            }
            form = AggregateForm(initial=initial_dict)

            #Вызов функции проверки и добавления кода агрегата в паллет
            saveAggregate(curAggregateNumber, curPalletNumber)
            #curPalletNumber = request.POST['pallet']
            #print(curPalletNumber)
            #
            #print(f'Это код агрегата - {request.POST["curPalletNumber"]}')
            #checkFile(curAggregateNumber)
            return render(request, 'palletizing/fillingPallet.html', {'form': form})

    else:
        form = AggregateForm()

    data = {
        'form': form,
    }
    return render(request, 'palletizing/fillingPallet.html', data)


def saveAggregate(aggregeteNumber, palletNumber):
    """Функция проверяет файл с переданным в нее номером паллета
        выгружает все аггрегаты в этом файле
        проверяет на дублирование
        добавляет новый аггрегат в файл"""
    print(f'Это код агрегата - {aggregeteNumber}')
    print(f'Это номер паллета - {palletNumber}')
    fileExist = os.path.isfile(f'D:\PythonProject\MarkSklad\sklad\palletFiles\\{palletNumber}.csv')
    print(fileExist)

    if fileExist:
        print(f'файл с номером {palletNumber} существует')
        with open(f'D:\PythonProject\MarkSklad\sklad\palletFiles\\{palletNumber}.csv', 'r') as file:
            listagg = file.readlines()
            if aggregeteNumber in listagg:
                print('Код аггрегата найден в файле')
                pass

            else:
                print('Файл пустой. Записываем код аггрегата')
                chekAggregateCode(aggregeteNumber, palletNumber)
    else:
        print(f'файл с номером {palletNumber} не существует')


def chekAggregateCode(aggregeteNumber, palletNumber):
    """Проверка наличия кода аггрегата в файле"""
    print(f'Это код агрегата - {aggregeteNumber}')
    print(f'Это номер паллета - {palletNumber}')

    #Чтение файла
    with open(f'D:\PythonProject\MarkSklad\sklad\palletFiles\\{palletNumber}.csv', 'a') as f:
        f.write(aggregeteNumber+'\n')

