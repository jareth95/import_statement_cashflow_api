import requests
import settings
import pdfplumber


class CashflowAPI:

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def get_token(self):

        url = 'http://127.0.0.1:8000/api-token-auth/'
        token_payload = {
            'username': self.username,
            'password': self.password
            }
        return requests.request('POST', url, data=token_payload).json()['token']


class PDFData:

    def __init__(self, file):
        self.file = file


    def extract_expenses(self, extract):
        extraction = {}
        line_number = 0
        if extract == 'expense':
            words = ['Card Payment', 'Bill Payment', 'Direct Debit to']

        with pdfplumber.open(self.file) as pdf:
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
        return extraction


api = CashflowAPI(settings.USERNAME, settings.PASSWORD)
pdf = PDFData('statements/Statement 15-jul-22 ac 73400867.pdf')
expenses = pdf.extract_expenses('expense')

print(api.get_token())