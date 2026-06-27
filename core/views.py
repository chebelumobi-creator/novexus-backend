# from django.shortcuts import render
# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.response import Response
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import User, Transaction, SystemSettings, OTP, IMF, AccountRestriction, UserSecuritySettings
# from .serializers import RegisterSerializer, UserSerializer, TransactionSerializer
# import uuid
# import random
# import string
# from decimal import Decimal
# from datetime import timedelta
# from django.utils import timezone
# import requests


# # ==================== CURRENCY CONVERSION FUNCTIONS ====================


# def get_currency_code(country_name):
#     """Get currency code from country name using manual mapping"""
#     currency_map = {
#         'russia': 'RUB',
#         'vietnam': 'VND',
#         'laos': 'LAK',
#         'myanmar': 'MMK',
#         'ukraine': 'UAH',
#         'cambodia': 'KHR',
#         'portugal': 'EUR',
#         'portuguese': 'EUR',
#         'philippines': 'PHP',
#         'japan': 'JPY',
#         'singapore': 'SGD',
#         'brunei': 'BND',
#         'united states': 'USD',
#         'usa': 'USD',
#         'us': 'USD',
#         'united kingdom': 'GBP',
#         'uk': 'GBP',
#         'china': 'CNY',
#         'india': 'INR',
#         'canada': 'CAD',
#         'australia': 'AUD',
#         'germany': 'EUR',
#         'france': 'EUR',
#         'italy': 'EUR',
#         'spain': 'EUR',
#         'brazil': 'BRL',
#         'mexico': 'MXN',
#         'south africa': 'ZAR',
#         'turkey': 'TRY',
#         'south korea': 'KRW',
#         'indonesia': 'IDR',
#         'malaysia': 'MYR',
#         'thailand': 'THB',
#         'pakistan': 'PKR',
#         'bangladesh': 'BDT',
#         'egypt': 'EGP',
#         'saudi arabia': 'SAR',
#         'uae': 'AED',
#         'switzerland': 'CHF',
#         'sweden': 'SEK',
#         'norway': 'NOK',
#         'denmark': 'DKK',
#         'poland': 'PLN',
#         'israel': 'ILS',
#     }
    
#     country_lower = country_name.lower().strip()
#     for key, code in currency_map.items():
#         if key in country_lower:
#             return code
#     return None


# def get_currency_symbol(currency_code):
#     """Get currency symbol from currency code"""
#     symbols = {
#         'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥',
#         'VND': '₫', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$',
#         'GHS': '₵', 'KES': 'KSh', 'ZAR': 'R', 'TRY': '₺', 'RUB': '₽',
#         'KRW': '₩', 'BRL': 'R$', 'MXN': '$', 'SGD': 'S$', 'CHF': 'CHF',
#         'IDR': 'Rp', 'MYR': 'RM', 'THB': '฿', 'PHP': '₱', 'PKR': '₨',
#         'BDT': '৳', 'EGP': 'E£', 'SAR': '﷼', 'AED': 'د.إ', 'SEK': 'kr',
#         'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł', 'ILS': '₪',
#         'LAK': '₭', 'MMK': 'K', 'UAH': '₴', 'KHR': '៛', 'BND': 'B$'
#     }
#     return symbols.get(currency_code, currency_code)
    


# def convert_currency(amount, from_currency, to_currency):
#     """Convert amount using ExchangeRate-API"""
#     try:
#         url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             rate = data['rates'].get(to_currency)
#             if rate:
#                 return float(amount) * rate
#         return None
#     except Exception as e:
#         print(f"Error converting currency: {e}")
#         return None


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register(request):
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         UserSecuritySettings.objects.get_or_create(user=user)
#         return Response({'message': 'Account created successfully', 'account_number': user.account_number}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def profile(request):
#     serializer = UserSerializer(request.user)
#     return Response(serializer.data)


# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_profile(request):
#     serializer = UserSerializer(request.user, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def transfer(request):
#     user = request.user
#     data = request.data

#     pin = data.get('pin')
#     if pin != user.transaction_pin:
#         return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

#     amount = Decimal(str(data.get('amount', 0)))

#     if amount <= 0:
#         return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

#     if amount > user.balance:
#         return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

#     if amount > user.daily_transfer_limit:
#         return Response({'error': f'Amount exceeds daily limit of ${user.daily_transfer_limit}'}, status=status.HTTP_400_BAD_REQUEST)

#     reference = 'RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10]

#     user.balance -= amount
#     user.save()

#     transaction = Transaction.objects.create(
#         sender=user,
#         recipient_name=data.get('recipient_name'),
#         recipient_email=data.get('recipient_email'),
#         recipient_bank=data.get('recipient_bank'),
#         recipient_account=data.get('recipient_account'),
#         amount=amount,
#         transaction_type='transfer',
#         status='completed',
#         reference=reference,
#         description=data.get('description', ''),
#     )

#     # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#     # send_mail(
#     #     subject='Transfer Successful - Novexus Finance Bank',
#     #     message=f'Dear {user.username},\n\nYour transfer of ${amount} to {data.get("recipient_name")} ({data.get("recipient_bank")}) was successful.\n\nReference: {reference}\n\nThank you for banking with Novexus Finance Bank.',
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     recipient_list=[user.email],
#     #     fail_silently=True,
#     # )

#     # send_mail(
#     #     subject='You have received money - Novexus Finance Bank',
#     #     message=f'Dear {data.get("recipient_name")},\n\nYou have received ${amount} from {user.username} via Novexus Finance Bank.\n\nReference: {reference}\n\nThank you.',
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     recipient_list=[data.get('recipient_email')],
#     #     fail_silently=True,
#     # )

#     serializer = TransactionSerializer(transaction)
#     return Response({'message': 'Transfer successful', 'transaction': serializer.data}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def transaction_history(request):
#     transactions = Transaction.objects.filter(sender=request.user).order_by('-created_at')
#     serializer = TransactionSerializer(transactions, many=True)
#     return Response(serializer.data)


# def validate_and_prepare_transfer(request, transfer_type):
#     user = request.user
#     data = request.data

#     user_settings, created = UserSecuritySettings.objects.get_or_create(user=user)

#     if user_settings.is_restricted:
#         reason = user_settings.restriction_reason or "Your account has been restricted."
#         return Response({'error': f'Account restricted: {reason}'}, status=status.HTTP_403_FORBIDDEN)

#     pin = data.get('pin')
#     if pin != user.transaction_pin:
#         return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

#     amount = Decimal(str(data.get('amount', 0)))
#     if amount <= 0:
#         return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

#     if amount > user.balance:
#         return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

#     if amount > user.daily_transfer_limit:
#         return Response({'error': f'Amount exceeds daily limit of ${user.daily_transfer_limit}'}, status=status.HTTP_400_BAD_REQUEST)

#     if user_settings.imf_enabled:
#         imf_code = data.get('imf_code')
#         if not imf_code:
#             return Response({'requires_imf': True, 'message': 'IMF code required'}, status=status.HTTP_200_OK)

#         try:
#             imf = IMF.objects.get(user=user, code=imf_code, is_active=True)
#         except IMF.DoesNotExist:
#             return Response({'error': 'Invalid IMF code'}, status=status.HTTP_400_BAD_REQUEST)

#     reference = 'RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10]

#     transaction_data = {
#         'sender': user,
#         'recipient_name': data.get('recipient_name'),
#         'recipient_email': data.get('recipient_email', ''),
#         'recipient_bank': data.get('recipient_bank'),
#         'recipient_account': data.get('recipient_account'),
#         'amount': amount,
#         'transaction_type': 'transfer',
#         'transfer_type': transfer_type,
#         'status': 'pending',
#         'reference': reference,
#         'description': data.get('description', ''),
#     }

#     if transfer_type == 'wire':
#         transaction_data['swift_code'] = data.get('swift_code', '')
#         transaction_data['country'] = data.get('country', '')

#     transaction = Transaction.objects.create(**transaction_data)

#     if user_settings.otp_enabled:
#         otp_code = str(random.randint(100000, 999999)).zfill(6)
#         otp = OTP.objects.create(
#             user=user,
#             code=otp_code,
#             transaction_id=transaction.id
#         )

#         return Response({
#             'requires_otp': True,
#             'otp_id': otp.id,
#             'transaction_id': transaction.id,
#             'message': 'OTP generated. Check admin panel for code.'
#         }, status=status.HTTP_200_OK)

#     if user_settings.pending_approval_enabled:
#         return Response({
#             'status': 'pending',
#             'message': 'Transfer submitted for admin approval. You will be notified once approved.',
#             'transaction_id': transaction.id,
#             'reference': reference
#         }, status=status.HTTP_200_OK)

#     user.balance -= amount
#     user.save()
#     transaction.status = 'completed'
#     transaction.save()

#     return {
#         'completed': True,
#         'transaction': transaction,
#         'amount': amount,
#         'reference': reference,
#         'user': user,
#         'data': data
#     }


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def domestic_transfer(request):
#     result = validate_and_prepare_transfer(request, 'domestic')
    
#     if not isinstance(result, dict) or 'completed' not in result:
#         return result
    
#     # Get user settings for manual verification
#     user_settings = UserSecuritySettings.objects.get(user=request.user)
#     manual_verification_required = user_settings.manual_verification_enabled
    
#     # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#     # send_mail(
#     #     subject='Domestic Transfer Successful - Novexus Finance Bank',
#     #     message=f'Dear {result["user"].username},\n\nYour domestic transfer of ${result["amount"]} to {result["data"].get("recipient_name")} ({result["data"].get("recipient_bank")}) was successful.\n\nReference: {result["reference"]}\n\nThank you for banking with Novexus Finance Bank.',
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     recipient_list=[result["user"].email],
#     #     fail_silently=True,
#     # )
    
#     # if result["data"].get('recipient_email'):
#     #     send_mail(
#     #         subject='You have received money - Novexus Finance Bank',
#     #         message=f'Dear {result["data"].get("recipient_name")},\n\nYou have received ${result["amount"]} from {result["user"].username} via Novexus Finance Bank.\n\nReference: {result["reference"]}\n\nThank you.',
#     #         from_email=settings.DEFAULT_FROM_EMAIL,
#     #         recipient_list=[result["data"].get('recipient_email')],
#     #         fail_silently=True,
#     #     )
    
#     serializer = TransactionSerializer(result["transaction"])
    
#     response_data = {
#         'message': 'Domestic transfer successful',
#         'transaction': serializer.data,
#         'manual_verification_required': manual_verification_required
#     }
    
#     return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def wire_transfer(request):
#     result = validate_and_prepare_transfer(request, 'wire')
    
#     if not isinstance(result, dict) or 'completed' not in result:
#         return result
    
#     # Get user settings for manual verification
#     user_settings = UserSecuritySettings.objects.get(user=request.user)
#     manual_verification_required = user_settings.manual_verification_enabled
    
#     country = result["data"].get('country', '')
#     equivalent_amount = None
#     target_currency = None
#     currency_symbol = None
    
#     print(f"DEBUG: Country received: {country}")
    
#     if country:
#         target_currency = get_currency_code(country)
#         print(f"DEBUG: Target currency: {target_currency}")
        
#         # COUNTRY VALIDATION
#         if not target_currency:
#             return Response({
#                 'error': f'Invalid country name: "{country}". Please check spelling or use a supported country.'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         if target_currency:
#             converted = convert_currency(float(result["amount"]), 'USD', target_currency)
#             print(f"DEBUG: Converted amount: {converted}")
            
#             if converted:
#                 equivalent_amount = round(converted, 2)
#                 currency_symbol = get_currency_symbol(target_currency)
#                 print(f"DEBUG: Final - {result['amount']} USD = {equivalent_amount} {target_currency}")
    
#     # ===== SAVE EQUIVALENT AMOUNT TO TRANSACTION =====
#     transaction = result["transaction"]
#     if equivalent_amount and target_currency:
#         transaction.equivalent_amount = equivalent_amount
#         transaction.target_currency = target_currency
#         transaction.currency_symbol = currency_symbol
#         transaction.save()
    
#     # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#     # send_mail(
#     #     subject='Wire Transfer Successful - Novexus Finance Bank',
#     #     message=f'Dear {result["user"].username},\n\nYour international wire transfer of ${result["amount"]} to {result["data"].get("recipient_name")} ({result["data"].get("recipient_bank")}, {result["data"].get("country")}) was successful.\n\nSWIFT Code: {result["data"].get("swift_code")}\nReference: {result["reference"]}\n\nThank you for banking with Novexus Finance Bank.',
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     recipient_list=[result["user"].email],
#     #     fail_silently=True,
#     # )
    
#     # if result["data"].get('recipient_email'):
#     #     send_mail(
#     #         subject='You have received an international wire transfer - Novexus Finance Bank',
#     #         message=f'Dear {result["data"].get("recipient_name")},\n\nYou have received ${result["amount"]} from {result["user"].username} via Novexus Finance Bank International Wire Transfer.\n\nReference: {result["reference"]}\n\nThank you.',
#     #         from_email=settings.DEFAULT_FROM_EMAIL,
#     #         recipient_list=[result["data"].get('recipient_email')],
#     #         fail_silently=True,
#     #     )
    
#     serializer = TransactionSerializer(result["transaction"])
    
#     response_data = {
#         'message': 'Wire transfer successful',
#         'transaction': serializer.data,
#         'equivalent_amount': equivalent_amount,
#         'target_currency': target_currency,
#         'currency_symbol': currency_symbol,
#         'manual_verification_required': manual_verification_required
#     }
    
#     return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def verify_otp(request):
#     """Verify OTP and complete transfer"""
#     user = request.user
#     data = request.data
    
#     otp_id = data.get('otp_id')
#     user_code = data.get('otp_code')
#     transaction_id = data.get('transaction_id')
    
#     # DEBUG - Print received values
#     print(f"DEBUG: otp_id={otp_id}, user_code={user_code}, transaction_id={transaction_id}")
    
#     try:
#         otp = OTP.objects.get(id=otp_id, user=user, is_used=False)
#         print(f"DEBUG: Found OTP with code: {otp.code}")
        
#         if otp.is_expired():
#             print("DEBUG: OTP is expired")
#             return Response({'error': 'OTP expired. Please request again.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # ✅ FIX: Convert both to strings before comparing
#         if str(otp.code) != str(user_code):
#             print(f"DEBUG: OTP codes do NOT match: {otp.code} vs {user_code}")
#             return Response({'error': 'Invalid OTP code'}, status=status.HTTP_400_BAD_REQUEST)
        
#         print("DEBUG: OTP codes match! ✅")
#         otp.is_used = True
#         otp.save()
        
#         try:
#             transaction = Transaction.objects.get(id=transaction_id, sender=user, status='pending')
#             amount = transaction.amount
            
#             user.balance -= amount
#             user.save()
            
#             transaction.status = 'completed'
#             transaction.save()
            
#             # ===== ADD CURRENCY CONVERSION AFTER COMPLETION =====
#             if transaction.transfer_type == 'wire' and transaction.country:
#                 target_currency = get_currency_code(transaction.country)
#                 if target_currency:
#                     converted = convert_currency(float(transaction.amount), 'USD', target_currency)
#                     if converted:
#                         transaction.equivalent_amount = round(converted, 2)
#                         transaction.target_currency = target_currency
#                         transaction.currency_symbol = get_currency_symbol(target_currency)
#                         transaction.save()
#                         print(f"DEBUG: Equivalent amount saved: {transaction.equivalent_amount} {transaction.target_currency}")
            
#             # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#             # if transaction.transfer_type == 'wire':
#             #     send_mail(
#             #         subject='Wire Transfer Successful - Novexus Finance Bank',
#             #         message=f'Dear {user.username},\n\nYour wire transfer of ${amount} to {transaction.recipient_name} ({transaction.recipient_bank}) was successful.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
#             #         from_email=settings.DEFAULT_FROM_EMAIL,
#             #         recipient_list=[user.email],
#             #         fail_silently=True,
#             #     )
#             # else:
#             #     send_mail(
#             #         subject='Domestic Transfer Successful - Novexus Finance Bank',
#             #         message=f'Dear {user.username},\n\nYour domestic transfer of ${amount} to {transaction.recipient_name} ({transaction.recipient_bank}) was successful.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
#             #         from_email=settings.DEFAULT_FROM_EMAIL,
#             #         recipient_list=[user.email],
#             #         fail_silently=True,
#             #     )
            
#             serializer = TransactionSerializer(transaction)
#             return Response({'message': 'Transfer completed', 'transaction': serializer.data})
            
#         except Transaction.DoesNotExist:
#             return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
#     except OTP.DoesNotExist:
#         return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def resend_otp(request):
#     """Resend OTP"""
#     user = request.user
#     transaction_id = request.data.get('transaction_id')
    
#     OTP.objects.filter(user=user, transaction_id=transaction_id, is_used=False).delete()
    
#     otp_code = str(random.randint(100000, 999999)).zfill(6)
#     otp = OTP.objects.create(
#         user=user,
#         code=otp_code,
#         transaction_id=transaction_id
#     )
    
#     return Response({
#         'message': 'New OTP generated',
#         'otp_id': otp.id
#     })


# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_transaction(request, transaction_id):
#     try:
#         transaction = Transaction.objects.get(id=transaction_id, sender=request.user)
#         transaction.delete()
#         return Response({'message': 'Transaction deleted successfully'})
#     except Transaction.DoesNotExist:
#         return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def deposit(request):
#     user = request.user
#     amount = Decimal(str(request.data.get('amount', 0)))

#     if amount <= 0:
#         return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

#     user.balance += amount
#     user.save()

#     Transaction.objects.create(
#         sender=user,
#         recipient_name=user.username,
#         recipient_email=user.email,
#         recipient_bank='Novexus Finance Bank',
#         recipient_account=user.account_number,
#         amount=amount,
#         transaction_type='deposit',
#         status='completed',
#         reference='RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10],
#     )

#     return Response({'message': f'${amount} deposited successfully', 'new_balance': str(user.balance)})


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def withdraw(request):
#     user = request.user
#     amount = Decimal(str(request.data.get('amount', 0)))

#     if amount <= 0:
#         return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

#     if amount > user.balance:
#         return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

#     pin = request.data.get('pin')
#     if pin != user.transaction_pin:
#         return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

#     user.balance -= amount
#     user.save()

#     Transaction.objects.create(
#         sender=user,
#         recipient_name=user.username,
#         recipient_email=user.email,
#         recipient_bank='Novexus Finance Bank',
#         recipient_account=user.account_number,
#         amount=amount,
#         transaction_type='withdrawal',
#         status='completed',
#         reference='RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10],
#     )

#     return Response({'message': f'${amount} withdrawn successfully', 'new_balance': str(user.balance)})


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     try:
#         from rest_framework_simplejwt.tokens import RefreshToken
#         refresh_token = request.data.get('refresh')
#         token = RefreshToken(refresh_token)
#         token.blacklist()
#         return Response({'message': 'Logged out successfully'})
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# # ==================== ADMIN VIEWS ====================

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_pending_transactions(request):
#     """Admin: Get all pending transactions"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     transactions = Transaction.objects.filter(status='pending').order_by('-created_at')
#     serializer = TransactionSerializer(transactions, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def approve_transaction(request, transaction_id):
#     """Admin: Approve pending transaction"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     try:
#         transaction = Transaction.objects.get(id=transaction_id, status='pending')
#         user = transaction.sender
#         amount = transaction.amount
        
#         user.balance -= amount
#         user.save()
        
#         transaction.status = 'completed'
#         transaction.save()
        
#         # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#         # send_mail(
#         #     subject='Transfer Approved - Novexus Finance Bank',
#         #     message=f'Dear {user.username},\n\nYour transfer of ${amount} has been approved by admin.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
#         #     from_email=settings.DEFAULT_FROM_EMAIL,
#         #     recipient_list=[user.email],
#         #     fail_silently=True,
#         # )
        
#         return Response({'message': 'Transaction approved'})
        
#     except Transaction.DoesNotExist:
#         return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def reject_transaction(request, transaction_id):
#     """Admin: Reject pending transaction"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     try:
#         transaction = Transaction.objects.get(id=transaction_id, status='pending')
#         transaction.status = 'failed'
#         transaction.save()
        
#         # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
#         # send_mail(
#         #     subject='Transfer Rejected - Novexus Finance Bank',
#         #     message=f'Dear {transaction.sender.username},\n\nYour transfer of ${transaction.amount} has been rejected by admin.\n\nReference: {transaction.reference}\n\nPlease contact support for more information.',
#         #     from_email=settings.DEFAULT_FROM_EMAIL,
#         #     recipient_list=[transaction.sender.email],
#         #     fail_silently=True,
#         # )
        
#         return Response({'message': 'Transaction rejected'})
        
#     except Transaction.DoesNotExist:
#         return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def system_settings(request):
#     """Admin: Get/Update system settings"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     settings_obj = SystemSettings.objects.first()
#     if not settings_obj:
#         settings_obj = SystemSettings.objects.create()
    
#     if request.method == 'GET':
#         return Response({
#             'pending_approval_enabled': settings_obj.pending_approval_enabled,
#             'otp_enabled': settings_obj.otp_enabled,
#             'imf_enabled': settings_obj.imf_enabled,
#         })
    
#     if request.method == 'POST':
#         settings_obj.pending_approval_enabled = request.data.get('pending_approval_enabled', settings_obj.pending_approval_enabled)
#         settings_obj.otp_enabled = request.data.get('otp_enabled', settings_obj.otp_enabled)
#         settings_obj.imf_enabled = request.data.get('imf_enabled', settings_obj.imf_enabled)
#         settings_obj.save()
#         return Response({'message': 'Settings updated'})


# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def manage_imf(request, user_id=None):
#     """Admin: Manage IMF codes for users"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     if request.method == 'GET':
#         imfs = IMF.objects.all()
#         data = [{'id': imf.id, 'user_email': imf.user.email, 'code': imf.code, 'is_active': imf.is_active} for imf in imfs]
#         return Response(data)
    
#     if request.method == 'POST':
#         try:
#             target_user = User.objects.get(id=user_id)
#             imf_code = request.data.get('code')
            
#             if not imf_code:
#                 imf_code = str(random.randint(1000000000, 9999999999))
            
#             IMF.objects.create(
#                 user=target_user,
#                 code=imf_code,
#                 is_active=True
#             )
            
#             return Response({'message': 'IMF code created', 'code': imf_code})
            
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def restrict_account(request, user_id):
#     """Admin: Restrict a user account"""
#     if not request.user.is_staff:
#         return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
#     try:
#         target_user = User.objects.get(id=user_id)
#         user_settings, created = UserSecuritySettings.objects.get_or_create(user=target_user)
#         user_settings.is_restricted = request.data.get('is_restricted', True)
#         user_settings.restriction_reason = request.data.get('reason', '')
#         user_settings.save()
        
#         return Response({'message': f'Account restriction updated'})
        
#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)





from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Transaction, SystemSettings, OTP, IMF, AccountRestriction, UserSecuritySettings
from .serializers import RegisterSerializer, UserSerializer, TransactionSerializer
import uuid
import random
import string
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
import requests


# ==================== CURRENCY CONVERSION FUNCTIONS ====================


def get_currency_code(country_name):
    """Get currency code from country name using manual mapping"""
    currency_map = {
        'russia': 'RUB',
        'vietnam': 'VND',
        'laos': 'LAK',
        'myanmar': 'MMK',
        'ukraine': 'UAH',
        'cambodia': 'KHR',
        'portugal': 'EUR',
        'portuguese': 'EUR',
        'philippines': 'PHP',
        'japan': 'JPY',
        'singapore': 'SGD',
        'brunei': 'BND',
        'united states': 'USD',
        'usa': 'USD',
        'us': 'USD',
        'united kingdom': 'GBP',
        'uk': 'GBP',
        'china': 'CNY',
        'india': 'INR',
        'canada': 'CAD',
        'australia': 'AUD',
        'germany': 'EUR',
        'france': 'EUR',
        'italy': 'EUR',
        'spain': 'EUR',
        'brazil': 'BRL',
        'mexico': 'MXN',
        'south africa': 'ZAR',
        'turkey': 'TRY',
        'south korea': 'KRW',
        'indonesia': 'IDR',
        'malaysia': 'MYR',
        'thailand': 'THB',
        'pakistan': 'PKR',
        'bangladesh': 'BDT',
        'egypt': 'EGP',
        'saudi arabia': 'SAR',
        'uae': 'AED',
        'switzerland': 'CHF',
        'sweden': 'SEK',
        'norway': 'NOK',
        'denmark': 'DKK',
        'poland': 'PLN',
        'israel': 'ILS',
    }
    
    country_lower = country_name.lower().strip()
    for key, code in currency_map.items():
        if key in country_lower:
            return code
    return None


def get_currency_symbol(currency_code):
    """Get currency symbol from currency code"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥',
        'VND': '₫', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$',
        'GHS': '₵', 'KES': 'KSh', 'ZAR': 'R', 'TRY': '₺', 'RUB': '₽',
        'KRW': '₩', 'BRL': 'R$', 'MXN': '$', 'SGD': 'S$', 'CHF': 'CHF',
        'IDR': 'Rp', 'MYR': 'RM', 'THB': '฿', 'PHP': '₱', 'PKR': '₨',
        'BDT': '৳', 'EGP': 'E£', 'SAR': '﷼', 'AED': 'د.إ', 'SEK': 'kr',
        'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł', 'ILS': '₪',
        'LAK': '₭', 'MMK': 'K', 'UAH': '₴', 'KHR': '៛', 'BND': 'B$'
    }
    return symbols.get(currency_code, currency_code)
    


def convert_currency(amount, from_currency, to_currency):
    """Convert amount using ExchangeRate-API"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency)
            if rate:
                return float(amount) * rate
        return None
    except Exception as e:
        print(f"Error converting currency: {e}")
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserSecuritySettings.objects.get_or_create(user=user)
        return Response({'message': 'Account created successfully', 'account_number': user.account_number}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    user = request.user
    data = request.data

    pin = data.get('pin')
    if pin != user.transaction_pin:
        return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

    amount = Decimal(str(data.get('amount', 0)))

    if amount <= 0:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    if amount > user.balance:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    if amount > user.daily_transfer_limit:
        return Response({'error': f'Amount exceeds daily limit of ${user.daily_transfer_limit}'}, status=status.HTTP_400_BAD_REQUEST)

    reference = 'RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10]

    user.balance -= amount
    user.save()

    transaction = Transaction.objects.create(
        sender=user,
        recipient_name=data.get('recipient_name'),
        recipient_email=data.get('recipient_email'),
        recipient_bank=data.get('recipient_bank'),
        recipient_account=data.get('recipient_account'),
        amount=amount,
        transaction_type='transfer',
        status='completed',
        reference=reference,
        description=data.get('description', ''),
    )

    # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
    # send_mail(
    #     subject='Transfer Successful - Novexus Finance Bank',
    #     message=f'Dear {user.username},\n\nYour transfer of ${amount} to {data.get("recipient_name")} ({data.get("recipient_bank")}) was successful.\n\nReference: {reference}\n\nThank you for banking with Novexus Finance Bank.',
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[user.email],
    #     fail_silently=True,
    # )

    # send_mail(
    #     subject='You have received money - Novexus Finance Bank',
    #     message=f'Dear {data.get("recipient_name")},\n\nYou have received ${amount} from {user.username} via Novexus Finance Bank.\n\nReference: {reference}\n\nThank you.',
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[data.get('recipient_email')],
    #     fail_silently=True,
    # )

    serializer = TransactionSerializer(transaction)
    return Response({'message': 'Transfer successful', 'transaction': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    transactions = Transaction.objects.filter(sender=request.user).order_by('-created_at')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


def validate_and_prepare_transfer(request, transfer_type):
    user = request.user
    data = request.data

    user_settings, created = UserSecuritySettings.objects.get_or_create(user=user)

    if user_settings.is_restricted:
        reason = user_settings.restriction_reason or "Your account has been restricted."
        return Response({'error': f'Account restricted: {reason}'}, status=status.HTTP_403_FORBIDDEN)

    pin = data.get('pin')
    if pin != user.transaction_pin:
        return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

    amount = Decimal(str(data.get('amount', 0)))
    if amount <= 0:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    if amount > user.balance:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    if amount > user.daily_transfer_limit:
        return Response({'error': f'Amount exceeds daily limit of ${user.daily_transfer_limit}'}, status=status.HTTP_400_BAD_REQUEST)

    if user_settings.imf_enabled:
        imf_code = data.get('imf_code')
        if not imf_code:
            return Response({'requires_imf': True, 'message': 'IMF code required'}, status=status.HTTP_200_OK)

        try:
            imf = IMF.objects.get(user=user, code=imf_code, is_active=True)
        except IMF.DoesNotExist:
            return Response({'error': 'Invalid IMF code'}, status=status.HTTP_400_BAD_REQUEST)

    reference = 'RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10]

    transaction_data = {
        'sender': user,
        'recipient_name': data.get('recipient_name'),
        'recipient_email': data.get('recipient_email', ''),
        'recipient_bank': data.get('recipient_bank'),
        'recipient_account': data.get('recipient_account'),
        'amount': amount,
        'transaction_type': 'transfer',
        'transfer_type': transfer_type,
        'status': 'pending',
        'reference': reference,
        'description': data.get('description', ''),
    }

    if transfer_type == 'wire':
        transaction_data['swift_code'] = data.get('swift_code', '')
        transaction_data['country'] = data.get('country', '')

    transaction = Transaction.objects.create(**transaction_data)

    if user_settings.otp_enabled:
        otp_code = str(random.randint(100000, 999999)).zfill(6)
        otp = OTP.objects.create(
            user=user,
            code=otp_code,
            transaction_id=transaction.id
        )

        return Response({
            'requires_otp': True,
            'otp_id': otp.id,
            'transaction_id': transaction.id,
            'message': 'OTP generated. Check admin panel for code.'
        }, status=status.HTTP_200_OK)

    if user_settings.pending_approval_enabled:
        return Response({
            'status': 'pending',
            'message': 'Transfer submitted for admin approval. You will be notified once approved.',
            'transaction_id': transaction.id,
            'reference': reference
        }, status=status.HTTP_200_OK)

    user.balance -= amount
    user.save()
    transaction.status = 'completed'
    transaction.save()

    return {
        'completed': True,
        'transaction': transaction,
        'amount': amount,
        'reference': reference,
        'user': user,
        'data': data
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def domestic_transfer(request):
    result = validate_and_prepare_transfer(request, 'domestic')
    
    if not isinstance(result, dict) or 'completed' not in result:
        return result
    
    # Get user settings for manual verification
    user_settings = UserSecuritySettings.objects.get(user=request.user)
    manual_verification_required = user_settings.manual_verification_enabled
    
    # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
    # send_mail(
    #     subject='Domestic Transfer Successful - Novexus Finance Bank',
    #     message=f'Dear {result["user"].username},\n\nYour domestic transfer of ${result["amount"]} to {result["data"].get("recipient_name")} ({result["data"].get("recipient_bank")}) was successful.\n\nReference: {result["reference"]}\n\nThank you for banking with Novexus Finance Bank.',
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[result["user"].email],
    #     fail_silently=True,
    # )
    
    # if result["data"].get('recipient_email'):
    #     send_mail(
    #         subject='You have received money - Novexus Finance Bank',
    #         message=f'Dear {result["data"].get("recipient_name")},\n\nYou have received ${result["amount"]} from {result["user"].username} via Novexus Finance Bank.\n\nReference: {result["reference"]}\n\nThank you.',
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=[result["data"].get('recipient_email')],
    #         fail_silently=True,
    #     )
    
    serializer = TransactionSerializer(result["transaction"])
    
    response_data = {
        'message': 'Domestic transfer successful',
        'transaction': serializer.data,
        'manual_verification_required': manual_verification_required
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wire_transfer(request):
    result = validate_and_prepare_transfer(request, 'wire')
    
    if not isinstance(result, dict) or 'completed' not in result:
        return result
    
    # Get user settings for manual verification
    user_settings = UserSecuritySettings.objects.get(user=request.user)
    manual_verification_required = user_settings.manual_verification_enabled
    
    country = result["data"].get('country', '')
    equivalent_amount = None
    target_currency = None
    currency_symbol = None
    
    print(f"DEBUG: Country received: {country}")
    
    if country:
        target_currency = get_currency_code(country)
        print(f"DEBUG: Target currency: {target_currency}")
        
        # COUNTRY VALIDATION
        if not target_currency:
            return Response({
                'error': f'Invalid country name: "{country}". Please check spelling or use a supported country.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if target_currency:
            converted = convert_currency(float(result["amount"]), 'USD', target_currency)
            print(f"DEBUG: Converted amount: {converted}")
            
            if converted:
                equivalent_amount = round(converted, 2)
                currency_symbol = get_currency_symbol(target_currency)
                print(f"DEBUG: Final - {result['amount']} USD = {equivalent_amount} {target_currency}")
    
    # ===== SAVE EQUIVALENT AMOUNT TO TRANSACTION =====
    transaction = result["transaction"]
    if equivalent_amount and target_currency:
        transaction.equivalent_amount = equivalent_amount
        transaction.target_currency = target_currency
        transaction.currency_symbol = currency_symbol
        transaction.save()
    
    # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
    # send_mail(
    #     subject='Wire Transfer Successful - Novexus Finance Bank',
    #     message=f'Dear {result["user"].username},\n\nYour international wire transfer of ${result["amount"]} to {result["data"].get("recipient_name")} ({result["data"].get("recipient_bank")}, {result["data"].get("country")}) was successful.\n\nSWIFT Code: {result["data"].get("swift_code")}\nReference: {result["reference"]}\n\nThank you for banking with Novexus Finance Bank.',
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[result["user"].email],
    #     fail_silently=True,
    # )
    
    # if result["data"].get('recipient_email'):
    #     send_mail(
    #         subject='You have received an international wire transfer - Novexus Finance Bank',
    #         message=f'Dear {result["data"].get("recipient_name")},\n\nYou have received ${result["amount"]} from {result["user"].username} via Novexus Finance Bank International Wire Transfer.\n\nReference: {result["reference"]}\n\nThank you.',
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=[result["data"].get('recipient_email')],
    #         fail_silently=True,
    #     )
    
    serializer = TransactionSerializer(result["transaction"])
    
    response_data = {
        'message': 'Wire transfer successful',
        'transaction': serializer.data,
        'equivalent_amount': equivalent_amount,
        'target_currency': target_currency,
        'currency_symbol': currency_symbol,
        'manual_verification_required': manual_verification_required
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    """Verify OTP and complete transfer"""
    user = request.user
    data = request.data
    
    otp_id = data.get('otp_id')
    user_code = data.get('otp_code')
    transaction_id = data.get('transaction_id')
    
    # DEBUG - Print received values
    print(f"DEBUG: otp_id={otp_id}, user_code={user_code}, transaction_id={transaction_id}")
    
    try:
        otp = OTP.objects.get(id=otp_id, user=user, is_used=False)
        print(f"DEBUG: Found OTP with code: {otp.code}")
        
        if otp.is_expired():
            print("DEBUG: OTP is expired")
            return Response({'error': 'OTP expired. Please request again.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ FIX: Convert both to strings before comparing
        if str(otp.code) != str(user_code):
            print(f"DEBUG: OTP codes do NOT match: {otp.code} vs {user_code}")
            return Response({'error': 'Invalid OTP code'}, status=status.HTTP_400_BAD_REQUEST)
        
        print("DEBUG: OTP codes match! ✅")
        otp.is_used = True
        otp.save()
        
        try:
            transaction = Transaction.objects.get(id=transaction_id, sender=user, status='pending')
            amount = transaction.amount
            
            user.balance -= amount
            user.save()
            
            transaction.status = 'completed'
            transaction.save()
            
            # ===== ADD CURRENCY CONVERSION AFTER COMPLETION =====
            if transaction.transfer_type == 'wire' and transaction.country:
                target_currency = get_currency_code(transaction.country)
                if target_currency:
                    converted = convert_currency(float(transaction.amount), 'USD', target_currency)
                    if converted:
                        transaction.equivalent_amount = round(converted, 2)
                        transaction.target_currency = target_currency
                        transaction.currency_symbol = get_currency_symbol(target_currency)
                        transaction.save()
                        print(f"DEBUG: Equivalent amount saved: {transaction.equivalent_amount} {transaction.target_currency}")
            
            # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
            # if transaction.transfer_type == 'wire':
            #     send_mail(
            #         subject='Wire Transfer Successful - Novexus Finance Bank',
            #         message=f'Dear {user.username},\n\nYour wire transfer of ${amount} to {transaction.recipient_name} ({transaction.recipient_bank}) was successful.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[user.email],
            #         fail_silently=True,
            #     )
            # else:
            #     send_mail(
            #         subject='Domestic Transfer Successful - Novexus Finance Bank',
            #         message=f'Dear {user.username},\n\nYour domestic transfer of ${amount} to {transaction.recipient_name} ({transaction.recipient_bank}) was successful.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[user.email],
            #         fail_silently=True,
            #     )
            
            serializer = TransactionSerializer(transaction)
            
            # ===== INCLUDE EQUIVALENT AMOUNT IN RESPONSE =====
            response_data = {
                'message': 'Transfer completed',
                'transaction': serializer.data,
                'equivalent_amount': transaction.equivalent_amount,
                'target_currency': transaction.target_currency,
                'currency_symbol': transaction.currency_symbol,
                'manual_verification_required': False
            }
            return Response(response_data)
            
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
    except OTP.DoesNotExist:
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_otp(request):
    """Resend OTP"""
    user = request.user
    transaction_id = request.data.get('transaction_id')
    
    OTP.objects.filter(user=user, transaction_id=transaction_id, is_used=False).delete()
    
    otp_code = str(random.randint(100000, 999999)).zfill(6)
    otp = OTP.objects.create(
        user=user,
        code=otp_code,
        transaction_id=transaction_id
    )
    
    return Response({
        'message': 'New OTP generated',
        'otp_id': otp.id
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id, sender=request.user)
        transaction.delete()
        return Response({'message': 'Transaction deleted successfully'})
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    user = request.user
    amount = Decimal(str(request.data.get('amount', 0)))

    if amount <= 0:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    user.balance += amount
    user.save()

    Transaction.objects.create(
        sender=user,
        recipient_name=user.username,
        recipient_email=user.email,
        recipient_bank='Novexus Finance Bank',
        recipient_account=user.account_number,
        amount=amount,
        transaction_type='deposit',
        status='completed',
        reference='RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10],
    )

    return Response({'message': f'${amount} deposited successfully', 'new_balance': str(user.balance)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    user = request.user
    amount = Decimal(str(request.data.get('amount', 0)))

    if amount <= 0:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

    if amount > user.balance:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    pin = request.data.get('pin')
    if pin != user.transaction_pin:
        return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_400_BAD_REQUEST)

    user.balance -= amount
    user.save()

    Transaction.objects.create(
        sender=user,
        recipient_name=user.username,
        recipient_email=user.email,
        recipient_bank='Novexus Finance Bank',
        recipient_account=user.account_number,
        amount=amount,
        transaction_type='withdrawal',
        status='completed',
        reference='RMD' + str(uuid.uuid4()).replace('-', '').upper()[:10],
    )

    return Response({'message': f'${amount} withdrawn successfully', 'new_balance': str(user.balance)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== ADMIN VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_transactions(request):
    """Admin: Get all pending transactions"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    transactions = Transaction.objects.filter(status='pending').order_by('-created_at')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_transaction(request, transaction_id):
    """Admin: Approve pending transaction"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        transaction = Transaction.objects.get(id=transaction_id, status='pending')
        user = transaction.sender
        amount = transaction.amount
        
        user.balance -= amount
        user.save()
        
        transaction.status = 'completed'
        transaction.save()
        
        # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
        # send_mail(
        #     subject='Transfer Approved - Novexus Finance Bank',
        #     message=f'Dear {user.username},\n\nYour transfer of ${amount} has been approved by admin.\n\nReference: {transaction.reference}\n\nThank you for banking with Novexus Finance Bank.',
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        #     fail_silently=True,
        # )
        
        return Response({'message': 'Transaction approved'})
        
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_transaction(request, transaction_id):
    """Admin: Reject pending transaction"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        transaction = Transaction.objects.get(id=transaction_id, status='pending')
        transaction.status = 'failed'
        transaction.save()
        
        # EMAIL DISABLED - Commented out to avoid SMTP errors on Render
        # send_mail(
        #     subject='Transfer Rejected - Novexus Finance Bank',
        #     message=f'Dear {transaction.sender.username},\n\nYour transfer of ${transaction.amount} has been rejected by admin.\n\nReference: {transaction.reference}\n\nPlease contact support for more information.',
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[transaction.sender.email],
        #     fail_silently=True,
        # )
        
        return Response({'message': 'Transaction rejected'})
        
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def system_settings(request):
    """Admin: Get/Update system settings"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    settings_obj = SystemSettings.objects.first()
    if not settings_obj:
        settings_obj = SystemSettings.objects.create()
    
    if request.method == 'GET':
        return Response({
            'pending_approval_enabled': settings_obj.pending_approval_enabled,
            'otp_enabled': settings_obj.otp_enabled,
            'imf_enabled': settings_obj.imf_enabled,
        })
    
    if request.method == 'POST':
        settings_obj.pending_approval_enabled = request.data.get('pending_approval_enabled', settings_obj.pending_approval_enabled)
        settings_obj.otp_enabled = request.data.get('otp_enabled', settings_obj.otp_enabled)
        settings_obj.imf_enabled = request.data.get('imf_enabled', settings_obj.imf_enabled)
        settings_obj.save()
        return Response({'message': 'Settings updated'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_imf(request, user_id=None):
    """Admin: Manage IMF codes for users"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        imfs = IMF.objects.all()
        data = [{'id': imf.id, 'user_email': imf.user.email, 'code': imf.code, 'is_active': imf.is_active} for imf in imfs]
        return Response(data)
    
    if request.method == 'POST':
        try:
            target_user = User.objects.get(id=user_id)
            imf_code = request.data.get('code')
            
            if not imf_code:
                imf_code = str(random.randint(1000000000, 9999999999))
            
            IMF.objects.create(
                user=target_user,
                code=imf_code,
                is_active=True
            )
            
            return Response({'message': 'IMF code created', 'code': imf_code})
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restrict_account(request, user_id):
    """Admin: Restrict a user account"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        target_user = User.objects.get(id=user_id)
        user_settings, created = UserSecuritySettings.objects.get_or_create(user=target_user)
        user_settings.is_restricted = request.data.get('is_restricted', True)
        user_settings.restriction_reason = request.data.get('reason', '')
        user_settings.save()
        
        return Response({'message': f'Account restriction updated'})
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)