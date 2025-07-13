from django.shortcuts import render
from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
from werkzeug.security import generate_password_hash, check_password_hash
from django.contrib.auth.models import User
from .models import UserAccount

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.create(
                email=data['Email'],
                phone_number=data['PhoneNumber'],
                password=generate_password_hash(data['Password'])
            )
            user_account = UserAccount.objects.create(
                user=user,
                phone_Number=data['PhoneNumber']
            )
            return JsonResponse({'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)