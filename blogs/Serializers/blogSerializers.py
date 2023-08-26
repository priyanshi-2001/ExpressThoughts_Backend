from rest_framework import serializers
from ..models import BlogsData,Comments,Likes

class BlogsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogsData
        fields = ['description', 'dateCreated','id','userId','dateModified']

class LikesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['blogId','id','userId','dateCreated']

class CommentsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['blogId','id','userId','dateCreated','description']