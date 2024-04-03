from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect
import re


class M1(MiddlewareMixin):
    ''' 中间件 '''
    def process_request(self, request):
        if request.path_info == '/user/login/':
            return
        if request.path_info == '/user/create/' or request.path_info == '/user/edit/':
            return
        if re.findall(r'^/app01/users/', request.path_info):
            return

        info = request.session.get('info')
        # print(info)
        if not info:
            return redirect('/user/login/')
        return
