from django.db.models import Avg
from rest_framework import serializers
from core.models import (
    User, Filial, Equipment
)
from aggregator.models import TokenAggregatorModel


class UserIdSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', )


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, min_length=11)


class CodeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, min_length=4, write_only=True)
    id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'code')


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = TokenAggregatorModel
        fields = ("token", )


class FilialRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = ("name", )


class UserInfoSerializer(serializers.ModelSerializer):
    filials = FilialRelatedSerializer(many=True)
    rating = serializers.SerializerMethodField('_rating')

    def _rating(self, obj):
        qs = obj.user_ex.filter(review__isnull=False).annotate(avg_rating=Avg('review__rating'))
        if qs:
            # first value of qs array is values from annotate
            # second value of qs array is orders queryset
            return int(qs[0].avg_rating)
        return 5

    class Meta:
        model = User
        fields = ("avatar", #"avatar_thumbnail",
                  "first_name", "last_name", "patronymic",
                  "email", "phone",
                  "filials",
                  "rating"
                  )


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        exclude = ("id", "expert")
