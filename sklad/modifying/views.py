import os.path

from django.shortcuts import render, HttpResponseRedirect
from modules import queryDB, ping
import re
from .forms import *
import json


def mainModify(request):
    """Переход на главную страницу паллетирования"""
    form = PalletForm()
    return render(request, 'modifying/mainModify.html', {'form': form})


def actionPallet(request):
    """Переход на страницу выбора действия с паллетом"""

    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            editPalletNumber = request.POST['palletField']
            codes = selectAggregeteCode(editPalletNumber)
            initial_dict = {
                "pallet": editPalletNumber,
                "task": codes
            }
            form = AggregateForm(initial=initial_dict)
            return render(request, 'modifying/actionPallet.html', {'form': form})

def selectAggregeteCode(editPalletNumber):
    """Выгрузка кодов агрегата по редактируемому паллету"""
    aggregeteCode = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT code FROM serial.group_codes where pallet_number = ?', editPalletNumber)
    print(aggregeteCode)
    return aggregeteCode


def actionModify(request):
    """В зависимости от выбора
    - расформировывает паллет полностью
    - расформировывает паллет частично"""
    if 'disband' in request.POST:
        if request.method == 'POST':

            editPalletNumber = request.POST['pallet']
            modifyCodes(editPalletNumber)
            form = PalletForm()
            return render(request, 'modifying/mainModify.html', {'form': form})


def modifyCodes(editPalletNumber):
    """Расформировывает паллет полностью"""
    aggregeteCodes = queryDB.DatabaseConn('marking_db').querySelectFetchone(
        'SELECT code FROM serial.group_codes where pallet_number = ?', editPalletNumber)

    listAppend = []
    newTuple = ()
    for code in aggregeteCodes:
        newTuple = newTuple + (code, 0)
        listAppend.append(newTuple)
        newTuple = ()

    if len(listAppend):
        queryDB.DatabaseConn('marking_db').queryInsertMany(
            'INSERT INTO serial.group_codes (code, status) VALUES (?,?)', listAppend)
        queryDB.DatabaseConn('marking_db').queryUpdate(
            'UPDATE serial.pallet_codes SET status =? WHERE code =?', (1, editPalletNumber))