from rest_framework import generics, status
from rest_framework.response import Response

from aggregator.helper import get_user_by_token, get_token_from_header
from aggregator.permissions import IsUserAuthenticated
from autopodbor.utils import send_simple_message_mailgun
from aggregator.serializers.serializers_support import SupportSerializer


class SupportView(generics.CreateAPIView):
    serializer_class = SupportSerializer
    permission_classes = [IsUserAuthenticated]

    def get_object(self):
        return get_user_by_token(get_token_from_header(self.request))

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_simple_message_mailgun(subject="Сообщение с агрегатора. Форма: Поддержка. "+serializer.validated_data.get("subject"),
                                    message=serializer.validated_data.get("message"),
                                    from_email=user.email,
                                    to_email="avtopodboranalytics@gmail.com")

        return Response(status=status.HTTP_200_OK)
