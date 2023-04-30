from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404


from jobscrape_api.models import JobLanguage, JobFramework, JobDatabase, JobSkill, ScrapeJob, ScrapeResult
from jobscrape_api.api.serializers import JobLanguageSerializer, JobFrameworkSerializer, JobDatabaseSerializer, JobSkillSerializer, ScrapeJobsListSerializer, ScrapeResultSerializer


class JobLanguageList(generics.ListAPIView):
    serializer_class = JobLanguageSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return JobLanguage.objects.filter(language__icontains=query)
        return JobLanguage.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [language['language'] for language in serializer.data]
        return Response(data)


class JobFrameworkList(generics.ListAPIView):
    serializer_class = JobFrameworkSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return JobFramework.objects.filter(framework__icontains=query)
        return JobFramework.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [framework['framework'] for framework in serializer.data]
        return Response(data)


class JobDatabaseList(generics.ListAPIView):
    serializer_class = JobDatabaseSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return JobDatabase.objects.filter(database__icontains=query)
        return JobDatabase.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [database['database'] for database in serializer.data]
        return Response(data)


class JobSkillList(generics.ListAPIView):
    serializer_class = JobSkillSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return JobSkill.objects.filter(skill__icontains=query)
        return JobSkill.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [skill['skill'] for skill in serializer.data]
        return Response(data)
    


class ScrapeJobsList(generics.ListAPIView):
    serializer_class = ScrapeJobsListSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return ScrapeJob.objects.filter(job_name__icontains=query)
        return ScrapeJob.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [job_name['job_name'] for job_name in serializer.data]
        return Response(data)


# add more methods - nothing for now
class ScrapeResultListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = ScrapeResultSerializer

    def get_queryset(self):
        return ScrapeResult.objects.all()


class ScrapeResultRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = ScrapeResultSerializer

    # IMPLEMENT COSINE
    
    def get_object(self):
        job_name = self.kwargs.get('job_name')
        obj = get_object_or_404(ScrapeResult, job_name__job_name=job_name)  
        return obj