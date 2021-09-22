from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission

from aggregator.custom_api_exeptions import Http403
from aggregator.models import TokenAggregatorModel


class IsUserAuthenticated(BasePermission):
    def has_permission(self, request, view):

        if 'HTTP_AUTHORIZATION' not in request.META:
            raise Http403(detail="Нету токена доступа.")

        token = request.META['HTTP_AUTHORIZATION'].split(" ")[True]

        try:
            TokenAggregatorModel.objects.get(token=token)
        except Exception:
            raise Http403(detail="Неверный токен.")

        return True
