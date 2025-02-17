import os.path

from django.shortcuts import render, HttpResponseRedirect
from modules import queryDB, ping
import re
from .forms import *
import json
from django.contrib import messages

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

    dictOrder = {}
    # Запрос доступных заданий на выбранной линии
    listOrderOnLine = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT uuid FROM serial.exchange_palletes where lineID = ?', IDLine)
    
    for line in listOrderOnLine:
        name = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
            'SELECT name FROM serial.product where gtin = (select top(1) gtin from serial.group_codes where uuid_pallet = ?)', line)
        dictOrder[line] = name
    
    # Инкриментирование следующего номера задания для линия
    newTask = split_task_for_incriment(listOrderOnLine, IDLine)

    # Инициализация uid для создания нового задания
    initial_dict = {
        "taskField": newTask,
    }
    form = PalletTaskForm(initial=initial_dict)

    # Переход на страницу с заданиями паллетов
    return render(request, 'palletizing/taskPage.html', {'form': form,
                                                         'NameLine': NameLine,
                                                         'task': newTask,
                                                         'Batch': dictOrder})


def split_task_for_incriment(listTaskInLine, IDLine):
    """Функция определяет последний (максимальный) номер задания и
     инкрементирует следующий номер"""
    listTasks = []
    for task in listTaskInLine:
        task_number = task[-3:]
        listTasks.append(task_number)
    if len(listTasks):
        lastNumber = max(listTasks)
    else:
        lastNumber = 0

    newNumberTask = int(lastNumber) + 1
    newTask = f'P{int(IDLine):02}-{newNumberTask:07}'

    return newTask


def splitLine(sting):
    """Перевод параметра кнопки Линии в словарь"""
    arg = re.sub("[{|}|']", "", sting)
    dictionary = dict(subString.split(":") for subString in arg.split(","))
    return dictionary


def startPalleting(request, batch):
    """Подтверждение начала паллета"""
    print(batch)

    #curPalletNumber = request.POST['palletField']
    curTaskNumber = batch
    initial_dict = {
        "taskField": curTaskNumber
    }
    form = PalletForm(initial=initial_dict)

    return render(request, 'palletizing/startPallet.html', {'form': form})


def addPalletNumber(request):
    """Функция создает новую запись в таблице с заданием на паллет"""
    if request.method == 'POST':
        form = PalletTaskForm(request.POST)
        if form.is_valid():
            curTaskNumber = request.POST['taskField']
            createNewTask(curTaskNumber)

            initial_dict = {
                "taskField": curTaskNumber,
            }
            print(curTaskNumber)
            form = PalletForm(initial=initial_dict)
            #print(f'Это код агрегата - {request.POST["aggregateField"]}')
            checkFile(curTaskNumber)  # проверка файла с номером задания
            return render(request, 'palletizing/palletNumberForm.html', {'form': form})

    else:
        form = PalletForm()

    data = {
        'form': form,
        #'task': arg
    }
    return render(request, 'palletizing/palletNumberForm.html', data)


def newPalletSetting(request):
    """Функция создает новую запись в файле с паллетом
    переход на страницу сканирования агрегатов"""
    if 'confirm' in request.POST:
        print('Начинаем новый паллет')
        if request.method == 'POST':
            form = PalletForm(request.POST)
            if form.is_valid():
                curPalletNumber = request.POST['palletField']
                curTaskNumber = request.POST['taskField']

                # Проверяем паллет на соотвествие условиям
                # Палет должен быть новым или не завершенным.
                # Палет должен принадлежать заданию
                resolutionStatus = checkNewPalletCode(curPalletNumber, curTaskNumber)
                print(resolutionStatus)

                if resolutionStatus['resolution']:
                    initial_dict = {
                        "pallet": curPalletNumber,
                        "task": curTaskNumber
                    }
                    form = AggregateForm(initial=initial_dict)
                    createNewPallet(curTaskNumber, curPalletNumber)
                    listAggCode = loadCodeInPallet(curPalletNumber, curTaskNumber)
                    counter = len(set(listAggCode))
                    listAggCode = loadCodeInPallet(curPalletNumber, curTaskNumber)
                    counter = len(set(listAggCode))
                    # Update status pallet
                    upadteStatusTask(curTaskNumber, 2)
                    # Update status pallet
                    updateStatusPallet(curTaskNumber, curPalletNumber, 2)

                    messages.success(request, f'{resolutionStatus["msg"]}')

                    return render(request, 'palletizing/fillingPallet.html', {'form': form, 'code': listAggCode, 'counter': counter})
                else:
                    initial_dict = {
                        "taskField": curTaskNumber
                    }
                    form = PalletForm(initial=initial_dict)
                    messages.error(request, f'{resolutionStatus["msg"]}')
                    return render(request, 'palletizing/palletNumberForm.html', {'form': form})
    elif 'complete' in request.POST:
        print('завершаем задание')
        if request.method == 'POST':
            curTaskNumber = request.POST['taskField']
            queryDB.DatabaseConn('marking_db').queryUpdate(
                'UPDATE serial.exchange_palletes SET status=? WHERE uuid =?', (2, curTaskNumber))

            return render(request, 'tsd/index.html')


def upadteStatusTask(curTaskNumber, status):
    """При сканировании кода паллета меняется статус задания
    'в работе' """
    queryDB.DatabaseConn('marking_db').queryUpdate(
        'UPDATE serial.exchange_palletes SET status=? WHERE uuid =?', (status, curTaskNumber))


def checkNewPalletCode(newPalletCode, curTaskNumber):
    """Проверка статуса кода палета"""
    resolutionDict = {'resolution': False, 'msg': ''}
    print()
    statusPalletCode = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT status, task FROM serial.pallet_codes where code = ?', newPalletCode)
    print(statusPalletCode)
    try:
        taskInDB = statusPalletCode[0][1]
        statusPallet = statusPalletCode[0][0]
        #print(statusPalletCode[0])
        if taskInDB == curTaskNumber or taskInDB == None:
            if len(statusPalletCode):
                if int(statusPallet) <= 2:
                    resolutionPallet = True
                    message = f'Код паллета валиден'
                else:
                    resolutionPallet = False
                    message = f'Код паллета уже завершен'
            else:
                resolutionPallet = False
                message = f'Код паллета не найден. Проверте правильность кода'
        else:
            resolutionPallet = False
            message = f'Код паллета принадлежит другому заданию'
        resolutionDict['resolution'] = resolutionPallet
        resolutionDict['msg'] = message
        return resolutionDict
    except Exception as err:
        print(f'Ошибка при проверке статуса кода паллета: {err}')
        message = f'Ошибка при проверке статуса кода паллета: {err}'
        resolutionDict['msg'] = message
        return resolutionDict


def createNewPallet(curTaskNumber, newPalletNumber):
    """ Create new pallet number in file"""
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')

    with open(joined_path, 'r') as file:
        jsonFile = file.read()

    if len(jsonFile):
        dictFile = json.loads(jsonFile)
        print(dictFile)
        if newPalletNumber in dictFile:
            #dictFile[newPalletNumber] = []
            print(dictFile[newPalletNumber])
        else:
            dictFile[newPalletNumber] = []
        with open(joined_path, 'w') as file:
        if newPalletNumber in dictFile:
            #dictFile[newPalletNumber] = []
            print(dictFile[newPalletNumber])
        else:
            dictFile[newPalletNumber] = []
        with open(joined_path, 'w') as file:
            json.dump(dictFile, file)
    else:
        with open(joined_path, 'w') as file:
        with open(joined_path, 'w') as file:
            json.dump({newPalletNumber: []}, file)


def updateStatusPallet(TaskNumber, palletNumber, status):
    """Функция при сканирование кода паллета меняет статус
    - 2 = в работе
    - 3 = завершен """
    # Меняем статус паллета на "в работе"
    if status == 2:
        try:
            queryDB.DatabaseConn('marking_db').queryUpdate(
                'UPDATE serial.pallet_codes SET status=?, task=? WHERE code =?', (2, TaskNumber, palletNumber))
        except Exception as err:
            print(f'Ошибка при изменении статуса паллета: {err}')
    else:
        # Меняем статус взятия паллета на "завершен"
        queryDB.DatabaseConn('marking_db').queryUpdate(
            'UPDATE serial.pallet_codes SET status =? WHERE code =?', (3, palletNumber))


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


def checkFile(curTaskNumber):
    """Проверка существоания файла"""
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    print(f'получен новый номер задания: {curTaskNumber}')
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    fileExist = os.path.isfile(joined_path)
    if fileExist:
        print('файл существует')
        pass
    else:
        createPalletFile(curTaskNumber)
        print('файл не существует')


def createPalletFile(curTaskNumber):
    """Создание нового файла паллета"""
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    newFile = open(joined_path, 'w')
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    newFile = open(joined_path, 'w')
    #newFile.write('номер паллета,номер маркировки, марка, дата паллетирования\n')
    newFile.close()
    newFile.close()


def addAggregateNumber(request):
    """Добавление кода аггрегата в файл
    прикрепление кода агрегата к паллету в БД"""
    print(request.POST)
    if 'complete' in request.POST:
        print('Завершаем')
        if request.method == 'POST':
            curTaskNumber = request.POST['task']
            createNewTask(curTaskNumber)
            curPalletNumber = request.POST['pallet']
            initial_dict = {
                "taskField": curTaskNumber,
                "curPallet": curPalletNumber
            }
            print(curTaskNumber)
            counter = countAggInPallet(curPalletNumber)
            form = PalletForm(initial=initial_dict)
            return render(request, 'palletizing/confirmPallet.html', {'form': form, 'counter': counter})
    elif 'disband' in request.POST:
        print('разрушаем')
        if request.method == 'POST':
            curTaskNumber = request.POST['task']
            curPalletNumber = request.POST['pallet']
            disbandPallet(curPalletNumber)

            initial_dict = {
                "taskField": curTaskNumber,
            }
            form = PalletForm(initial=initial_dict)
            return render(request, 'palletizing/palletNumberForm.html', {'form': form})
    elif 'write' in request.POST:
        if request.method == 'POST':
            form = AggregateForm(request.POST)
            if form.is_valid():
                print(request.POST.get('pallet'))
                print(request.POST.get('aggregateField'))

                curTaskNumber = request.POST.get('task')
                curPalletNumber = request.POST.get('pallet')
                curAggregateNumber = request.POST.get('aggregateField')

                # Проверка GTIN агрегата и присваевание наименования заданию
                initial_dict = {
                    "pallet": curPalletNumber,
                    "task": curTaskNumber
                }
                form = AggregateForm(initial=initial_dict)



                
                # Вызов функции проверки кода агрегата на линии
                resolution = checkAggreageteCode(curTaskNumber, curAggregateNumber)
                if resolution['resolution']:
                if resolution['resolution']:
                    # Добавляем код агрегата в паллет
                    saveAggregate(curAggregateNumber, curPalletNumber, curTaskNumber)
                    listAggCode = loadCodeInPallet(curPalletNumber, curTaskNumber)
                    counter = len(set(listAggCode))
                    # Выгрузка списка кодов агрегата в паллете

                    print(f'Код добавляем')
                    messages.success(request, resolution['msg'])
                    return render(request, 'palletizing/fillingPallet.html', {'form': form, 'code': listAggCode, 'counter': counter})
                else:
                    listAggCode = loadCodeInPallet(curPalletNumber, curTaskNumber)
                    counter = len(set(listAggCode))
                    print(f'Код добавляем')
                    print(resolution['msg'])
                    return render(request, 'palletizing/fillingPallet.html', {'form': form, 'code': listAggCode, 'counter': counter})
                else:
                    listAggCode = loadCodeInPallet(curPalletNumber, curTaskNumber)
                    counter = len(set(listAggCode))
                    print(resolution['msg'])
                    print(f'Код не является агрегатом. всплываюшее окно')
                    return render(request, 'palletizing/fillingPallet.html', {'form': form, 'code': listAggCode, 'counter': counter})


def countAggInPallet(curPalletNumber):
    """Выгрузка количества кодов агрегата в паллете"""
    count = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT count(code) FROM serial.group_codes WHERE pallet_number = ?', curPalletNumber)
    return count

'''def checkAggregateGTIN(curTaskNumber, curAggregateNumber):
    """Проверка и присваивание gtin заданию"""

    GTIN = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT gtin FROM serial.group_codes WHERE code = ?', curAggregateNumber)
    orderGTIN = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT gtin FROM serial.exchenge_palletes WHERE uuid = ?', curTaskNumber)'''


def loadCodeInPallet(palletNumber, taskNumber):
    """Выгрузка кодов агрегата в паллете
    для отображения на странице
    (Возможно для счетчика) """
    joined_path = os.path.join('palletFiles', f'{taskNumber}.json')
    fileExist = os.path.isfile(joined_path)
    if fileExist:
        print(f'файл с номером {taskNumber} существует')

        with open(joined_path, 'r') as file:
        with open(joined_path, 'r') as file:
            jsonFile = file.read()

        dictFile = json.loads(jsonFile)
        try:
            print(type(dictFile[palletNumber]))
            print((dictFile[palletNumber]))
            return dictFile[palletNumber]
        except Exception as err:
            print(f'Ошибка при чтении файла: {err}')
            dictFile[palletNumber] = []
            return dictFile[palletNumber]

    else:
        # print(f'файл с номером {palletNumber} не существует')
        pass


def disbandPallet(curPalletNumber):
    """При неполном наборе паллета расформировываем палет"""
    # Получаем список кодов агрегата из паллета
    aggregateList = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT code FROM serial.group_codes WHERE pallet_number = ?', curPalletNumber)
    print(aggregateList)
    listAppend = []
    newTuple = ()
    for code in aggregateList:
        newTuple = newTuple + (code, 0)
        listAppend.append(newTuple)
        newTuple = ()
    print(listAppend)
    # Если список пустой, то расформировываем паллет
    if len(listAppend):
        queryDB.DatabaseConn('marking_db').queryInsertMany(
            'INSERT INTO serial.group_codes (code, status) VALUES (?,?)', listAppend)
        queryDB.DatabaseConn('marking_db').queryUpdate(
            'UPDATE serial.pallet_codes SET status =? WHERE code =?', (1, curPalletNumber))


def checkAggreageteCode(curTaskNumber, curAggregateNumber):
    """Функция проводит проверку кода агрегата на линии
    Если код агрегата считан, добавляем к списку для записи в БД
    Если код агрегата не считан, то переводим на страницу пополнения кода агрегата"""
    resolutionDict = {'resolution': False, 'msg': ''}

    curLineNumber = curTaskNumber[1:3]
    print(int(curLineNumber))
    ipLine = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT IP FROM serial.Lines where ID = ?', curLineNumber)
    print(ipLine[0])
    statusAggregate = queryDB.DatabaseConn('client_db', server=str(ipLine[0])).querySelectFetchone(
        'SELECT status FROM serial.group_codes where code = ?', curAggregateNumber)
    print(statusAggregate)
    if len(statusAggregate):
        status = int(statusAggregate[0])
        if status == 0:
            print('Код агрегата полный')
            message = f'Код агрегата валиден'
            message = f'Код агрегата валиден'
            resolution = True
        else:
            print('Код агрегата не считан на линии')
            message = f'Код агрегата не считан на линии'
            message = f'Код агрегата не считан на линии'
            resolution = False
    else:
        print('Код агрегата не найден')
        message = f'Отсканирован не верный код'
        resolution = False

    resolutionDict['resolution'] = resolution
    resolutionDict['msg'] = message
    return resolutionDict
    resolutionDict['resolution'] = resolution
    resolutionDict['msg'] = message
    return resolutionDict


def saveAggregate(aggregeteNumber, palletNumber, curTaskNumber):
    """Функция проверяет файл с переданным в нее номером паллета
        выгружает все аггрегаты в этом файле
        проверяет на дублирование
        добавляет новый аггрегат в файл"""
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    print(f'Это код агрегата - {aggregeteNumber}')
    print(f'Это номер паллета - {palletNumber}')
    joined_path = os.path.join('palletFiles', f'{curTaskNumber}.json')
    
    fileExist = os.path.isfile(joined_path)
    print(fileExist)

    if fileExist:
        print(f'файл с номером {curTaskNumber} существует')

        # Присваевания коду агрегата номера паллета и номера задания
        aggregateInDB(curTaskNumber, palletNumber, aggregeteNumber)

        with open(joined_path, 'r') as file:
        with open(joined_path, 'r') as file:
            jsonFile = file.read()

        dictFile = json.loads(jsonFile)
        print(dictFile[palletNumber])
        dictFile[palletNumber].append(aggregeteNumber)
        print(dictFile)

        with open(joined_path, 'w') as file:
        with open(joined_path, 'w') as file:
            json.dump(dictFile, file)

    else:
        #print(f'файл с номером {palletNumber} не существует')
        pass


def aggregateInDB(task, palletNumber, aggregateCode):
    """Функция добавляет к коду агрегата номер паллета и номер задания
    добавляет gtin к номеру задаия"""
    try:
        queryDB.DatabaseConn('marking_db').queryInsert(
            'INSERT INTO serial.group_codes (code, status, pallet_number, uuid_pallet) VALUES (?,?,?,?)', (aggregateCode, 0, palletNumber, task))
    except Exception as err:
        print(err)


def closePallet(request):
    """Подтверждение завершения паллета"""
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            curTaskNumber = request.POST['taskField']
            #createNewTask(curTaskNumber)

            curPalletNumber = request.POST['curPallet']
            complitePalletNumber = request.POST['palletField']


            print(curTaskNumber)

            resolutionComplited = complitePalletCode(curPalletNumber, complitePalletNumber)

            if resolutionComplited:
                initial_dict = {
                    "taskField": curTaskNumber,
                }
                form = PalletForm(initial=initial_dict)
                return render(request, 'palletizing/palletNumberForm.html', {'form': form})
            else:
                initial_dict = {
                    "taskField": curTaskNumber,
                    "curPallet": curPalletNumber
                }
                print(curTaskNumber)
                form = PalletForm(initial=initial_dict)
                return render(request, 'palletizing/confirmPallet.html', {'form': form})


def complitePalletCode(curPalletNumber, complitePalletNumber):
    """Функция меняет статус кода паллета на завершен
    после подтверждения"""
    if curPalletNumber == complitePalletNumber:
        resolution = True

        queryDB.DatabaseConn('marking_db').queryUpdate(
            'UPDATE serial.pallet_codes SET status =? WHERE code =?', (3, curPalletNumber))
    else:
        resolution = False

    return resolution

def checkAggregateCode(aggregateNumber, palletNumber):
    """Проверка наличия кода аггрегата в файле"""
    print(f'Это код агрегата - {aggregateNumber}')
    print(f'Это номер паллета - {palletNumber}')
    joined_path = os.path.join('palletFiles', f'{palletNumber}.json')
    #Чтение файла
    with open(joined_path, 'a') as f:
        f.write(aggregateNumber+'\n')

