from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from safedelete import SOFT_DELETE_CASCADE

from aggregator.permissions import IsUserAuthenticated

from auto import glossary
from aggregator.serializers.serializers_report import *
from report import report_constants

from report.models import ReportPodbor, Photo
from auto.models import Auto, BodyType, Year, MarkAuto, ModelAuto, Generation, AutoPhoto

from aggregator.helper import (
    get_user_by_token, get_token_from_header, has_user_permission_to_report, make_list_for_response,
    is_one_month_report, generate_photo_dict
)

from aggregator.custom_api_exeptions import Http204, Http400


class ReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        user = get_user_by_token(get_token_from_header(self.request))
        reports = ReportPodbor.objects.filter(executor=user, deleted__isnull=True)
        return reports


class AutoVinListView(generics.ListAPIView):
    serializer_class = AutoVINSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        serializer = SearchVinSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        vins = Auto.objects.filter(vin__contains=self.request.query_params.get("text"), deleted__isnull=True)
        return vins


class BodyTypeListView(generics.ListAPIView):
    serializer_class = BodyTypeSerializer
    permission_classes = [IsUserAuthenticated]
    queryset = BodyType.objects.all()


class YearListView(generics.ListAPIView):
    serializer_class = YearSerializer
    permission_classes = [IsUserAuthenticated]
    queryset = Year.objects.all()


class MarkAutoListView(generics.ListAPIView):
    serializer_class = MarkAutoSerializer
    permission_classes = [IsUserAuthenticated]
    queryset = MarkAuto.objects.all()


class ModelAutoListView(generics.ListAPIView):
    serializer_class = ModelAutoSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        if 'mark_id' not in self.request.query_params:
            raise Http400(detail="mark_id - обязательное поле.")
        return ModelAuto.objects.filter(mark_auto=self.request.query_params.get("mark_id"))


class GenerationListView(generics.ListAPIView):
    serializer_class = GenerationSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        if 'model_id' not in self.request.query_params:
            raise Http400(detail="model_id - обязательное поле.")
        return Generation.objects.filter(model_auto=self.request.query_params.get("model_id"))


class TransmissionTypeListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(glossary.TRANSMISSION_TYPE))


class EngineTypeListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(glossary.ENGINE_TYPE))


class DriveTypeListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(glossary.DRIVE_TYPE))


class AuthorTypeListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(glossary.AUTHOR_TYPE))


class EngineCapacityListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(glossary.ENGINE_CAPACITY))


class ReportTypeListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        report = ReportPodbor()
        return Response(make_list_for_response(report.REPORT_TYPE))


class ReportStatusListView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        report = ReportPodbor()
        return Response(make_list_for_response(report.STATUS))


class CreateUpdateDestroyAutoView(generics.UpdateAPIView, generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsUserAuthenticated]
    serializer_class = CreateUpdateAutoSerializer

    def get_object(self):
        if 'id' in self.request.data:
            _id = self.request.data.get("id")
        elif 'id' in self.request.query_params:
            _id = self.request.query_params.get("id")
        else:
            raise Http400(detail="id - обязательное поле.")
        return get_object_or_404(Auto.objects.all(), id=_id)

    def perform_destroy(self, instance):
        instance.delete(force_policy=SOFT_DELETE_CASCADE)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise Http400(detail="Авто с таким vin уже существует, но было удалено.")

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise Http400(detail="Авто с таким vin уже существует, но было удалено.")


class ReportCreateUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView, generics.CreateAPIView):
    permission_classes = [IsUserAuthenticated]
    serializer_class = ReportCreateUpdateDestroySerializer

    def get_object(self):
        if 'id' in self.request.data:
            _id = self.request.data.get("id")
        elif 'id' in self.request.query_params:
            _id = self.request.query_params.get("id")
        else:
            raise Http400(detail="id - обязательное поле.")

        report = get_object_or_404(ReportPodbor.objects.all(), id=_id)
        has_user_permission_to_report(get_token_from_header(self.request), report)
        is_one_month_report(report)

        return report

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ReportSerializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if 'auto_id' not in self.request.data:
            raise Http400(detail="auto_id - обязательное поле.")
        serializer.save()
        instance = ReportPodbor.objects.get(id=serializer.data.get("id"))
        auto = get_object_or_404(Auto.objects.all(), id=serializer.data.get("auto_id"))
        instance.is_read = False
        instance.auto = auto
        instance.vin = auto.vin
        instance.executor = get_user_by_token(get_token_from_header(self.request))
        instance.save()
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(dict(id=obj.id), status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        serializer.save()
        instance = ReportPodbor.objects.get(id=serializer.data.get("id"))
        if 'auto_id' in self.request.data:
            auto = get_object_or_404(Auto.objects.all(), id=serializer.data.get("auto_id"))
            instance.auto = auto
            instance.vin = auto.vin
            instance.save()
        return instance

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_update(serializer)
        return Response(dict(id=obj.id))

    def perform_destroy(self, instance):
        instance.delete(force_policy=SOFT_DELETE_CASCADE)


class PhotoReportTypeView(generics.ListAPIView):
    permission_classes = [IsUserAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(make_list_for_response(report_constants.PHOTO_TYPE))


class PhotoReportView(generics.RetrieveAPIView):
    permission_classes = [IsUserAuthenticated]
    serializer_class = GetPhotoReportSerializers

    def get_object(self):
        serializer = self.get_serializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        report = get_object_or_404(ReportPodbor.objects.all(), id=self.request.query_params.get('id'))
        has_user_permission_to_report(get_token_from_header(self.request), report)
        return report

    def retrieve(self, request, *args, **kwargs):
        return Response(generate_photo_dict(report=self.get_object(),
                                            type_photo=request.query_params.get('type_photo')))


class UploadPhotoReportView(generics.CreateAPIView):
    permission_classes = [IsUserAuthenticated]
    serializer_class = UploadPhotoReportSerializer

    def perform_create(self, serializer):
        report = get_object_or_404(ReportPodbor, pk=int(self.request.data.get('report_podbor')))
        has_user_permission_to_report(get_token_from_header(self.request), report)
        is_one_month_report(report)

        photo = Photo.objects.create(photo_type=self.request.data.get('photo_type'), report_podbor=report)
        print('get photo size before save__!_!_!_!_!__!_!_!_!_!_', self.request.data.get("photo_file").size)
        photo.image.save(self.request.data.get("photo_file").name, self.request.data.get("photo_file"))
        photo.save()
        photo.image_small.generate()
        if not AutoPhoto.objects.filter(auto_id=report.auto.id):
            photo = Photo.objects.filter(report_podbor=report, photo_type=report_constants.PHOTOFRONTVIEWS).first()
            if photo:
                AutoPhoto.objects.create(auto_id=report.auto.id, image=photo.image)
            else:
                photo = Photo.objects.filter(report_podbor=report, photo_type=report_constants.PHOTOINSPECTION).first()
                if photo:
                    AutoPhoto.objects.create(auto_id=report.auto.id, image=photo.image)
        return photo

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(dict(photo_id=photo.id), status=status.HTTP_201_CREATED, headers=headers)


class DeletePhotoReportView(generics.DestroyAPIView):
    permission_classes = [IsUserAuthenticated]

    def get_object(self):
        if 'id' not in self.request.query_params:
            raise Http400(detail="id - обязательное поле.")

        photo = get_object_or_404(Photo.objects.all(), id=self.request.query_params.get('id'))
        has_user_permission_to_report(get_token_from_header(self.request), photo.report_podbor)
        is_one_month_report(photo.report_podbor)

        return photo
