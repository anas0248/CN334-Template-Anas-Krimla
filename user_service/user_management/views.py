from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from user_management.models import *
from user_management.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        try:   
            new_user = User.objects.create_user(username=data['username'], password=data['password'])
        except:
            return JsonResponse({"error":"username already used."}, status=400)
        new_user.save()
        data['user'] = new_user.id
        customer_serializer = CustomerSerializer(data=data)
        if customer_serializer.is_valid():
            customer_serializer.save()
            return JsonResponse(customer_serializer.data, status=201)
        new_user.delete()
        return JsonResponse({"error":"data not valid"}, status=400)
    return JsonResponse({"error":"method not allowed."}, status=405)

class CustomerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        customer_data = Customer.objects.get(user=request.user)
        customer_serializer = CustomerSerializer(customer_data)
        content = {
            'data': customer_serializer.data
        }
        return Response(content)

class UserView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username:
            try:
                user = User.objects.get(username=username)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)  # <<-- many=True ถ้าเป็น list
            return Response(serializer.data, status=status.HTTP_200_OK)
        
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        payments = Payment.objects.filter(payment_owner=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response({'data': serializer.data})

    def post(self, request, format=None):
        data = request.data.copy()
        data['payment_owner'] = request.user.id
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class SummaryView(APIView):
    def get(self, request):
        total_customers = Customer.objects.count()

        summary_data = {
            "total_customers": total_customers,
        }

        return Response(summary_data, status=status.HTTP_200_OK)