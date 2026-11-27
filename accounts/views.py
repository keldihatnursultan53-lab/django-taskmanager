from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserMeSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = UserMeSerializer(user).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 11-аптада JWT қосылғанда request.user арқылы жұмыс істейді.
        # 10-аптада тексеру үшін ?username=... немесе ?user_id=... арқылы да көруге болады.
        if request.user and request.user.is_authenticated:
            return Response(UserMeSerializer(request.user).data, status=status.HTTP_200_OK)

        username = request.query_params.get("username")
        user_id = request.query_params.get("user_id")

        if user_id:
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({"detail": "Пайдаланушы табылмады."}, status=status.HTTP_404_NOT_FOUND)
            return Response(UserMeSerializer(user).data, status=status.HTTP_200_OK)

        if username:
            user = User.objects.filter(username=username).first()
            if not user:
                return Response({"detail": "Пайдаланушы табылмады."}, status=status.HTTP_404_NOT_FOUND)
            return Response(UserMeSerializer(user).data, status=status.HTTP_200_OK)

        last_user = User.objects.order_by("-id").first()
        if not last_user:
            return Response({"detail": "Базада пайдаланушы жоқ."}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserMeSerializer(last_user).data, status=status.HTTP_200_OK)