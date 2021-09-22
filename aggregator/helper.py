import os
from datetime import datetime

import jwt
from rest_framework.generics import get_object_or_404

from aggregator.custom_api_exeptions import Http204, Http403
from aggregator.models import TokenAggregatorModel
from autopodbor.settings import SECRET_KEY
from core.models import User
from aggregator.constants import TYPE_PHOTO



def user_is_expert(user: User) -> None:
    if not user.is_expert:
        raise Http204(detail='Пользователь не експерт.')


def create_update_token_aggregator(user: User) -> TokenAggregatorModel:
    token = jwt.encode({"user_id": user.id, 'time': str(datetime.now().second)}, SECRET_KEY, algorithm='HS256')
    token_model = TokenAggregatorModel.objects.filter(user=user).first()
    if token_model:
        token_model.token = token.decode("utf-8")
        token_model.save()
    else:
        token_model = TokenAggregatorModel.objects.create(
            token=token.decode("utf-8"),
            user=user,
        )
    return token_model


def get_user_by_token(token) -> User:
    token_model = get_object_or_404(TokenAggregatorModel.objects.all(), token=token)
    return token_model.user


def get_token_from_header(request):
    return request.META['HTTP_AUTHORIZATION'].split(" ")[True]


def has_user_permission_to_report(token, report):
    user = get_user_by_token(token)
    if user == report.executor:
        return True
    raise Http403("У пользователя нету доступа к отчету.")


def make_list_for_response(tuple_list):
    qs_list = []

    for item in tuple_list:
        qs_list.append({
            'key': item[0],
            'value': item[1]
        })

    return qs_list


def is_one_month_report(report):
    time_between_insertion = datetime.now() - report.created
    if time_between_insertion.days > 30:
        raise Http403("Больше нельзя изменять отчет.")
    return True


def generate_photo_dict(report, type_photo):
    photos = {}
    type_dict = TYPE_PHOTO[type_photo]
    for photo in report.photos_auto.all():
        if photo.photo_type not in type_dict:
            continue
        photo_type = type_dict[photo.photo_type]

        if photo.image_google:
            try:
                photos[photo_type]
            except KeyError as ex:
                photos[photo_type] = []
            photos[photo_type].append({
                "image_small": '/google_photo/google_images/' + photo.image_google + '/150/150/',
                "image": '/google_photo/google_images/' + photo.image_google,
                "image_google": photo.image_google,
                "from_google": 'from-google',
                "pk": photo.pk,
            })
        if photo.googlePhoto:
            try:
                photos[photo_type]
            except KeyError as ex:
                photos[photo_type] = []
            photos[photo_type].append({
                "image_small": '/google_photo/google_images_obj/' + str(photo.googlePhoto.id) + '/150/150/',
                "image": '/google_photo/google_images_obj/' + str(photo.googlePhoto.id),
                "image_google": photo.googlePhoto.imageId,
                "from_google": 'from-google',
                "pk": photo.pk,
            })
        if photo.image:
            path_to_photo = photo.image.path
            if not os.path.exists(path_to_photo):
                photo.delete()
                continue
            path_to_image_small = photo.image_small.path
            if not os.path.exists(path_to_image_small):
                photo.image_small.generate()
            image_full = "/media/" + str(photo.image)
            try:
                photo.image_small.url
                photo.image_small.url.split("/")[3]
                image_small = "/media/" + str(photo.image_small)
            except:
                if not photo.embed_url:
                    continue
                else:
                    image_full = image_small = photo.embed_url
            try:
                photos[photo_type]
            except KeyError as ex:
                photos[photo_type] = []
            photos[photo_type].append({
                "image_small": image_small,
                "image": image_full,
                "image_google": '',
                "from_google": 'from-local',
                "pk": photo.pk,
            })
    return photos
