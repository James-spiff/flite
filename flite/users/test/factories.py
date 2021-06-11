import factory
from ..models import Bank, AllBanks, Balance, BankTransfer, P2PTransfer, Transaction


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username',)

    id = factory.Faker('uuid4')
    username = factory.Sequence(lambda n: f'testuser{n}')
    password = factory.Faker('password', length=10, special_chars=True, digits=True,
                             upper_case=True, lower_case=True)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    full_name = first_name + ' ' + last_name
    is_active = True
    is_staff = False

class BankFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Bank

    account_number = factory.Faker('bban') #faker.providers.bank
    account_name = User.full_name  
    account_type = factory.Faker('word', ext_word_list=['CURRENT', 'SAVINGS'])

class AllBanksFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = AllBanks

    name = factory.Faker('company') #from faker.providers.company
    bank_code = factory.Faker('iban')


class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Transaction

    id = factory.Faker('uuid4')
    reference = factory.Faker('sentence')
    amount = 1000 
    