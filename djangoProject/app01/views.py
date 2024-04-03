from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models


def users_list(request):
    queryset = models.User.objects.all()
    gender_choices = [
        (1, '男'),
        (0, '女'),
    ]
    context = {"queryset": queryset,
               'gender_choices': ('女', '男'),
               }
    return render(request, 'users_list.html', context)


def users_add(request):
    if request.method == 'GET':
        return render(request, 'users_add.html')
    form = {
        'account': request.POST.get('account'),
        'name': request.POST.get('name'),
        'gender': request.POST.get('gender'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'password': request.POST.get('password'),
    }
    result = models.User.objects.filter(account=form['account'])
    if result:
        form['tip'] = '该账号已存在。'
        return render(request, 'users_add.html', form)
    models.User.objects.create(**form)
    return redirect('/app01/users/list/')


def users_edit(request, user_id):
    obj = models.User.objects.filter(id=user_id).first()
    if request.method == 'GET':
        return render(request, 'users_edit.html', {'obj': obj})
    form = {
        'account': request.POST.get('account'),
        'name': request.POST.get('name'),
        'gender': request.POST.get('gender'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'password': request.POST.get('password'),
    }
    models.User.objects.filter(id=user_id).update(**form)
    return redirect('/app01/users/list/')


def users_delete(request, user_id):
    models.User.objects.filter(id=user_id).delete()
    return redirect('/app01/users/list/')

