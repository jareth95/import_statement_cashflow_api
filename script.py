import requests
import settings
import pdfplumber
from time import strptime


class CashflowAPI:

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def get_token(self):

        url = 'https://cashflow-manager-26.herokuapp.com/api-token-auth/'
        token_payload = {
            'username': self.username,
            'password': self.password
            }
        return requests.request('POST', url, data=token_payload).json()['token']


    def create_expense(self, token, amount, category, date, description):
        url = 'https://cashflow-manager-26.herokuapp.com/expenses/api/v1/new/'
        headers = {
            'Authorization': f'Token {token}' 
        }
        payload = {
            'owner': token,
            'amount': amount,
            'category': category,
            'date': date,
            'description': description
            }
        return requests.request('POST', url, headers=headers, data=payload)


class PDFData:

    def __init__(self, file):
        self.file = file


    def extract_expenses(self, extract):
        extraction = {}
        line_number = 0
        if extract == 'expense':
            words = ['Card Payment', 'Bill Payment', 'Direct Debit to']

        with pdfplumber.open(self.file) as pdf:
            year = pdf.pages[0].extract_text().split("\n")[2].split()[-1]
            for  page  in pdf.pages:
                text = page.extract_text()
                for counter, line in enumerate(text.split("\n")):
                    for word in words:
                        if word in line:
                            line = line.split()
                            if line[0] != 'Card' and  line[0] != 'Bill'  and  line[0] != 'Direct':
                                line_number = counter
                                try:
                                    float(line[-2])
                                    if '.' in line[-2]:
                                        extraction[f'{line[0]} {line[1]}'] = [{
                                            ' '.join(line[5:-2]) : line[-2]
                                            }]
                                    else:
                                        extraction[f'{line[0]} {line[1]}'] = [{
                                        ' '.join(line[5:-1]) : line[-1]
                                        }]
                                except ValueError:  
                                    extraction[f'{line[0]} {line[1]}'] = [{
                                        ' '.join(line[5:-1]) : line[-1]
                                        }]
                            else:
                                split_line = text.split("\n")[line_number].split()
                                try:
                                    float(line[-2])
                                    if '.' in line[-2]:
                                        extraction[f'{split_line[0]} {split_line[1]}'].append({
                                            ' '.join(line[3:-2]) : line[-2]
                                            })
                                    else:
                                        extraction[f'{split_line[0]} {split_line[1]}'].append({
                                        ' '.join(line[3:-1]) : line[-1]
                                        })
                                except ValueError:  
                                    extraction[f'{split_line[0]} {split_line[1]}'].append({
                                        ' '.join(line[3:-1]) : line[-1]
                                        })               
        return extraction, year


def export_import_expenses():
    api = CashflowAPI(settings.USERNAME, settings.PASSWORD)
    pdf = PDFData('statements/Statement 15-jul-22 ac 73400867.pdf')

    expenses = pdf.extract_expenses('expense')[0]
    year = pdf.extract_expenses('expense')[1]
    token = api.get_token()
    
    for date in expenses:
        day = date.split()[0]
        month = strptime(date.split()[1],'%b').tm_mon
        for expense in expenses[date]:
            for expense_name, expense_amount in expense.items():
                api.create_expense(token, expense_amount, 'statement', f'{year}-{month}-{day}', expense_name)
        


export_import_expenses()