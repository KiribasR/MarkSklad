from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Search
from .forms import SearchForm
from modules import queryDB


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def search(request):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print("Это тоже сработало")
            return HttpResponseRedirect('/thanks/')

        # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()
    data = {
        'form': form
    }
    return render(request, 'search/search.html', data)


def search_results(request):
    print('Поиск сработал')
    ip = get_client_ip(request)
    print (f'ip = {ip}')
    form = SearchForm()
    if request.method == 'POST':
        resultData = request.POST['searchField']

        print(resultData)
    #resv = queryDB.DatabaseConn('marking_db').querySelectFetchall("SELECT * FROM serial.exchange_files WHERE batch = ?", resultData)
    #resv = queryDB.DatabaseConn('marking_db').querySelectFetchall("SELECT * FROM serial.exchange_files WHERE batch = ?", resultData)

    #print(resv)
    """if resultData.find('\x1d') != -1:
        print('Найдены символы \x1d')
        resultData = resultData
    else:
        print('Не найдены символы \x1d')

        resultData = resultData.replace('~', '\x1d')
    resv = queryDB.DatabaseConn('marking_db').querySelectFetchone("SELECT status FROM serial.mark_codes WHERE code = ?",
                                                                  resultData)"""
    result = definitionMode(resultData)
    return render(request, 'search/searchResult.html', {'form': form, 'resultData': result})


def definitionMode(searchData):
    """Функция определения формата поиска:
    Поиск по
    - КИ,
    - КИТУ,
    - Паллет,
    - номеру задания на паллет"""

    # Поиск GS коде:
    if searchData.find('\x1d') != -1:
        # Ищем код маркировки
        print('Ищем код маркировки')
        data = searchCode(searchData)

        """elif searchData.find('~') != -1:
            # Ищем код маркировки с заменой ~ на GS код
            print('Ищем код маркировки с заменой ~ на GS код')
            searchData = searchData.replace('~', '\x1d')
            data = searchCode(searchData)"""
    else:
        if searchData.find('\x1d') == -1 and len(searchData) <= 12:
            # Ищем номер задания на паллет
            print('Ищем номер задания на паллет')
            data = searchOrderPallet(searchData)

        elif searchData.find('\x1d') == -1  and len(searchData) <=22 and len(searchData) >12:
            # Ищем номер паллета
            print('Ищем номер паллета')
            data = searchPalletNumber(searchData)
        elif searchData.find('\x1d') == -1 and len(searchData) >23:
            # Ищем код аггрегата
            print('Ищем код аггрегата')
            data = searchAggNumber(searchData)

    print(data)
    return data


def searchCode(code):
    """Поиск кода маркировки по запросу"""
    # Определение места положения кода (на линии или на сервере)
    location = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT status, line FROM serial.exchange_files WHERE batch IN '
        '(SELECT batch FROM serial.mark_codes WHERE code =?)',
        code)
    print(location)
    if len(location) != 0:
        if location[0][0] == 2:
            print('Ищем код маркировки на линии')
            lineData = queryDB.DatabaseConn('marking_db').querySelectFetchall(
                'SELECT IP, name FROM serial.Lines where ID = ?', location[0][1])
            IP = lineData[0][0]
            LineName = lineData[0][1]
            print(IP)
            data = queryDB.DatabaseConn('client_db', IP).querySelectFetchall(
                'SELECT code, aggregate_number, created, updated, line, status, batch FROM serial.mark_codes WHERE code = ?',
                code)
            print(data)

        else:
            print('Ищем код маркировки на сервере')
            data = queryDB.DatabaseConn('marking_db').querySelectFetchall(
                'SELECT code, aggregate_number, created, updated, line, status, batch FROM serial.mark_codes WHERE code =?',
                code)
            LineName = 'Сервер'

        # Структурирование полученных данных в словарь

        codeResult = data[0][0]
        aggregateResult = definitionAggregate(data[0][1])
        created = data[0][2].strftime('%d.%m.%Y %H:%M:%S')
        updated = data[0][3].strftime('%d.%m.%Y %H:%M:%S')
        line = LineName
        status = definitionStatus(data[0][5])
        batch = data[0][6]

        dictCode = {'Код маркировки': codeResult,
                    'Статус': status,
                    'Линия': line,
                    'Задание': batch,
                    'Код агрегата': aggregateResult,
                    'Время создания': created,
                    'Время обновления': updated}



    else:
        dictCode = {'Код маркировки': 'Код не найден'}
    return dictCode


def definitionStatus(inputstatus):
    """Перевод статуса в человекочитаймый вид"""
    dictStatus = {0: 'Полный',
                  1: 'Пустой',
                  2: 'Брак',
                  3: 'На печать',
                  4: 'Новый',
                  5: 'Напечатан',
                  6: 'Экспорт',
                  7: 'Закрыт',
                  8: 'Удален'}
    status = dictStatus.get(inputstatus)
    return status


def definitionAggregate(inputAggregate):
    """Перевод агрегата в человекочитаймый вид"""
    if inputAggregate == None:
        outputAggregate = '-'
    else:
        outputAggregate = inputAggregate

    return outputAggregate


def searchOrderPallet(searchData):
    """Поиск по номеру задания"""
    data = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT created, status, lineID FROM serial.exchange_palletes WHERE uuid =?',
        searchData)
    name = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT name FROM serial.product where gtin = (select top(1) gtin from serial.group_codes where uuid_pallet = ?)',
        searchData)
    countPallet = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT count(code) FROM serial.pallet_codes where task = ?',
        searchData)
    # Структурирование полученных данных в словарь
    print(data)
    if len(data) != 0:
        dictBatch = {'uuid': searchData,
                     'created': data[0][0].strftime('%d.%m.%Y %H:%M:%S'),
                     'status': data[0][1],
                     'line': data[0][2],
                     'name': name,
                     'countPallet': countPallet
                     }
    else:
        dictBatch = {'batch': 'Задание не найдено'}
    return dictBatch


def searchPalletNumber(searchData):
    """Поиск по номеру паллета"""
    data = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT created, status, updated, pack_size, task FROM serial.pallet_codes WHERE code =?',
        searchData)
    countAgg = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT count(code) FROM serial.group_codes where pallet_number = ?',
        searchData)
    # Структурирование полученных данных в словарь
    print(data)
    if len(data) != 0:
        dictBatch = {'code': searchData,
                     'created': data[0][0].strftime('%d.%m.%Y %H:%M:%S'),
                     'updated': data[0][2].strftime('%d.%m.%Y %H:%M:%S'),
                     'status': data[0][1],
                     'size': data[0][3],
                     'task': data[0][4],
                     'countPallet': countAgg
                     }
    else:
        dictBatch = {'code': 'Код паллета не найден'}
    return dictBatch


def searchAggNumber(searchData):
    """Поиск по номеру агрегата"""
    data = queryDB.DatabaseConn('marking_db').querySelectFetchall(
        'SELECT status, created, updated, batch, gtin, pallet_number, uuid_Pallet FROM serial.group_codes WHERE code =?',
        searchData)
    name = queryDB.DatabaseConn('MARKING_DB').querySelectFetchone(
        'SELECT name FROM serial.product where gtin = (select top(1) gtin from serial.group_codes where code = ?)',
        searchData)
    # Структурирование полученных данных в словарь
    print(data)
    status = searchData
    if data[0][1] != None:
        created = data[0][1].strftime('%d.%m.%Y %H:%M:%S'),
    else:
        created = '-'

    if data[0][2] != None:
        updated = data[0][2].strftime('%d.%m.%Y %H:%M:%S'),
    else:
        updated = '-'
    if data[0][5] == None:
        pallet_number = '-'
    else:
        pallet_number = data[0][5]

    if data[0][6] == None:
        uuid_pallet = '-'
    else:
        uuid_pallet = data[0][6]

    if len(data) != 0:
        dictBatch = {'code': searchData,
                     'status': data[0][0],
                     'created': created,
                     'updated': updated,
                     'batch': data[0][3],
                     'gtin': data[0][4],
                     'pallet_number': pallet_number,
                     'uuid_pallet': uuid_pallet,
                     'name': name[0]
                     }
    else:
        dictBatch = {'code': 'Код агрегата не найден'}
    return dictBatch


