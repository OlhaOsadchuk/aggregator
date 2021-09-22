import os

from rest_framework import serializers

from auto import glossary
from report.models import ReportPodbor, Photo
from auto.models import Auto, BodyType, MarkAuto, Year, Generation, ModelAuto
from aggregator.serializers.serializers_user import UserInfoSerializer
from aggregator.constants import TYPE_PHOTO
from report import report_constants


class BodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyType
        fields = "__all__"


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = "__all__"


class MarkAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkAuto
        exclude = ("popular",)


class ModelAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelAuto
        fields = ("name", "id")


class GenerationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("_name")

    def _name(self, obj):
        return obj.__str__()

    class Meta:
        model = Generation
        fields = ("name", "id")


class AutoSerializer(serializers.ModelSerializer):
    body_type_auto = BodyTypeSerializer()
    year_auto = YearSerializer()
    mark_auto = MarkAutoSerializer()
    generation = GenerationSerializer()
    model_auto = ModelAutoSerializer()

    transmission_type = serializers.SerializerMethodField("_transmission_type")
    engine_type = serializers.SerializerMethodField("_engine_type")
    drive_type = serializers.SerializerMethodField("_drive_type")
    author_type = serializers.SerializerMethodField("_author_type")
    engine_capacity = serializers.SerializerMethodField("_engine_capacity")

    def _transmission_type(self, obj):
        return dict(key=obj.transmission_type,
                    value=glossary.TRANSMISSION_TYPE[obj.transmission_type][1])

    def _engine_type(self, obj):
        return dict(key=obj.engine_type,
                    value=glossary.ENGINE_TYPE[obj.engine_type][1])

    def _drive_type(self, obj):
        return dict(key=obj.drive_type,
                    value=glossary.DRIVE_TYPE[obj.drive_type][1])

    def _author_type(self, obj):
        return dict(key=obj.author_type,
                    value=glossary.AUTHOR_TYPE[obj.author_type][1])

    def _engine_capacity(self, obj):
        return dict(key=obj.engine_capacity,
                    value=glossary.ENGINE_CAPACITY[int(float(obj.engine_capacity)*10)][1])

    class Meta:
        model = Auto
        exclude = ("data_lk", "notifications", "deleted")


class CreateUpdateAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auto
        exclude = ("data_lk", "notifications", "deleted")


class SearchVinSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=3, max_length=17)


class AutoVINSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auto
        fields = ("vin", "id")


class ReportSerializer(serializers.ModelSerializer):
    auto = AutoSerializer()
    executor = UserInfoSerializer()
    status = serializers.SerializerMethodField("_status")
    report_type = serializers.SerializerMethodField("_report_type")
    photo = serializers.SerializerMethodField('_photo')

    def _status(self, obj):
        return dict(key=obj.status,
                    value=obj.STATUS[obj.status][1])

    def _report_type(self, obj):
        return dict(key=obj.report_type,
                    value=obj.REPORT_TYPE[obj.report_type][1])

    def _photo(self, obj):
        photo = obj.photos_auto.filter(photo_type=report_constants.PHOTOFRONTVIEWS).first()
        if not photo:
            return {}
        if photo.image_google:
            return dict(photo={
                "image_small": '/google_photo/google_images/' + photo.image_google + '/150/150/',
                "image": '/google_photo/google_images/' + photo.image_google,
                "image_google": photo.image_google,
                "from_google": 'from-google',
                "pk": photo.pk,
            })
        if photo.googlePhoto:
           return dict(photo={
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
            path_to_image_small = photo.image_small.path
            if not os.path.exists(path_to_image_small):
                photo.image_small.generate()
            image_full = "/media/" + str(photo.image)
            try:
                photo.image_small.url
                photo.image_small.url.split("/")[3]
                image_small = "/media/" + str(photo.image_small)
            except:
                if photo.embed_url:
                    image_full = image_small = photo.embed_url
            return {
                "image_small": image_small,
                "image": image_full,
                "image_google": '',
                "from_google": 'from-local',
                "pk": photo.pk,
                }

    class Meta:
        model = ReportPodbor
        exclude = ("order",  # TODO add later
                   'lk_id', "notifications", "data", "google_album", "google_album_url",
                   "upload_ftp_status", "success_upload_status")


class ReportCreateUpdateDestroySerializer(serializers.ModelSerializer):
    auto_id = serializers.IntegerField(required=False)

    class Meta:
        model = ReportPodbor
        exclude = ("order",  # TODO add later
                   'lk_id', "notifications", "data", "executor", "google_album", "google_album_url",
                   "upload_ftp_status", "success_upload_status")


class GetPhotoReportSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, write_only=True)
    type_photo = serializers.ChoiceField(required=True, write_only=True, choices=TYPE_PHOTO)

    class Meta:
        model = ReportPodbor
        fields = ("id", 'type_photo')


class UploadPhotoReportSerializer(serializers.ModelSerializer):
    photo_file = serializers.ImageField(write_only=True)

    class Meta:
        model = Photo
        fields = ("id", "report_podbor", "photo_type", "photo_file")
