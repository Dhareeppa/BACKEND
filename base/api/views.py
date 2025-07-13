from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from base import models
from .serializers import UserRegisterSerializer

from .serializers import RegisterSerializers
from base.models import UserData, MoneyTransfer

from .serializers import UserSerializers

from base.models import User

from .serializers import Transaction_HistorySerializer

from base.models import Transaction_History

from .serializers import TransactionSerializer
from .serializers import (MoneyTransferRequestSerializer, AccountLookupSerializer, 
    AccountInfoSerializer, TransferResponseSerializer,
    MoneyTransferSerializer, EnhancedTransactionSerializer,
    UpdatedUserSerializers, BalanceSerializer)

from .transaction import MoneyTransferService 


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def Get_Route(request):
    routes = [
        'api/token',
        'api/token/refresh',
    ]
    return Response(routes)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register_view(request):
    serializer = UserRegisterSerializer(data=request.data)
    try:
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "username": user.username
            })
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializers(data=request.data)
    try:
        if serializer.is_valid():

            username = serializer.validated_data.get('username')
            if not username:
                return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'User not found. Please register first.'}, status=status.HTTP_404_NOT_FOUND)

            pan_card = serializer.validated_data.get('pan_card', '').strip()
            aadhar_card = serializer.validated_data.get('aadhar_card', '').strip()

            if UserData.objects.filter(pan_card=pan_card).exclude(user=user).exists():
                return Response({'error': 'PAN card already exists for another user.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if UserData.objects.filter(aadhar_card=aadhar_card).exclude(user=user).exists():
                return Response({'error': 'Aadhar card already exists for another user.'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                existing_userdata = UserData.objects.get(user=user)
                if existing_userdata.first_name:
                    return Response({'error': 'User already has a complete account'},
                                    status=status.HTTP_400_BAD_REQUEST)

                existing_userdata.first_name = serializer.validated_data.get('first_name', '')
                existing_userdata.middle_name = serializer.validated_data.get('middle_name', '')
                existing_userdata.last_name = serializer.validated_data.get('last_name', '')
                existing_userdata.date_of_birth = serializer.validated_data.get('date_of_birth')
                existing_userdata.current_address = serializer.validated_data.get('current_address', '')
                existing_userdata.phone_number = serializer.validated_data.get('phone_number', '')
                existing_userdata.pan_card = pan_card
                existing_userdata.aadhar_card = aadhar_card
                existing_userdata.profile_image = serializer.validated_data.get('profile_image', None)
                existing_userdata.save()
                user_account = existing_userdata

            except UserData.DoesNotExist:
                if hasattr(request.user, 'account'):
                    return Response({'error': 'User already has an account'}, status=status.HTTP_400_BAD_REQUEST)
                user_account = UserData.objects.create(
                    user=user,
                    first_name=serializer.validated_data.get('first_name', ''),
                    middle_name=serializer.validated_data.get('middle_name', ''),
                    last_name=serializer.validated_data.get('last_name', ''),
                    date_of_birth=serializer.validated_data.get('date_of_birth', ''),
                    current_address=serializer.validated_data.get('current_address', ''),
                    phone_number=serializer.validated_data.get('phone_number', ''),
                    pan_card=serializer.validated_data.get('pan_card', ''),
                    aadhar_card=serializer.validated_data.get('aadhar_card', ''),
                    available_balance=500.00,
                    profile_image=serializer.validated_data.get("profile_image", None),
                )

            return Response({
                'message': 'User Account created successfully',
                'account_number': user_account.account_number
            }, status=status.HTTP_201_CREATED)

    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetData(request):
    try:
        user_data = UserData.objects.all()
        if not user_data:
            return Response({'error': 'User account not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializers(user_data, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_logged_in_user_data(request):
    try:
        user_data = UserData.objects.get(user=request.user)
        serializer = UserSerializers(user_data)
        return Response(serializer.data)
    except UserData.DoesNotExist:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def transaction(request):
    serializer = Transaction_HistorySerializer(data=request.data)
    try:
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            if not username:
                return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'User not found. Please register first.'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                existing_Transaction = Transaction_History.objects.get(user=user)
                if existing_Transaction.account_Number:
                    return Response({'error': 'User already has a complete account'},
                                     status=status.HTTP_400_BAD_REQUEST)
                
                existing_Transaction.bank_Name = serializer.validated_data.get('bank_name', ''),
                existing_Transaction.recipient_account = serializer.validated_data.get('recipient_account', ''),
                existing_Transaction.recipient_name = serializer.validated_data.get('recipient_name', ''),
                existing_Transaction.transaction_type = serializer.validated_data.get('transaction_type', ''),
                existing_Transaction.amount = serializer.validated_data.get('amount', ''),
                existing_Transaction.balance_before = serializer.validated_data.get('balance_before', ''),
                existing_Transaction.balance_after = serializer.validated_data.get('balance_after', ''),
                existing_Transaction.description = serializer.validated_data.get('description', ''),
                existing_Transaction.transaction_id = serializer.validated_data.get('transaction_id', ''),
                existing_Transaction.reference_number = serializer.validated_data.get('reference_number', ''),
                existing_Transaction.transaction_date = serializer.validated_data.get('transaction_date', ''),
                existing_Transaction.save()
                user_transaction=existing_Transaction
                
            except Transaction_History.DoesNotExist:
                if hasattr(request.user, 'account'):
                    return Response({'error': 'User already has an account'}, status=status.HTTP_400_BAD_REQUEST)
                user_transaction = Transaction_History.objects.create(
                    user=user,
                    bank_Name = serializer.validated_data.get('bank_name', ''),
                    recipient_account = serializer.validated_data.get('recipient_account', ''),
                    transaction_type = serializer.validated_data.get('transaction_type', ''),
                    recipient_name = serializer.validated_data.get('recipient_name', ''),
                    amount = serializer.validated_data.get('amount', ''),
                    balance_before = serializer.validated_data.get('balance_before', ''),
                    balance_after = serializer.validated_data.get('balance_after', ''),
                    description = serializer.validated_data.get('description', ''),
                    transaction_id = serializer.validated_data.get('transaction_id', ''),
                    reference_number = serializer.validated_data.get('reference_number', ''),
                    transaction_date = serializer.validated_data.get('transaction_date', ''),
                    )
                return Response({
                        'message': 'User existing_Transaction created successfully',
                        'account_number': user_transaction.account
                    }, status=status.HTTP_201_CREATED)
        
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Get_transaction(request):
    try:
        transaction_data = Transaction_History.objects.filter(user=request.user)
        if not transaction_data.exists():
            return Response({'message': 'No received transactions found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction_data, many=True)
        return Response(serializer.data)
    except Transaction_History.DoesNotExist:
        return Response({'error': 'transaction not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Get_Receive_transaction(request):
    try:
        transactions = Transaction_History.objects.filter(
            user=request.user,
            transaction_type="TRANSFER_RECEIVED").order_by('-transaction_date')
        
        if not transactions.exists():
            return Response({'message': 'No received transactions found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransactionSerializer(transactions, many=True)
        return Response({'transactions': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_money(request):
    try:
        try:
            sender_account = UserData.objects.get(user=request.user, is_active=True)
        except UserData.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Your account not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MoneyTransferRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        receiver_account_result = MoneyTransferService.get_account_by_number(
            serializer.validated_data['receiver_account_number']
        )
        
        if not receiver_account_result['success']:
            return Response({
                'success': False,
                'error': receiver_account_result['error']
            }, status=status.HTTP_404_NOT_FOUND)
        
        result = MoneyTransferService.transfer_money(
            sender_account_number=sender_account.account_number,
        recipient_name=serializer.validated_data.get('recipient_name', ''),
            receiver_account_number=serializer.validated_data['receiver_account_number'],
            amount=serializer.validated_data['amount'],
            description=serializer.validated_data.get('description', '')
        )
        
        if result['success']:
            response_data = {
                'success': True,
                'message': 'Transfer completed successfully',
                'transaction_id': result['transaction_id'],
                'sender_new_balance': result['sender_new_balance'],
                'receiver_account': serializer.validated_data['receiver_account_number'],
                'amount': serializer.validated_data['amount'],
                'transfer_details': MoneyTransferSerializer(result['transfer']).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Transfer failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_balance(request):
    try:
        user_data = UserData.objects.get(user=request.user, is_active=True)
        
        response_data = {
            'available_balance': user_data.available_balance,
            'account_number': user_data.account_number,
            'account_holder': f"{user_data.first_name} {user_data.last_name}",
            'last_updated': user_data.updated_at
        }
        
        serializer = BalanceSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except UserData.DoesNotExist:
        return Response({
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_account_by_number(request):
    account_number = request.GET.get('account_number')
    
    if not account_number:
        return Response({
            'error': 'Account number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = MoneyTransferService.get_account_by_number(account_number)
    
    if result['success']:
        return Response({
            'found': True,
            'account_holder': result['account_holder'],
            'account_number': result['account_number']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'found': False,
            'message': result['error']
        }, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enhanced_transaction_history(request):
    try:
        user_data = UserData.objects.get(user=request.user, is_active=True)
    
        limit = int(request.GET.get('limit', 50))
        limit = min(limit, 100)  
        
        transactions = Transaction_History.objects.filter(
            user=request.user
        ).order_by('-transaction_date')[:limit]
        
        transfer_result = MoneyTransferService.get_transfer_history(request.user, limit)
        transaction_data = EnhancedTransactionSerializer(transactions, many=True).data
        
        response_data = {
            'success': True,
            'transactions': transaction_data,
            'current_balance': user_data.available_balance,
            'account_number': user_data.account_number,
            'total_count': len(transaction_data)
        }
        
        if transfer_result['success']:
            response_data['transfers'] = MoneyTransferSerializer(
                transfer_result['transfers'], many=True
            ).data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except UserData.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to get transaction history: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transfer_details(request, transfer_id):
    try:
        user_data = UserData.objects.get(user=request.user, is_active=True)
        transfer = MoneyTransfer.objects.get(
            models.Q(sender=user_data) | models.Q(receiver=user_data),
            transfer_id=transfer_id
        )
        
        serializer = MoneyTransferSerializer(transfer)
        transfer_data = serializer.data
        if transfer.sender.id == user_data.id:
            transfer_data['user_role'] = 'sender'
        else:
            transfer_data['user_role'] = 'receiver'
            
        return Response({
            'success': True,
            'transfer': transfer_data
        }, status=status.HTTP_200_OK)
        
    except MoneyTransfer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Transfer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except UserData.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_updated_user_data(request):
    try:
        user_data = UserData.objects.get(user=request.user)
        serializer = UpdatedUserSerializers(user_data)
        return Response(serializer.data)
    except UserData.DoesNotExist:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)