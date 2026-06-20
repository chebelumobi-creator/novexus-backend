from rest_framework import serializers
from .models import User, Transaction
import random
import string

def generate_account_number():
    return ''.join(random.choices(string.digits, k=10))

def generate_username(first_name, last_name):
    """Generate username from first and last name"""
    base = f"{first_name.lower()}{last_name.lower()}"
    base = ''.join(c for c in base if c.isalnum())
    return f"{base}{random.randint(100, 999)}"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    transaction_pin = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone', 'address', 'transaction_pin']  # ← REMOVED 'username'

    def create(self, validated_data):
        password = validated_data.pop('password')
        transaction_pin = validated_data.pop('transaction_pin')
        
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        username = generate_username(first_name, last_name)
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=validated_data.get('email'),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
        )
        user.set_password(password)
        user.transaction_pin = transaction_pin
        user.account_number = generate_account_number()
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'username', 'phone', 'address', 'profile_photo', 'balance', 'account_number', 'is_verified', 'daily_transfer_limit']

    def get_full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['sender', 'reference', 'status', 'created_at']