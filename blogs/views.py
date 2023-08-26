from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import json
from operator import itemgetter
from datetime import datetime
from django.db.models import Q
from django.core import serializers
import csv
from django.db.models import Subquery, OuterRef
from django.db.models import F, Value
from django.core.files.uploadedfile import InMemoryUploadedFile
import re
from django.http import HttpResponse
from .models import BlogsData,Likes,Comments,Loggers
from .Serializers.blogSerializers import BlogsDataSerializer,CommentsDataSerializer,LikesDataSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class DashboardData(View):

    @csrf_exempt
    def signup(request):
        try:
            if request.method=='POST':
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                username=body.get('username')
                email=body.get('email')
                password=body.get('password')

                if not username or not password or not email:
                    return JsonResponse({'Error': 'Username and password are required.','Message':'Failed'})
                
                user_record=User.objects.filter(email=email).last()
                if user_record is not None:
                    return JsonResponse({'Error': 'User exists','Message':'User exists Already'})

                hashed_password = make_password(password)
                user = User(username=username, password=hashed_password,email=email)
                user.save()

                return JsonResponse({'Error': 'NA','Message':'Success'})    
            return JsonResponse({'Error': 'Method Error','Message':'Error in Method'})    
        except Exception as ex:
            return JsonResponse({'Error': str(ex),'Message':'Exception'})   
    @csrf_exempt
    def login(request):
        try:
            if request.method=='POST':
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                username=body.get('username')
                password=body.get('password')

                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Error': 'NA','Message':token.key,"userId":token.user_id})
                else:
                    return JsonResponse({'Error': 'Error','Message':'Failed',"userId":'Failed'})
            return JsonResponse({'Error': 'Method Error','Message':'Error in Method',"userId":'MethodError'}) 
        except Exception as ex:
            return JsonResponse({'Error': str(ex),'Message':'Exception',"userId":'Exception'})  
        
    @csrf_exempt
    @permission_classes([IsAuthenticated])
    def logout(request):
        try:
            if request.method=="POST":
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                token.delete()
                
                return JsonResponse({'Error': 'NA','Message':'Success'})
            return JsonResponse({'Error': 'Method Error','Message':'Error in Method'}) 
        except Exception as ex:
            return JsonResponse({'Error': str(ex),'Message':'Exception'})  
            

    @csrf_exempt
    def getBlogsData(request):
        try:
            if request.method=='GET':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','data':'Auth Fail'})
                
                page=request.GET.get('page',1)

                data=BlogsData.objects.all().order_by('-dateModified')
                
                startIndex=( int(page)-1)*5
                endIndex=startIndex+5

                paginated_data=data[startIndex:endIndex]

                if len(paginated_data)==0:
                    return JsonResponse({'Error':'no data found','data':[]})
                blogs_id=[x.id for x in paginated_data]
                blogs_data=BlogsData.objects.filter(id__in=blogs_id)
                # serializered_data = BlogsDataSerializer(data=blogs_data, many=True)
                # serializered_data.is_valid()
                data=[{"id":x.id,"userId":x.userId.id,"userName":x.userId.username,"description":x.description,"dateModified":x.dateModified} for x in blogs_data]
                

                return JsonResponse({'Error':'NA','data':data})
            return JsonResponse({'Error':'Method Error','data':'Error'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'data':'Error'})


    @csrf_exempt
    def addComment(request):
        try:
            if request.method=='POST':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','Status':'Auth Fail'})
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                blogId=body.get('blogId')
                description=body.get('description')
                if blogId is None or description is None:
                    return JsonResponse({'Error':'Payload Error','Status':'Failed'})
                
                user_instance = token.user
                blog_instance = BlogsData.objects.filter(id=blogId).last()
                if user_instance is None or blog_instance is None:
                    return JsonResponse({'Error':'Payload Error','Status':'Failed'})
                new_comment=Comments()
                new_comment.dateCreated=datetime.now()
                new_comment.userId=user_instance
                new_comment.blogId=blog_instance
                new_comment.description=description
                new_comment.save()
                commentqueryset=Comments.objects.filter(id=new_comment.id)
                # data=CommentsDataSerializer(commentqueryset)
                data=[{"id":x.id,"userId":x.userId.id,"userName":x.userId.username,"description":x.description} for x in commentqueryset]
                return JsonResponse({'Error':'NA','Status':data})
               
    
            return JsonResponse({'Error':'Method Error','Status':'Failed'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'Status':'Error'})


    @csrf_exempt
    def addLike(request):
        try:
            if request.method=='POST':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','Status':'Auth Fail'})
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                blogId=body.get('blogId')
                if  blogId is None:
                    return JsonResponse({'Error':'Payload Error','Status':'Failed'})
                
                user_instance =token.user
                blog_instance = BlogsData.objects.filter(id=blogId).last()
                if user_instance is None or blog_instance is None:
                    return JsonResponse({'Error':'Payload Error','Status':'Failed'})
                found=Likes.objects.filter(blogId=blog_instance,userId=user_instance).last()
                if found is not None:
                    return JsonResponse({'Error':'Already Liked','Status':'Liked Already'})
                new_like=Likes()
                new_like.dateCreated=datetime.now()
                new_like.userId=user_instance
                new_like.blogId=blog_instance
                new_like.save()
                likes_queryset=Likes.objects.filter(id=new_like.id)
                # data=LikesDataSerializer(likes_queryset)
                data=[{"id":x.id,"userId":x.userId.id,"userName":x.userId.username} for x in likes_queryset]

                return JsonResponse({'Error':'NA','Status':data})
                
            return JsonResponse({'Error':'Method Error','Status':'Failed'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'Status':'Error'})
        

    @csrf_exempt
    def createBlog(request):
        try:
            if request.method=='POST':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','Status':'Auth Fail'})
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                description=body.get('description')
                if description is None:
                    return JsonResponse({'Error':'Payload Error','Status':'Failed'})
                
                user_instance=User.objects.get(id=token.user.id)
                new_blog=BlogsData()
                new_blog.dateCreated=datetime.now()
                new_blog.dateModified=datetime.now()
                new_blog.userId=user_instance
                new_blog.description=description
                new_blog.save()
                return JsonResponse({'Error':'NA','Status':'Success'})
                     
            return JsonResponse({'Error':'Method Error','Status':'Failed'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'Status':'Error'})
        

    @csrf_exempt
    def getLikes(request):
        try:
            if request.method=='GET':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','Status':'Auth Fail'})
                blogId=request.GET.get('blogId',None)
                if blogId is None:
                    return JsonResponse({'Error':'Params Error','Status':'Failed'})
                likes_data=Likes.objects.filter(blogId=blogId)
                data=[{"id":x.id,"userId":x.userId.id,"userName":x.userId.username} for x in likes_data]

                # data=LikesDataSerializer(data=likes_data, many=True)
                # data.is_valid()

                return JsonResponse({'Error':'NA','Status':data})
                
            return JsonResponse({'Error':'Method Error','Status':'Failed'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'Status':'Error'})
        

    @csrf_exempt
    def getComments(request):
        try:
            if request.method=='GET':
                token_key = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[1]
                token = Token.objects.get(key=token_key)
                if not token.user.is_authenticated:
                    return JsonResponse({'Error':'Auth Failed','Status':'Auth Fail'})
                blogId=request.GET.get('blogId',None)
                if blogId is None:
                    return JsonResponse({'Error':'Params Error','Status':'Failed'})
                comments_data=Comments.objects.filter(blogId=blogId)
                data=[{"id":x.id,"userId":x.userId.id,"userName":x.userId.username,"description":x.description} for x in comments_data]
                # data=CommentsDataSerializer(data=comments_data, many=True)
                # data.is_valid()
                return JsonResponse({'Error':'NA','Status':data})
                      
            return JsonResponse({'Error':'Method Error','Status':'Failed'})
        except Exception as ex:
             return JsonResponse({'Error':str(ex),'Status':'Error'})