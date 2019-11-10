"""django_exercises_manatal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from app.models import School, Student
from rest_framework import routers, serializers, viewsets
from django.contrib import admin
import uuid
from rest_framework_nested import routers


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'max_student']


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'school', 'first_name', 'last_name', 'student_identification']

    def create(self, validated_data):
        current_count = Student.objects.filter(school=validated_data.get('school')).count()
        max_count = School.objects.get(pk=validated_data.get('school').id).max_student
        if current_count >= max_count:
            raise serializers.ValidationError(("School's max student limit is reached"))
        validated_data.update({'student_identification': str(uuid.uuid4())[:20]})
        return Student.objects.create(**validated_data)

    def update(self, instance, validated_data):
        current_count = Student.objects.filter(school=validated_data.get('school')).count()
        max_count = School.objects.get(pk=validated_data.get('school').id).max_student
        if current_count > max_count:
            raise serializers.ValidationError(("School's max student limit is reached"))
        instance.school = validated_data.get('school', instance.school)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.student_identification = validated_data.get('student_identification', instance.student_identification)
        instance.save()
        return instance


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.filter(school=self.kwargs['school_pk'])

router = routers.DefaultRouter()
router.register(r'endpoint/schools', SchoolViewSet, base_name='schools')


school_router = routers.NestedSimpleRouter(router, r'endpoint/schools', lookup='school')
school_router.register(r'students', StudentViewSet, base_name='student')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^', include(school_router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
]
