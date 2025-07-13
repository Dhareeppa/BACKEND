from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from base import models
from django.db import models
from base.models import UserData, Transaction_History, MoneyTransfer



class MoneyTransferService:
    @staticmethod
    def transfer_money(sender_account_number, receiver_account_number, amount, description="", recipient_name=""):
        try:
            with db_transaction.atomic():
                sender = UserData.objects.select_for_update().get(
                    account_number = sender_account_number,
                    is_active=True
                )
                receiver = UserData.objects.select_for_update().get(
                    account_number = receiver_account_number,
                    is_active=True
                )
                
                amount = Decimal(str(amount))

                if sender_account_number == receiver_account_number:
                    raise ValidationError("Cannot transfer to tha same Account")
                
                if amount <=0:
                    raise ValidationError("Transfer amount must be positive")
                
                if not sender.can_transfer(amount):
                    raise ValidationError("Insufficient balance or account inactive")
                
                sender_balance_before = sender.available_balance
                receiver_balance_before = receiver.available_balance

                transfer = MoneyTransfer.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    description=description,
                    status="PENDING"
                )
                
                sender.available_balance -= amount
                receiver.available_balance += amount

                sender_transaction = Transaction_History.objects.create(
                    user=sender.user,
                    transaction_type = "TRANSFER_SENT",
                    recipient_account= receiver.account_number,
                    recipient_name=recipient_name or f"{sender.first_name} {sender.last_name}",
                    amount = amount,
                    balance_before = sender_balance_before,
                    balance_after = sender.available_balance,
                    status = "COMPLETED",
                    description = description or f"Transfer to {receiver.account_number}",
                    reference_number = transfer.transfer_id  
                )

                receiver_transaction = Transaction_History.objects.create(
                    user=receiver.user,
                    transaction_type = "TRANSFER_RECEIVED",
                    recipient_account=sender.account_number,
                    recipient_name=f"{receiver.first_name} {receiver.last_name}", 
                    amount=  amount,
                    balance_before=receiver_balance_before,
                    balance_after = receiver.available_balance,
                    status = "COMPLETED",
                    description=description or f"Transfer form {sender.account_number}",
                    reference_number = transfer.transfer_id  
                )

                transfer.sender_transaction = sender_transaction
                transfer.receiver_transaction = receiver_transaction
                transfer.status = "COMPLETED"
                transfer.completed_at = timezone.now()
                transfer.save()

                sender.save()
                receiver.save()

                return {
                    'success':True,
                    'transfer':transfer,
                    'sender_new_balance': sender.available_balance,
                    'receiver_new_balance': receiver.available_balance,
                    'transaction_id': transfer.transfer_id
                }
        except UserData.DoesNotExist:
            return{
                'success':False,
                'error':'Account not found or inactive'
            }
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Transfer failed: {str(e)}'
            }
        
    @staticmethod
    def get_account_by_number(account_number):
        try:
            account = UserData.objects.get(
                account_number=account_number,
                is_active=True
            ) 
            return {
                'success':True,
                'account':account,
                'account_holder_Name':f"{account.first_name} {account.last_name}",
                'account_Number':account.account_number
            }
        except UserData.DoesNotExist:
            return{
                'success':False,
                'error':'Account not found'
            }
        
    @staticmethod
    def get_transfer_history(user, limit=50):
        try:
            user_data = UserData.objects.get(user=user)
            transfers = MoneyTransfer.objects.filter(
                models.Q(sender=user_data) | models.Q(receiver=user_data),
                status = "COMPLETED"
            ) .order_by('-created_at')[:limit]
            return {
            'success': True,
            'transfers': transfers,
            'user_account': user_data
        }
        except UserData.DoesNotExist:
            return {
                'success': False,
                'error': 'User account not found'
            }