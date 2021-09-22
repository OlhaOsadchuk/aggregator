from django.conf.urls import url

from aggregator.views.views_report import *
from aggregator.views.views_user import *
from  aggregator.views.views_support import *

urlpatterns = [
    url(r'^check_phone/', CheckPhoneView.as_view(), name="aggregator_check_phone"),
    url(r'^create_code/', CreateCodeView.as_view(), name="create_code"),
    url(r'^check_code/', CheckCodeView.as_view(), name="check_code"),

    url(r'^get_user_info/', GetUserInfoView.as_view(), name="get_user_info"),
    url(r'^get_user_equipment/', GetUserEquipment.as_view(), name="get_user_equipment"),

    url(r'^reports/', ReportListView.as_view(), name="reports"),
    url(r'^crud_report/', ReportCreateUpdateDestroyView.as_view(), name="crud_report"),
    url(r'^report_types/', ReportTypeListView.as_view(), name="report_types"),
    url(r'^report_statuses/', ReportStatusListView.as_view(), name="report_statuses"),

    url(r'^report_photos/', PhotoReportView.as_view(), name="report_photos"),
    url(r'^report_photos_type/', PhotoReportTypeView.as_view(), name="report_photos_type"),
    url(r'^upload_report_photos/', UploadPhotoReportView.as_view(), name="upload_report_photos"),
    url(r'^delete_report_photos/', DeletePhotoReportView.as_view(), name="delete_report_photos"),

    url(r'^autos_vin/', AutoVinListView.as_view(), name="autos_vin"),
    url(r'^body_types/', BodyTypeListView.as_view(), name="body_types"),
    url(r'^auto_years/', YearListView.as_view(), name="auto_years"),
    url(r'^marks_auto/', MarkAutoListView.as_view(), name="marks_auto"),
    url(r'^models_auto/', ModelAutoListView.as_view(), name="models_auto"),
    url(r'^generations_auto/', GenerationListView.as_view(), name="generations_auto"),
    url(r'^transmission_type/', TransmissionTypeListView.as_view(), name="transmission_type"),
    url(r'^engine_type/', EngineTypeListView.as_view(), name="engine_type"),
    url(r'^drive_type/', DriveTypeListView.as_view(), name="drive_type"),
    url(r'^author_type/', AuthorTypeListView.as_view(), name="author_type"),
    url(r'^engine_capacity/', EngineCapacityListView.as_view(), name="engine_capacity"),
    url(r'^cud_auto/', CreateUpdateDestroyAutoView.as_view(), name="cud_auto"),

    url(r'^support/', SupportView.as_view(), name="support")
]
