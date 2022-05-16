from tkinter import messagebox
import time
import helper

class eGela:
    _login = 0
    _cookiea = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. ESKAERA #####")
        metodo = 'POST'
        uri = "https://egela.ehu.eus/login/index.php"
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 33
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 2. ESKAERA #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 66
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 3. ESKAERA #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        popup.destroy()

        if COMPROBACION_DE_LOG_IN:
            #############################################
            # ACTUALIZAR VARIABLES
            #############################################
            self._root.destroy()
        else:
            messagebox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. ESKAERA (Ikasgairen eGelako orrialde nagusia) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress_step = float(100.0 / len(self._refs))

        print("\n##### HTML-aren azterketa... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################

            # ACTUALIZAR BARRA DE PROGRESO
            # POR CADA PDF ANIADIDO EN self._refs
            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):
        print("##### PDF-a deskargatzen... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        return pdf_name, pdf_file
