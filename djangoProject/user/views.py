from django.shortcuts import render, redirect
from app01 import models as app01_models
from . import models
from . import investment_analysis
# import requests
# import re
import time
import akshare as ak
# Create your views here.


def login(request):
    form = {
        'account': '',
        'password': '',
    }
    if request.method == "GET":
        return render(request, 'login.html', form)
    form['account'] = request.POST['username']
    form['password'] = request.POST['password']
    obj = app01_models.User.objects.filter(**form)
    if len(obj) == 0:
        form['tip'] = '账号或密码错误'
        return render(request, 'login.html', form)
    request.session['info'] = {
        'id': obj.first().id,
        'account': obj.first().account,
    }
    return redirect('/user/index/')


def index(request):
    info = request.session.get('info')
    obj = app01_models.User.objects.filter(id=info['id']).first()
    data = ak.stock_zh_a_spot_em()
    data = data[['代码', '最新价']]
    # print(data)
    if request.method=='GET':
        transitions = models.HoldingStocks.objects.filter(account_id=info['id'])
        for transition in transitions:
            price = data.loc[data['代码'] == transition.code_id].iat[0, 1]
            models.HoldingStocks.objects.filter(id=transition.id).update(now_price=price)
            transition.profit = (price-transition.buy_price)*100*transition.number
            transition.profit_ratio = (price-transition.buy_price) / transition.buy_price * 100
            transition.profit_ratio = float('{:.2f}'.format(transition.profit_ratio))
        form = {
            "obj": obj,
            "transitions": transitions,
        }
        return render(request, 'index.html', form)
    number = request.POST.get('number')
    number = int(number)
    transition_id = request.POST.get('transition_id')
    transition = models.HoldingStocks.objects.get(id=transition_id)
    if transition.number < number or number <= 0:
        return redirect('/user/index/')
    # 获取现价
    # code = transition.code_id
    # url = f"https://quote.cfi.cn/quote_{code}.html"
    # resp = requests.get(url)
    # # print(resp.text)
    # price = re.findall("id='last'>(.*?)<", resp.text)[0]
    # price = float(price[0: len(price) - 1])

    price = data.loc[data['代码'] == transition.code_id].iat[0, 1]
    obj.fund += price*number*100
    obj.save()
    if transition.number == number:
        transition.delete()
    else:
        transition.number -= number
        transition.save()
    return redirect('/user/index/')


def logout(request):
    request.session.clear()
    return redirect('/user/login/')


def buy(request):
    info = request.session.get('info')
    obj = app01_models.User.objects.filter(id=info['id']).first()
    stocks = models.Stock.objects.all()
    if request.method == 'GET':
        search_stock = request.GET.get('search_stock')
        if search_stock:
            stocks1 = stocks.filter(code__contains=search_stock)
            if not stocks1:
                stocks1 = stocks.filter(title__contains=search_stock)
            stocks = stocks1
        form = {
            'obj': obj,
            'stocks': stocks,
        }
        return render(request, 'buy.html', form)

    code = request.POST.get('code')
    number = request.POST.get('number')
    number = int(number)
    # url = f"https://quote.cfi.cn/quote_{code}.html"
    # resp = requests.get(url)
    # # print(resp.text)
    # price = re.findall("id='last'>(.*?)<", resp.text)[0]
    # price = float(price[0: len(price) - 1])
    # print(price)
    data = ak.stock_zh_a_spot_em()
    data = data[['代码', '最新价']]
    price = data.loc[data['代码'] == code].iat[0, 1]
    stocks = stocks.filter(code__contains=code)
    form = {
        'obj': obj,
        'stocks': stocks,
    }
    if price*int(number)*100 > obj.fund or number <= 0:
        form['tip'] = '可用资金不足或数量错误，买入失败！'
        return render(request, 'buy.html', form)
    # print(code)

    obj.fund = obj.fund - price*number*100
    obj.save()
    obj_stock = models.Stock.objects.get(code=code)
    result = models.HoldingStocks.objects.filter(code_id=code, account_id=obj)
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if result:
        result = result.first()
        buy_price = (price*number+result.buy_price*result.number)/(number+result.number)
        buy_price = float('{:.2f}'.format(buy_price))
        result.buy_price = buy_price
        result.number += number
        result.buy_time = now_time
        result.save()
    else:
        models.HoldingStocks.objects.create(code=obj_stock, number=number, buy_price=price, account_id=obj, buy_time=now_time)
    form['tip'] = '买入成功'
    return render(request, 'buy.html', form)


def create(request):
    if request.method == "GET":
        return render(request, 'create.html')
    form = {
        'account': request.POST.get('account'),
        'name': request.POST.get('name'),
        'gender': request.POST.get('gender'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'password': request.POST.get('password'),
    }
    result = app01_models.User.objects.filter(account=form['account'])
    if result:
        form['tip'] = '该账号已存在。'
        return render(request, 'create.html', form)
    app01_models.User.objects.create(**form)
    return redirect('/user/login/')


def edit(request):
    info = request.session.get('info')
    obj = app01_models.User.objects.get(id=info['id'])
    if request.method == "GET":
        form = {
            'name': obj.name,
            'gender': obj.gender,
            'email': obj.email,
            'phone': obj.phone,
            'password': obj.password,
        }
        return render(request, 'edit.html', form)
    form = {
        'name': request.POST.get('name'),
        'gender': request.POST.get('gender'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'password': request.POST.get('password'),
    }
    app01_models.User.objects.filter(id=info['id']).update(**form)
    form['tip'] = '保存成功!'
    return render(request, 'edit.html', form)


def rank(request):
    all_users = app01_models.User.objects.all().order_by('-fund')
    # print(all_users)
    form = {
        'all_users': all_users,
    }
    return render(request, 'rank.html', form)


def analysis(request):
    if request.method == 'GET':
        return render(request, 'analysis.html')
    codes = request.POST.getlist('number')
    # print(codes)
    form = investment_analysis.Portfolio_investment_analysis(codes)
    if not form:
        form = {'tip': '提交的股票数量不足，或无法获取当前股票数据'}
        return render(request, 'analysis.html', form)
    return render(request, 'analysis_result.html', form)


def k_image(request, code):
    graphic = investment_analysis.draw_k(code)
    code = models.Stock.objects.filter(code=code).first()
    form = {
        'code': code,
        'graphic': graphic
    }
    return render(request, 'k_image.html', form)

