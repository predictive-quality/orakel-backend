from ..models import User
from rest_framework import serializers, viewsets, response, status

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    

class UserViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    allowed_methods = ("GET","OPTIONS", "HEAD")

    def list(self, request):
        r = {}
        for q in User.objects.values("username", "first_name", "last_name"):
            r[q["username"]] =  q["first_name"] + " " + q["last_name"]
        return response.Response(r)
