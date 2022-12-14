from django.conf import settings
from django.views import View
from rest_framework import viewsets
from rest_framework.views import APIView
from account.serializer import *
from django.contrib.auth.models import User
from account.serializer import CreateUserSerializer, UserSerializer

from django.shortcuts import redirect, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import response, status
from rest_framework.response import Response

import requests
import os
import json
from django.core.exceptions import ImproperlyConfigured

from django.http import JsonResponse
from django.db import models
from account.models import Profile, Coupang
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from account.serializer import *
from django.contrib.auth import authenticate, login, logout
from config.settings import SECRET_KEY, KAKAO_REST_API_KEY

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.authentication import SessionAuthentication
from cryptography.fernet import Fernet
from pathlib import Path

from config.utils import secret

secrets=secret()

class CreateUserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    def get(self, request):
        return Response("please register",status=status.HTTP_200_OK)
    def create(self, request):
        serializer = CreateUserSerializer(request.POST)
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        return redirect("http://127.0.0.1/account/login")


class loginView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def create(self, request):
        serializer = UserSerializer(request.POST)
        user = authenticate(request, username=request.POST.get(
            'username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect("http://127.0.0.1/blog/posts")
        else:
            return redirect("http://127.0.0.1/account/register")
        


class KakaoGetLogin(View):
    def get(self, request):
        REST_API_KEY = KAKAO_REST_API_KEY
        REDIRECT_URI = 'http://127.0.0.1/account/kakao/login/callback'

        API_HOST = f'https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code'

        return redirect(API_HOST)


class KaKaoSignInCallBackView(APIView):
    def get(self, request):
        auth_code = request.GET.get('code')
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_REST_API_KEY,
            'redirection_uri': 'http://127.0.0.1',
            'code': auth_code
        }

        token_response = requests.post(kakao_token_api, data=data)

        access_token = token_response.json().get('access_token')

        user_info_response = requests.get(
            'https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
        user_info = user_info_response.json()
        if not Profile.objects.filter(kakao_id=user_info["id"]).exists():
            user_register_data = {
                'username': user_info["id"],
                'password': user_info["properties"]["nickname"]
            }
            user_register_response = requests.post(
                'http://127.0.0.1/account/register', data=user_register_data)
            profile = Profile.objects.create(user=User.objects.get(
                username=user_info["id"]), kakao_id=user_info["id"], nickname=user_info["properties"]["nickname"])

        user = authenticate(
            request, username=user_info["id"], password=user_info["properties"]["nickname"])
        if user is not None:
            login(request, user)
        return redirect('http://127.0.0.1/blog/posts')


class KakaoGetLogout(View):
    def get(self, request):
        REST_API_KEY = KAKAO_REST_API_KEY
        REDIRECT_URI = 'http://127.0.0.1'

        API_HOST = f'http://kauth.kakao.com/oauth/logout?client_id=${REST_API_KEY}&logout_redirect_uri=${REDIRECT_URI}'

        return redirect(API_HOST)


class logoutView(View):
    def get(self, request):
        logout(request)
        return redirect('http://127.0.0.1/account/login')


class CoupangRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    serializer_class = UserSerializer
    queryset = Coupang.objects.all()
    def create(self, request):
        fernet=Fernet(secrets['HASH_KEY'])
        Coupang.objects.update_or_create(
            user=User.objects.get(id=request.user.id),
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        return Response(status=status.HTTP_201_CREATED)
