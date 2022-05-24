import json
import urllib
import requests
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import helper

app_key = 'guwt8f1csto7rkm'
app_secret = 'j8lunqqz3lzetos'
server_addr = "localhost"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # 8090. portuan entzuten dagoen zerbitzaria sortu
        listen_socket = socket(AF_INET, SOCK_STREAM)
        listen_socket.bind(('localhost', 8090))
        listen_socket.listen(1)
        print("\t\tSocket listening on port 8090")

        # nabitzailetik 302 eskaera jaso
        # ondorengo lorroan programa gelditzen da zerbitzariak 302 eskaera bat jasotzen duen arte
        client_connection, client_address = listen_socket.accept()
        eskaera = client_connection.recv(1024).decode()
        print("\t\tNabigatzailetik ondorengo eskaera jaso da:")
        print(eskaera)

        # eskaeran "auth_code"-a bilatu
        lehenengo_lerroa = eskaera.split('\n')[0]
        aux_auth_code = lehenengo_lerroa.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("\tauth_code: " + auth_code)

        # erabiltzaileari erantzun bat bueltatu
        http_response = """\ HTTP/1.1 200 OK 

            <html> 
                <head>
                    <title>Proba</title>
                </head> 
                <body> 
                    The authentication flow has completed. Close this window. 
                </body> 
            </html> 
            """
        client_connection.sendall(str.encode(http_response))
        client_connection.close()

        return auth_code

    def do_oauth(self):
        # Authorization
        base_uri = "https://www.dropbox.com/oauth2/authorize"
        goiburuak = {'Host': 'dropbox.com', 'Content-Type': 'application/x-www-form-urlencoded'}
        datuak = {'client_id': app_key,
                  'redirect_uri': redirect_uri,  # Loopback IP address
                  # https sartuz gero cifratu egindo du redirect eskaera eta ezin izanngo du dekodetu eta txarto emango du
                  # errorea 51. lerroan
                  'response_type': 'code', }

        datuak_kodifikatuta = urllib.parse.urlencode(datuak)
        step2_uri = base_uri + '?' + datuak_kodifikatuta
        print("\t" + step2_uri)
        webbrowser.open_new(step2_uri)

        print("\n\tGoogle prompts user for consent")

        auth_code = self.local_server()

        # Exchange authorization code for access token
        uri = 'https://api.dropboxapi.com/oauth2/token'
        goiburuak = {'Host': 'api.dropboxapi.com', 'Content-Type': 'application/x-www-form-urlencoded'}
        datuak = {'client_id': app_key,
                  'client_secret': app_secret,
                  'code': auth_code,
                  'grant_type': 'authorization_code',
                  'redirect_uri': redirect_uri}
        datuak_kodifikatuta = urllib.parse.urlencode(datuak)
        goiburuak['Content-Length'] = str(len(datuak_kodifikatuta))
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_kodifikatuta, allow_redirects=False)
        status = erantzuna.status_code
        print("\t\tStatus: " + str(status))

        # Google responds to this request by returning a JSON object
        # that contains a short-lived access token and a refresh token.
        edukia = erantzuna.text
        print("\t\tEdukia:")
        print("\n" + edukia)
        edukia_json = json.loads(edukia)
        self.access_token = edukia_json['access_token']
        print("\taccess_token: " + self.access_token)
        print("\tThe authentication flow has completed.")

        self._root.destroy()

    def list_folder(self, msg_listbox, cursor="", edukia_json_entries=[]):
        if self._path == "/":
            self._path = ""
        if not cursor:
            print("\t/list_folder")
            uri = 'https://api.dropboxapi.com/2/files/list_folder'
            datuak = {"path": self._path,}
        else:
            print("\t/list_folder/continue")
            uri = 'https://api.dropboxapi.com/2/files/list_folder/continue'
            datuak = {'cursor': cursor,}

        # Call Dropbox API
        goiburuak = {'Host': 'api.dropboxapi.com', 'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json'}
        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code
        print("\tStatus: " + str(status))

        # See if there are more entries available. Process data.
        edukia = erantzuna.text
        edukia_json_dict = json.loads(edukia)
        print(edukia_json_dict)
        print("\tEdukia: ")
        print("\t\tCursor: " + edukia_json_dict['cursor'] + '\n')
        for each in edukia_json_dict['entries']:
            print('\t\t- ' + each['name'])
            print('\t\t\t Mota:' + each['.tag'])
            print('\t\t\t ID:' + each['id'])
        if edukia_json_dict['has_more']:
            self.list_folder(self.access_token, edukia_json_dict['cursor'])

        self._files = helper.update_listbox2(msg_listbox, self._path, edukia_json_dict)

    def transfer_file(self, file_path, file_data):
        print("\n\n\n\n ------- FITXATEGIA IGOTZEN -----------\n\n")
        print("\t/upload " + file_path)
        uri = "https://content.dropboxapi.com/2/files/upload"
        datuak = {'path': file_path}
        datuak_json = json.dumps(datuak)

        goiburuak = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/octet-stream',
                     'Dropbox-API-Arg': datuak_json, }

        erantzuna = requests.post(uri, headers=goiburuak, data=file_data, allow_redirects=False)
        status = erantzuna.status_code
        print("\tStatus: " + str(status))
        print("\t\tTestua: " + str(erantzuna.text))
        print("\n\n ------- FITXATEGIA IGOTA -----------")

    def delete_file(self, file_path):
        print("\n------- FITXATEGIA EZABATZEN -----------\n")
        print("\t/delete_file " + file_path)
        uri = 'https://api.dropboxapi.com/2/files/delete'
        datuak = {'path': file_path, }
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json', }

        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))
        print("\n ------- FITXATEGIA EZABATUA -----------\n")

    def create_folder(self, path):
        print("\n------- KARPETA SORTZEN -----------\n")
        print("\t/create_folder " + path)
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        datuak = {'path': path, }
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json', }

        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))
        print("\n ------- KARPETA SORTUTA -----------\n")

    # EXTRAK:
        # 2 eskaera --> PARTEKATU KARPETA
        # eskaeraa 1 --> DESKARGATU PATH JAKIN BAT ZIP FORMATUAN
        # eskaera 1 --> MUGITU PATH BAT BESTE BATERA

    def share_folder(self, path, norekinPartekatu):
        print("\n------- KARPETA PARTEKATZEN -----------\n")
        print("\t/share_folder " + path)
        print('Path: ' + path + '\nPartner: ' + norekinPartekatu)

        uri = 'https://api.dropboxapi.com/2/sharing/share_folder'
        datuak = {'path': path, }

        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json', }

        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))

        edukia_json = json.loads(erantzuna.text)
        if (status == 200):
            sfID = edukia_json['shared_folder_id']
        elif (status == 409):
            sfID = edukia_json['error']['bad_path']['shared_folder_id']
        else:
            sfID = 'errorea'

        print("\n\t/add_folder_member " + path + ' to ' + norekinPartekatu)
        uri = 'https://api.dropboxapi.com/2/sharing/add_folder_member'
        datuak = {"members": [{"access_level": "editor", "member": {".tag": "email", "email": norekinPartekatu}}, ],
                  "quiet": False, "shared_folder_id": sfID}

        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json', }

        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))

        print("\n ------- KARPETA PARTEKATZEN -----------\n")

    def download_zip(self, path):
        print("\n------- PATH-aren ZIP DESKARGATZEN -----------\n")
        print("\t/download_zip " + path)
        uri = 'https://content.dropboxapi.com/2/files/download_zip'

        datuak = {'path': path, }
        datuak_json = json.dumps(datuak)

        goiburuak = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Dropbox-API-Arg': datuak_json, }

        erantzuna = requests.post(uri, headers=goiburuak, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))
        file = open(path.split('/')[1] + '.zip', 'wb')
        file.write(erantzuna.content)
        file.close()
        print("\n ------- PATH-aren ZIP DESKARGATUTA -----------\n")

    def move(self, pathFrom, pathTo):
        print("\n------- PATH-a MUGITZEN -----------\n")
        print("\t/move " + pathFrom + ' ' + pathTo + '-ra')
        uri = 'https://api.dropboxapi.com/2/files/move_v2'

        datuak = {'from_path': pathFrom,
                  'to_path': pathTo, }

        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self.access_token,
                     'Content-Type': 'application/json', }

        datuak_json = json.dumps(datuak)
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)
        status = erantzuna.status_code

        print('\tStatus: ' + str(status))
        print("\t\tTestua: " + str(erantzuna.text))

        print("\n ------- PATH-a MUGITZEN -----------\n")

        return status
