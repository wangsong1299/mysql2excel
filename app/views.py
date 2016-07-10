#coding:utf-8
import os, re, json, random
from django import forms
from django.template import Context, Template
from django.template.loader import get_template  
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

from django.contrib.auth.decorators import login_required  
from django.views.decorators.csrf import csrf_exempt

from channels.handler import AsgiHandler
from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http


import models as dataModel

# http requests
# Create your views here.
def index(request):
	# template = Template('My name is {{name}}')
	# context = Context({'name': 'test'})

	template = get_template('index.html')  
	context = {'name':'NIM'}
	html = template.render(context = context, request = request)
	return HttpResponse(html)

@csrf_exempt
@login_required(login_url="/login/")  
def home(request):
    return render(request, 'home.html')

@login_required(login_url="/login/")  
def downloads(request):
    listFiles = os.listdir(os.path.join(os.getcwd(), 'app/static/datafile'))
    file_list = []
    for fileName in listFiles:
        file_list.append({
                'name': fileName,
                'link': '/static/datafile/' + fileName
            })
    template = get_template('downloads.html')  
    context = {'file_list': file_list}
    html = template.render(context = context, request = request)
    return HttpResponse(html)

@csrf_exempt
@login_required(login_url="/login/")  
def uploads(request):
    if request.method == "POST":
        fileTmp = request.FILES['excelFile']
        fileName = fileTmp.name
        if re.search(r'\.xlsx$', fileName):
            filePath =  os.path.dirname(__file__)
            dest = open(os.path.join(filePath, 'static/datafile/' + fileName), 'wb+')
            for chunk in fileTmp.chunks():
                dest.write(chunk)
            dest.close()
            return HttpResponse('upload ' + fileName + ' ok!')
        else:
            return HttpResponse(fileName + ' is not an excel file!')
    return render_to_response('uploads.html')


# websocket channel
# Connected to websocket.connect
from models import cache_data

@channel_session
@channel_session_user_from_http
def ws_connect(message):
    # room = message.content['path'].strip('/')
    group_user = unicode(message.user) + unicode(int(random.random() * 10000))
    message.channel_session['user'] = group_user
    Group(group_user).add(message.reply_channel)
    cache_data[group_user] = {}

# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    group_user = message.channel_session['user']
    Group(group_user).discard(message.reply_channel)
    if cache_data.has_key(group_user):
        del cache_data[group_user]

@channel_session
def ws_receive(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    try:
        group_user = message.channel_session['user']
        data = json.loads(message['text'])
        command = data['msg']
        dataModel.parseCommand(command, group_user = group_user)
    except Exception, what:
        print 'ws receive err: ', what
    # message.reply_channel.send({
    #     "text": command,
    # })