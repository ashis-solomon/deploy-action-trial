from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


from technicalquestions_api.models import QuizQuestion, ResultTest
from technicalquestions_api.api.serializers import QuizQuestionSerializer, ResultTestSerializer

import json
from random import sample
from collections import defaultdict

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np



class QuizQuestionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = QuizQuestionSerializer
    queryset = QuizQuestion.objects.all() 

class GenerateTechnicalQuestionsView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get(self, request):
        # Get all questions from the database grouped by subject
        questions_by_subject = defaultdict(list)
        for question in QuizQuestion.objects.all():
            questions_by_subject[question.subject].append(question)

        # Select 10 random questions for each subject
        questions = []
        for subject, subject_questions in questions_by_subject.items():
            questions += sample(subject_questions, 10)

        # Serialize the questions data to JSON
        data = [{
            'question_id': question.question_id,
            'topic': question.topic,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'correct_answer': question.correct_answer,
            'difficulty': question.difficulty,
            'cognitive_level': question.cognitive_level,
            'subject': question.subject,
        } for question in questions]

        # Return the questions data in a JSON response
        return Response(data)
    

class SimilarQuestionsView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def post(self, request):
        # Get list of wrong question ids from request body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        wrong_question_ids = body.get('ids', [])

        # Get all questions except the ones the user attempted wrong
        ex_questions = QuizQuestion.objects.filter(question_id__in=wrong_question_ids)
        print(ex_questions)
        questions = QuizQuestion.objects.exclude(question_id__in=wrong_question_ids)
        #print(questions)

        # Create a matrix of the question features (topic, subject, difficulty, cognitive level)
        feature_matrix = []
        ex_feature_matrix=[]
        for question in questions:
            #features = question.question+","+question.topic+","+question.option_a+","+question.option_b+","+question.option_c+","+question.option_d+","+ question.subject+","+question.difficulty+","+ question.cognitive_level
            #features = question.topic+","+ question.subject
            #features = question.topic
            features = question.topic+","+question.option_a+","+question.option_b+","+question.option_c+","+question.option_d+","+question.difficulty+","+ question.cognitive_level
            feature_matrix.append(features)
            
        for question in ex_questions:
            #features = question.question+","+question.topic+","+question.option_a+","+question.option_b+","+question.option_c+","+question.option_d+","+ question.subject+","+question.difficulty+","+ question.cognitive_level
            #features = question.question+","+question.topic+","+ question.subject+","+question.difficulty+","+ question.cognitive_level
            features = question.topic+","+question.option_a+","+question.option_b+","+question.option_c+","+question.option_d+","+question.difficulty+","+ question.cognitive_level
            #features = question.topic+","+ question.subject
            ex_feature_matrix.append(features)    
            
        #print(ex_feature_matrix)    
            

        # Calculate the cosine similarity matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(feature_matrix + ex_feature_matrix)

# calculate cosine similarity between tf-idf vectors
        cosine_similarities = cosine_similarity(tfidf_matrix[-len(ex_feature_matrix):], tfidf_matrix[:-len(ex_feature_matrix)])

        # get the most similar elements using cosine similarity
        similar_indices = cosine_similarities.argsort()[:, ::-1][0][:40]
        similar_elements = [feature_matrix[i] for i in similar_indices]

        print(similar_elements)
        indices = [i for i in range(len(feature_matrix)) if feature_matrix[i] in similar_elements]

        print(indices)
        print("hey")
        # vectorizer = TfidfVectorizer()
        # transformed = vectorizer.fit_transform(feature_matrix)
        # similarity_matrix = cosine_similarity(transformed)
        # print(similarity_matrix)
        # print(type(similarity_matrix))
        # print(len(similarity_matrix))
        # print(len(similarity_matrix[0]))

        # Get the indices of the top 40 most similar questions
        #flat_indices = similarity_matrix.flatten().argsort()[::-1][:40]
        #print(flat_indices)
        #top_indices = [(index // similarity_matrix.shape[1], index % similarity_matrix.shape[1]) for index in flat_indices]
        #print(top_indices)

        # Get the actual questions corresponding to the top indices
        #top_questions = [list(questions)[i] for i in [index[1] for index in top_indices]]
        #print(top_questions)
        
        # flat_indices = similarity_matrix.flatten().argsort()[::-1][:40]
        # top_indices = [(index // similarity_matrix.shape[1], index % similarity_matrix.shape[1]) for index in flat_indices]

        #     # Get the actual question ids corresponding to the top indices
        top_questions = [questions[i].question_id for i in indices]
        print(top_questions)
        print("hello")

        # Convert the questions to a JSON response
        data = {
            'questions': [{
                'question_id': question.question_id,
                'topic': question.topic,
                'question': question.question,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'correct_answer': question.correct_answer,
                'difficulty': question.difficulty,
                'cognitive_level': question.cognitive_level,
                'subject': question.subject
            } for question in questions.filter(question_id__in=top_questions)]
        }
        return Response(data, status=status.HTTP_200_OK)
    

class ProvideQuestionsView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def post(self, request):
        # Get list of wrong question ids from request body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        question_ids = body.get('ids', [])

        # Get all questions except the ones the user attempted wrong
        questions = QuizQuestion.objects.filter(question_id__in=question_ids)
        #print(questions)
        data = []
        for question in questions:
            data.append({
                'question_id': question.question_id,
                'topic': question.topic,
                'question': question.question,
                'options': [
                    question.option_a,
                    question.option_b,
                    question.option_c,
                    question.option_d,
                ],
                'correct_answer': question.correct_answer,
                'difficulty': question.difficulty,
                'cognitive_level': question.cognitive_level,
                'subject': question.subject,
            })
        return JsonResponse({'questions': data})    
        
        
class ResultTestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    serializer_class = ResultTestSerializer

    def get_queryset(self):
        # print(self.request.user)
        return ResultTest.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ResultTestSerializer(data=request.data)
        if serializer.is_valid():
            test = serializer.save()
            serializer = ResultTestSerializer(test)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResultTestUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultTestSerializer

    def get_queryset(self):
        print(self.request.user)
        return ResultTest.objects.filter(user=self.request.user)
    

class ResultTestUserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultTestSerializer

    def get_object(self):
        queryset = ResultTest.objects.filter(user=self.request.user)
        obj = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        return obj