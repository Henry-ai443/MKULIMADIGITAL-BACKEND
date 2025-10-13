from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message":"User registreed successfully",
                "token":token.key,
                "user":{
                    'username':user.username,
                    'email':user.email,
                    'role':user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error':serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
