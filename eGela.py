from tkinter import messagebox as tkMessageBox
import requests
import urllib
from bs4 import BeautifulSoup
import time
import helper
import sys

class eGela:
    _login = 0
    _cookiea = ""
    _ikasgaia = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. ESKAERA (Login inprimakia lortu 'logintoken' ateratzeko) #####")
        metodoa = "GET"
        uria = "https://egela.ehu.eus/login/index.php"
        goiburuak = {'Host': 'egela.ehu.eus'}

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print(str(kodea) + " " + deskribapena)

        cookie = erantzuna.headers['Set-Cookie'].split(";")[0]
        print("Set-Cookie: " + cookie)

        html = erantzuna.content

        # bilaketaren emaitzak duen HTML kodea parsetuko dugu
        soup = BeautifulSoup(html, 'html.parser')

        logintoken = soup.find('input', {'name': 'logintoken'})['value']
        print("Logintoken: " + str(logintoken))

        action = soup.find('form', {'class': 'm-t-1 ehuloginform'})['action']
        print("Action: " + str(action))

        print("##### HTML-aren azterketa... #####")
        # sartu kodea hemen

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 2. ESKAERA (Kautotzea -datu bidalketa-) #####")
        metodoa = "POST"
        uria = action
        goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': cookie, 'Content-Type': 'application/x-www-form-urlencoded'}
        edukia = {'logintoken': logintoken,
                  'username': username,
                  'password': password}

        # datuak imprimaki formatua duen kate batean bihurtuko ditut
        # zelan? urllib liburutegia erabiliz
        edukia_encoded = urllib.parse.urlencode(edukia)
        goiburuak['Content-Length'] = str(len(edukia_encoded))

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, data=edukia_encoded, allow_redirects=False)

        # HTTP erantzunak 4 atal ditu:
        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print(str(kodea) + " " + deskribapena)

        html = erantzuna.content

        # cookie = erantzuna.headers['Set-Cookie'][0].split(";")[0]
        if(erantzuna.headers.__contains__('Set-Cookie')):
            cookie = erantzuna.headers['Set-Cookie'].split(";")[0]
            print("Set-Cookie: " + cookie)
        else:
            print("Erantzunak ez du 'Set-Cookie' goiburua")

        location = erantzuna.headers['Location']
        print("Location: " + location)

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 3. ESKAERA (berbidalketa) #####")
        metodoa = "GET"
        uria = location
        goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': cookie}

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

        # HTTP erantzunak 4 atal ditu:
        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print(str(kodea) + " " + deskribapena)

        if erantzuna.headers.__contains__('Location'):
            location = erantzuna.headers['Location']
            print("Location: " + location)
        else:
            print("Erantzunak ez du 'Location' goiburua")

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 4. ESKAERA (eGelako orrialde nagusia) #####")
        metodoa = "GET"
        uria = location
        goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': cookie}

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

        # HTTP erantzunak 4 atal ditu:
        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print(str(kodea) + " " + deskribapena)

        html = erantzuna.content

        soup = BeautifulSoup(html, 'html.parser')

        izena = None
        if soup.find('span', {'class': 'usertext mr-1'}) is not None:
            izena = str(soup.find('span', {'class': 'usertext mr-1'}).getText())
            print('Sartu den kontuaren izena: ' + izena)
        else:
            print("Ez da erabiltzailearen izena aurkitu")

        webSistemak = str(soup.find('h3', {'class': 'coursename'})).split('href="')[1].split('"')[0]

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        popup.destroy()

        print("\n##### LOGIN EGIAZTAPENA #####")
        if izena is not None:
            # sartu kodea hemen
            tkMessageBox.showinfo("Alert Message", "Login correct!")

            # KLASEAREN ATRIBUTUAK EGUNERATU

            self._cookiea = cookie
            self._login = 1
            self._ikasgaia = webSistemak
            #self._root.destroy()

        else:
            tkMessageBox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 5. ESKAERA (Ikasgairen eGelako orrialdea) #####")

        metodoa = "GET"
        uria = self._ikasgaia
        goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

        # HTTP erantzunak 4 atal ditu:
        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print(str(kodea) + " " + deskribapena)

        html = erantzuna.content

        print("\n##### HTML-aren azterketa... #####")

        # bilaketaren emaitzak duen HTML kodea parsetuko dugu
        soup = BeautifulSoup(html, 'html.parser')

        errenkadak = soup.find_all('a', {'class': 'aalink'})
        i = 1

        for errenkada in errenkadak:
            if str(errenkada).split('src="')[1].split('"')[0].__contains__("pdf"):
                print("---------------" + str(i) + ".Eskaera----------------")

                # HTTP eskaerak 4 eremu ditu:
                metodoa = "GET"
                uria = str(errenkada).split('href="')[1].split('"')[0]
                goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}

                # eskaera bidali eta erantzuna jaso
                erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

                # HTTP erantzunak 4 atal ditu:
                kodea = erantzuna.status_code
                deskribapena = erantzuna.reason
                print(str(kodea) + " " + deskribapena)

                html = erantzuna.content

                # bilaketaren emaitzak duen HTML kodea parsetuko dugu
                soup = BeautifulSoup(html, 'html.parser')
                pdf = soup.find_all('div', {'class': 'resourceworkaround'})
                pdf_link = str(pdf).split('href="')[1].split('"')[0]
                pdf_name = pdf_link.split('/')[len(pdf_link.split('/')) - 1]
                print(str(i) + '.PDF-aren izena : ' + pdf_name)
                print(str(i) + '.PDF-aren link-a: ' + pdf_link)
                self._refs.append({'izena': pdf_name, 'link': pdf_link})
                i = i + 1

        progress_step = float(100.0 / len(self._refs))
        for ref in self._refs:
            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)
            self.get_pdf(self, ref);

        print(self._refs)
        popup.destroy()

        return self._refs

    def get_pdf(self, selection):
        print("##### PDF-a deskargatzen... #####")
        metodoa = "GET"
        uria = selection['link']
        goiburuak = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}

        # eskaera bidali eta erantzuna jaso
        erantzuna = requests.request(metodoa, uria, headers=goiburuak, allow_redirects=False)

        # HTTP erantzunak 4 atal ditu:
        kodea = erantzuna.status_code
        deskribapena = erantzuna.reason
        print("     |  " + str(kodea) + " " + deskribapena)

        pdf_name = selection['izena']
        pdf_content = erantzuna.content
        print('     |  ' + selection['izena'] + ' gordetzen...')

        print("PDF-aren izena : " + selection['izena'])
        pdf_file = open(selection['izena'], 'wb')
        pdf_file.write(pdf_content)
        pdf_file.close()

        return pdf_name, pdf_file

e = eGela
e.check_credentials(e, sys.argv[1], sys.argv[2])
e.get_pdf_refs(e)