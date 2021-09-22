from django.views.decorators.http import require_http_methods
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from aggregator.custom_api_exeptions import Http204
from aggregator.helper import (
    user_is_expert, create_update_token_aggregator, get_user_by_token, get_token_from_header
)
from aggregator.permissions import IsUserAuthenticated
from aggregator.send_code import SendCode

from core.models import User, Equipment
from aggregator.serializers.serializers_user import (
    PhoneSerializer, CodeSerializer, UserIdSerializer,
    UserInfoSerializer, EquipmentSerializer,
)


class CheckPhoneView(generics.RetrieveAPIView):
    def get_object(self):
        serializer = PhoneSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return get_object_or_404(User.objects.all(), phone=serializer.validated_data.get('phone'))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_is_expert(instance)
        return Response(dict(id=instance.id), status=status.HTTP_200_OK)


class CreateCodeView(generics.RetrieveAPIView):
    def get_object(self):
        serializer = UserIdSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return get_object_or_404(User.objects.all(), id=self.request.query_params.get('id'))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_is_expert(instance)

        send_code = SendCode()
        send_code.send_code(instance.id, instance.phone)
        return Response(dict(id=instance.id), status=status.HTTP_200_OK)


class CheckCodeView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        serializer = CodeSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        instance = get_object_or_404(User.objects.all(), id=serializer.validated_data.get('id'))
        user_is_expert(instance)

        code_check = serializer.validated_data.get('code')
        send_code = SendCode()
        send_code.check_code(instance.id, code_check)

        token_model = create_update_token_aggregator(instance)
        return Response(dict(token=token_model.token), status=status.HTTP_201_CREATED)


class GetUserInfoView(generics.RetrieveAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = [IsUserAuthenticated]

    def get_object(self):
        return get_user_by_token(get_token_from_header(self.request))


class GetUserEquipment(generics.RetrieveAPIView):
    serializer_class = EquipmentSerializer
    permission_classes = [IsUserAuthenticated]

    def get_object(self):
        user = get_user_by_token(get_token_from_header(self.request))
        try:
            equipment = Equipment.objects.get(expert=user)
        except Exception:
            raise Http204(detail="У пользователя нет оборудования.")
        return equipment
