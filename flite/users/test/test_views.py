from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import *
from .factories import UserFactory, BankFactory, AllBanksFactory, TransactionFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.user_data = model_to_dict(UserFactory.build())

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=response.data.get('id'))
        eq_(user.username, self.user_data.get('username'))
        ok_(check_password(self.user_data.get('password'), user.password))

    def test_post_request_with_valid_data_succeeds_and_profile_is_created(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(UserProfile.objects.filter(user__username=self.user_data['username']).exists(),True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(self):
        
        referring_user = UserFactory()
        self.user_data.update({"referral_code":referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'],owner__username=referring_user.username).exists(),True)


    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(self):
        
        self.user_data.update({"referral_code":"FAKECODE"})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        
class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        new_first_name = fake.first_name()
        payload = {'first_name': new_first_name}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.user.id)
        eq_(user.first_name, new_first_name)

class TestTransactions(APITestCase):

    def setUp(self):
        self.sender = UserFactory()
        self.receipient = UserFactory()
        self.bank_1 = AllBanksFactory()
        self.bank_2 = AllBanksFactory()
        self.sender_account = BankFactory(owner=self.sender, bank=self.bank_1, account_name=self.sender.account_name)
        self.receipient_account = BankFactory(owner=self.receipient, bank=self.bank_2, account_name=self.receipient.username)
        self.sender_balance = 100000
        self.receipient_balance = 50000
        self.sender_balance.save()
        self.receipient_balance.save()

    def test_user_can_make_a_deposit(self):
        self.url = f"/api/v1/users/{sender.id}/deposits"
        balance =  self.sender_balance
        transac_data = model_to_dict(TransactionFactory.build(), fields=['reference', 'amount'])
        res = self.client.post(self.url, transac_data)
        eq_(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_withdrawal(self):
        self.url = f"/api/v1/users/{sender.id}/withdrawals"
        balance =  self.sender_balance
        transac_data = model_to_dict(TransactionFactory.build(), fields=['reference', 'amount'])
        res = self.client.post(self.url, transac_data)
        eq_(res.status_code, status.HTTP_201_CREATED)
        

    def test_user_can_make_a_p2p_transfer(self):
        self.url = f"/api/v1/account/{sender.id}/p2ptransfers/{receipient.id}"
        balance =  self.sender_balance
        transac_data = model_to_dict(TransactionFactory.build(), fields=['reference', 'amount'])
        res = self.client.post(self.url, transac_data)
        eq_(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_fetch_all_transactions(self):
        self.url = f"/api/v1/account/{sender.id}/transaction-list"
        account = BankFactory(owner=self.sender, bank=self.bank)
        TransactionFactory.create_batch(6, owner=self.sender, bank=account)
        res = self.client.get(self.url)
        eq_(res.status_code, status.HTTP_200_OK)
        eq_(res.json().__len__(), 6)

    def test_user_can_fetch_a_single_transaction(self):
        self.url = f"/api/v1/account/{sender.id}/transaction-detail/{self.transaction.id}"
        transac_data = TransactionFactory(owner=self.sender, bank=sender_account)
        res = self.client.get(self.url)
        eq_(res.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.sender.delete()
        self.receipient.delete()