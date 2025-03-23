from django.urls import path
from .views import UploadResumeView, PostJobView, MatchView, GenerateCoverLetterView

urlpatterns = [
    path('upload-resume/', UploadResumeView.as_view()),
    path('post-job/', PostJobView.as_view()),
    path('match/', MatchView.as_view()),
    path('generate-cover-letter/', GenerateCoverLetterView.as_view()),
]
