from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from . import models
from .serializers import TreeSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


def child_nodes(id, depth):
    objects = TreeSerializer(
        models.Worker.objects.filter(head=id), many=True).data
    if depth > 1 and objects:
        for i in objects:
            nodes = child_nodes(i['id'], depth-1)
            if nodes:
                i['subordinates'] = nodes
    return objects


@api_view(['GET'])
def subordinates(request, id):
    depth = 1
    try:
        depth = int(request.query_params.get('depth', 1))
    except:
        pass
    if id == 0:
        workers = child_nodes(None, depth)
    else:
        workers = child_nodes(id, depth)
    return Response(workers)


def auth(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                user = authenticate(username=username, password=password)
                if user and user.is_active:
                    login(request, user)
                    return redirect('list')
        return render(request, 'auth.html', {})
    else:
        return redirect("/")


def log_out(request):
    logout(request)
    return redirect('/')
