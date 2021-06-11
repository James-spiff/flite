from rest_framework import serializers
from .models import *
from . import utils

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(required=False)


    def validate_referral_code(self, code):
        
        self.reffered_profile = UserProfile.objects.filter(referral_code=code.lower())
        is_valid_code = self.reffered_profile.exists()
        if not is_valid_code:
            raise serializers.ValidationError(
                "Referral code does not exist"
            )
        else:
            return code

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        referral_code = None
        if 'referral_code' in validated_data:
            referral_code = validated_data.pop('referral_code',None)
            
        user = User.objects.create_user(**validated_data)

        if referral_code:
            referral =Referral()
            referral.owner = self.reffered_profile.first().user
            referral.referred = user
            referral.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token','referral_code')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}



class SendNewPhonenumberSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number", None) 
        email = validated_data.get("email", None)

        obj, code = utils.send_mobile_signup_sms(phone_number, email)
        
        return {
            "verification_code":code,
            "id":obj.id
        }

    class Meta:
        model = NewUserPhoneVerification
        fields = ('id', 'phone_number', 'verification_code', 'email',)
        extra_kwargs = {'phone_number': {'write_only': True, 'required':True}, 'email': {'write_only': True}, }
        read_only_fields = ('id', 'verification_code')
        

class WithdrawalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance')
        read_only_fields = ('owner', 'status', 'new_balance')

    def create(self, validated_data):
        owner = validated_data.get('owner')
        amount = validated_data.get('amount')
        owner_balance = owner.balance.first()
        if amount > owner_balance:
            raise serializers.ValidationError('Insufficient Funds')
        new_balance = owner_balance - amount
        owner_balance.book_balance = new_balance
        owner_balance.available_balance = new_balance
        owner_balance.save()

        validated_data['new_balance'] = new_balance
        validated_data['amount'] = amount
        validated_data['bank'] = owner.accounts.first()
        validated_data['status'] = 'Successful' 

        bank_transfer = BankTransfer.objects.create(**validated_data)

        return bank_transfer 


class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance')
        read_only_fields = ('owner', 'status', 'new_balance')

    def create(self, validated_data):
        owner = validated_data.get('owner')
        amount = validated_data.get('amount')
        owner_balance = owner.balance.first()
        new_balance = owner_balance + amount
        owner_balance.book_balance = new_balance
        owner_balance.available_balance = new_balance
        owner_balance.save()

        validated_data['new_balance'] = new_balance
        validated_data['amount'] = amount
        validated_data['bank'] = owner.accounts.first()
        validated_data['status'] = 'Successful' 

        bank_transfer = BankTransfer.objects.create(**validated_data)

        return bank_transfer


class P2PTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = P2PTransfer
        fields = ('id', 'owner', 'refernce', 'status', 'amount', 'new_balance', 'sender', 'recipient')
        read_only_fields = ('owner', 'status', 'new_balance', 'sender', 'recipient')

    def create(self, validated_data):
        owner = validated_data.get('owner')
        sender = validated_data.get('sender')
        receipient = validated_data.get('receipient')
        amount = validated_data.get('amount')
        sender_balance = sender.balance.first()
        receipient_balance = receipient.balance.first()
        new_sender_balance = sender_balance.available_balance - amount
        new_receipient_balance = receipient_balance.available_balance + amount 
        sender_balance.book_balance = new_sender_balance
        receipient_balance.book_balance = new_receipient_balance
        sender_balance.available_balance = new_sender_balance
        receipient_balance.available_balance = new_receipient_balance
        sender_balance.save()
        receipient_balance.save()

        validated_data['new_balance'] = new_sender_balance
        validated_data['amount'] = amount
        validated_data['status'] = 'Successful'


        P2P_transfer = P2PTransfer.objects.create(**validated_data)

        return P2P_transfer


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = ('id', 'owner', 'book_balance', 'available_balance')
        read_only_fields = ('id', 'owner', 'book_balance', 'available_balance')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance')
        read_only_fields = ('owner','status', 'new_balance')