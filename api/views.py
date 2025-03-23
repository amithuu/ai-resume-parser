from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Candidate, Job, MatchResult
from .serializers import CandidateSerializer, JobSerializer, MatchResultSerializer
from .utils import parse_resume_with_llm, parse_job_with_llm, match_candidate_to_job, generate_cover_letter
import pdfplumber
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class UploadResumeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if 'resume' not in request.FILES:
            return Response({'error': 'No resume file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['resume']
        candidate = Candidate.objects.create(resume_file=file)

        # Extract text from resume PDF
        with pdfplumber.open(file) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])

        # Parse using LLM
        parsed_data = parse_resume_with_llm(text)
        candidate.parsed_data = parsed_data
        candidate.name = parsed_data.get('name', 'Unknown Candidate')
        candidate.save()

        return Response(CandidateSerializer(candidate).data, status=status.HTTP_201_CREATED)


class PostJobView(APIView):
    def post(self, request):
        job = Job.objects.create(
            title=request.data['title'],
            description=request.data['description']
        )
        parsed_data = parse_job_with_llm(job.description)
        job.parsed_data = parsed_data
        job.save()
        return Response(JobSerializer(job).data)

class MatchView(APIView):
    def post(self, request):
        candidate = Candidate.objects.get(id=request.data['candidate_id'])
        job = Job.objects.get(id=request.data['job_id'])

        score, missing = match_candidate_to_job(candidate.parsed_data, job.parsed_data)

        result = MatchResult.objects.create(
            candidate=candidate,
            job=job,
            match_score=score,
            missing_skills=missing
        )
        return Response(MatchResultSerializer(result).data)

class GenerateCoverLetterView(APIView):
    def post(self, request):
        candidate = Candidate.objects.get(id=request.data['candidate_id'])
        job = Job.objects.get(id=request.data['job_id'])
        cover_letter = generate_cover_letter(candidate.parsed_data, job.parsed_data)
        return Response({"cover_letter": cover_letter})
