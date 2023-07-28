'''
Створити програму, яка імітуватиме роботу системи «банкомат / термінал». При створенні об’єкту- атрибутами
передається сума балансу юзера та пін-код доступу.

Перевірка пін-коду викликається автоматично при створенні об’єкту та передбачає три спроби. Якщо вхід виконано-
баланс автоматично записується в окремий текстовий файл + в іншому файлі зберігається баланс самої системи.

Для користувача доступні наступні дії:

1.Зняти кошти. В такому випадку сума не може перевищувати наявний баланс користувача та самої системи.
При знятті- сума автоматично мінусується з балансу юзера та системи.

2.Поповнити баланс. В такому випадку баланс юзера та системи буде поповнено на відповідну суму.

3.Дізнатися актуальний курс валют. Тут використовуємо реквест, а сам курс дістаємо з довільного сайту.

4.Перевести певну суму в довільну валюту. Тут також використовуємо реквест для актуального курсу. Після
операції- для юзера буде створено ще один атрибут (сума коштів у вказаній валюті), значення якого буде
зберігатися в новому текстовому файлі.

5.Кожна операція записується в окремий файл у вигляді словника, де ключем буде час + дата (datetime.now()),
значенням- тип здійсненої операції.

Обов’язкові умови- наявність наслідування та інкапсуляції
'''

from datetime import datetime
import requests
from bs4 import BeautifulSoup as Bs

class Bank:
    def __init__(self, user_balance, system_balance, pincode):
        self._user_balance = user_balance
        self._system_balance = system_balance
        self._pincode = pincode
        self._EUR = 100
        self._USD = 200
        self._PLN = 500
        self.check_pincode()

    def check_pincode(self):
        attempts = 0
        while attempts < 3:
            input_pincode = int(input('Enter pin code: '))
            if input_pincode == self._pincode:
                print('Pin code is correct.')
                self.user_file = open('User_balance.txt', 'w')
                self.user_file.write(str(f'User balance: {self._user_balance} UAH\n'))
                self.balance_file = open('System_balance.txt', 'w')
                self.balance_file.write(str(f'System balance: {self._system_balance} UAH\n'))
                self.choise_action()
                break
            else:
                print('Pin code is incorrect.')
                attempts += 1
        if attempts == 3:
            print('Maximum number of attempts reached.')

class Bank_operations(Bank):
    def __init__(self, user_balance, system_balance, pincode):
        super().__init__(user_balance, system_balance, pincode)

    def choise_action(self):
        print('Withdraw money - 1\nTop up the balance - 2\nFind out the dollar exchange rate - 3\nMoney transfer in currency - 4')
        action = int(input('Select an action: '))
        if action == 1:
            sum = int(input('Enter sum: '))
            self.withdraw_money(sum)
        elif action == 2:
            sum = int(input('Enter sum: '))
            self.top_up_the_balance(sum)
        elif action == 3:
            self.exchange_rate()
        elif action == 4:
            self.money_transfer_in_currency()

    def withdraw_money(self, sum):
        if 0 < sum <= self._user_balance and 0 < sum <= self._system_balance:
            self._user_balance -= sum
            self._system_balance -= sum
            data = f'{{"{str(datetime.now().replace(microsecond=0))}": "Withdraw money"}}'
            self.operation_file = open('Operations.txt', 'w')
            self.operation_file.write(data)
            self.user_file.write(f'After operation: {self._user_balance} UAH')
            self.balance_file.write(f'After operation: {self._system_balance} UAH')
        else:
            print('Error')

    def top_up_the_balance(self, sum):
        if sum >= 0:
            self._user_balance += sum
            self._system_balance += sum
            data = f'{{"{str(datetime.now().replace(microsecond=0))}": "Top_up_the_balance"}}'
            self.operation_file = open('Operations.txt', 'w')
            self.operation_file.write(data)
            self.user_file.write(f'After operation: {self._user_balance} UAH')
            self.balance_file.write(f'After operation: {self._system_balance} UAH')
        else:
            print('Error')

    def exchange_rate(self):
        url = 'https://privatbank.ua/rates-archive/'
        response = requests.get(url)
        html = Bs(response.content, 'html.parser')
        print('EUR - 0\nUSD - 1\nPLN - 2')
        self.currency_selection = int(input('select currency: '))
        data = f'{{"{str(datetime.now().replace(microsecond=0))}": "Exchange_rate"}}'
        self.operation_file = open('Operations.txt', 'w')
        self.operation_file.write(data)
        for i in html.select('.currency-pairs'):
            if i == html.select('.currency-pairs')[self.currency_selection]:
                self.purchase = i.select('.purchase > span')
                self.sale = i.select('.sale > span')
                print(f'Purchase: {self.purchase[0].text} UAH\nSale: {self.sale[0].text} UAH')
                return float(self.purchase[0].text)
            else:
                print('Error')

    def money_transfer_in_currency(self):
        self.currencies_file = open('Currencies_balance.txt', 'w')
        self.currencies_file.write(f'Euro: {self._EUR} EUR\nDollar: {self._USD} USD\nZloty: {self._PLN} PLN\n')
        self.exchange_rate()
        sum = float(input('Enter sum in UAH: '))
        result = round(sum / float(self.purchase[0].text), 2)
        if self.currency_selection == 0 and result <= self._EUR:
            print(f'{result} EUR')
            self.currencies_file.write(f'Euro (after operation): {self._EUR - result} EUR')
            self.user_file.write(f'After operation: {self._user_balance - sum} UAH')
            self.balance_file.write(f'After operation: {self._system_balance - sum} UAH')
        elif self.currency_selection == 1 and result <= self._USD:
            print(f'{result} USD')
            self.currencies_file.write(f'Dollar (after operation): {self._USD - result} USD')
            self.user_file.write(f'After operation: {self._user_balance - sum} UAH')
            self.balance_file.write(f'After operation: {self._system_balance - sum} UAH')
        elif self.currency_selection == 2 and result <= self._PLN:
            print(f'{result} PLN')
            self.currencies_file.write(f'Zloty (after operation): {self._PLN - result} PLN')
            self.user_file.write(f'After operation: {self._user_balance - sum} UAH')
            self.balance_file.write(f'After operation: {self._system_balance - sum} UAH')
        else:
            print('Error')
        data = f'{{"{str(datetime.now().replace(microsecond=0))}": "Money_transfer_in_currency"}}'
        self.operation_file = open('Operations.txt', 'w')
        self.operation_file.write(data)

n = Bank_operations(10000, 8000, 1234)



