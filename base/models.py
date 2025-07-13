from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.core.exceptions import ValidationError

import random
from datetime import datetime
import string


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    current_address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True)
    pan_card = models.CharField(max_length=20, unique=True)
    aadhar_card = models.CharField(max_length=12, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    account_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=500.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def Number_checkSum(Numbe_str):
        digits = [int(_) for _ in Numbe_str]
        for i in range(len(digits) - 1, -1, -2):
            doubled = digits[i] * 2
            digits[i] = doubled if doubled < 10 else doubled - 9
        total = sum(digits)
        return (10 - total % 10) % 10

    @classmethod
    def AccountNumber(cls):
        Account_CreateTime = datetime.now()
        preFix = f"{Account_CreateTime.year % 100}{Account_CreateTime.month:02d}{Account_CreateTime.day:02d}"
        random_digits = ''.join(random.choices(string.digits, k=7))
        baseNumber = f"{preFix}{random_digits}"
        checkDigit = cls.Number_checkSum(baseNumber)
        AccountNumber = f"{baseNumber}{checkDigit}"
        assert cls.ValidateAccountNumber(AccountNumber), f"Generated invalid account number: {AccountNumber}"

        while cls.objects.filter(account_number=AccountNumber).exists():
            random_digits = ''.join(random.choices(string.digits, k=7))
            baseNumber = f"{preFix}{random_digits}"
            checkDigit = cls.Number_checkSum(baseNumber)
            AccountNumber = f"{baseNumber}{checkDigit}"

        return AccountNumber

    @classmethod
    def ValidateAccountNumber(cls, AccountNumber):
        checkDigit = int(AccountNumber[-1])
        number_to_check = AccountNumber[:-1]
        calculated_check_digit = cls.Number_checkSum(number_to_check)
        return checkDigit == calculated_check_digit

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = UserData.AccountNumber()
        super().save(*args, **kwargs)
    
    def can_transfer(self, amount):
        return self.available_balance >= Decimal(str(amount)) and  self.is_active

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Transaction_History(models.Model):
    TRANSACTION_TYPES = [
        ('TRANSFER_SENT', 'transfer_Sent'),
        ('TRANSFER_RECEIVED', 'transfer_Received'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_Name = models.CharField(max_length=20, default="Money Pay")
    recipient_account = models.CharField(max_length=20)
    transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPES)
    recipient_name = models.CharField(max_length=20)


    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = str(uuid.uuid4())[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"
    


class MoneyTransfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    transfer_id = models.CharField(max_length=50, unique=True)
    sender = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='sent_transfers')
    receiver = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    sender_transaction = models.ForeignKey(
        Transaction_History, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sender_transfer'
    )
    receiver_transaction = models.ForeignKey(
        Transaction_History, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='receiver_transfer'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.transfer_id:
            import uuid
            self.transfer_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transfer_id} - {self.sender.account_number} to {self.receiver.account_number}"