from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User 
from django.contrib.auth.password_validation import validate_password
from base.models import UserData
from decimal import Decimal
from base.models import Transaction_History,MoneyTransfer


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        phone_number = validated_data['phone_number']

        user = User.objects.create_user(
            username=username,
            password=password,
            is_superuser=False,
            is_staff=False,
            is_active=True
        )
          
        return user


class UserSerializers(ModelSerializer):
    class Meta:
        model = UserData                                                                     
        fields = ['id','first_name', 'middle_name', 'last_name', 'date_of_birth', 
                 'current_address', 'phone_number', 'pan_card', 'aadhar_card', 
                 'profile_image', 'account_number', 'available_balance', 'created_at', 'updated_at']
        
        extra_kwargs = {
            'account_number': {'required': False},
            'available_balance': {'required': False},
        }
        
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        def get_username(self, obj):
            return obj.user.username


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction_History
        fields ="__all__"


class Transaction_HistorySerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    bank_Name = serializers.CharField(required=True)
    recipient_account  = serializers.CharField(required=True)
    transaction_type = serializers.CharField(required=True)
    recipient_name = serializers.CharField(required=True)

    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)  
    balance_before = serializers.CharField(required=True)
    balance_after = serializers.CharField(required=True)
    
    description = serializers.CharField(required=True)
    transaction_id = serializers.CharField(required=True)
    reference_number = serializers.CharField(required=True)
    transaction_date = serializers.CharField(required=True)
     

    

class RegisterSerializers(serializers.Serializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    current_address = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)    
    pan_card = serializers.CharField(required=True)
    aadhar_card = serializers.CharField(required=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    




class MoneyTransferRequestSerializer(serializers.Serializer):
    recipient_name = serializers.CharField(max_length=20)
    receiver_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=("0.01")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        if value > 1000000:  
            raise serializers.ValidationError("Amount exceeds maximum transfer limit")
        return value

class AccountLookupSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=20)

class AccountInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserData
        fields = ['account_number', 'full_name', 'available_balance']
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class TransferResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    transaction_id = serializers.CharField(required=False)
    sender_new_balance = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    receiver_new_balance = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

class MoneyTransferSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name', read_only=True)
    sender_account = serializers.CharField(source='sender.account_number', read_only=True)
    receiver_name = serializers.CharField(source='receiver.first_name', read_only=True)
    receiver_account = serializers.CharField(source='receiver.account_number', read_only=True)
    
    class Meta:
        model = MoneyTransfer
        fields = [
            'transfer_id', 'amount', 'status', 'description', 'reference_number',
            'created_at', 'completed_at', 'sender_name', 'sender_account',
            'receiver_name', 'receiver_account'
        ]


class EnhancedTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction_History
        fields = [
            'id', 'transaction_id', 'transaction_type', 'transaction_type_display',
            'amount', 'balance_before', 'balance_after', 'status', 'status_display',
            'description', 'reference_number', 'recipient_account', 'recipient_name',
            'sender_account', 'sender_name', 'transaction_date', 'created_at'
        ]


class UpdatedUserSerializers(ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserData
        fields = [
            'id', 'username', 'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'current_address', 'phone_number', 'pan_card', 
            'aadhar_card', 'profile_image', 'account_number', 'available_balance', 
            'is_active', 'created_at', 'updated_at'
        ]
        
        extra_kwargs = {
            'account_number': {'read_only': True},
            'available_balance': {'read_only': True},
        }
        
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BalanceSerializer(serializers.Serializer):
    available_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    account_number = serializers.CharField()
    account_holder = serializers.CharField()
    last_updated = serializers.DateTimeField()
    
    