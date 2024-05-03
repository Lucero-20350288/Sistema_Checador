import tkinter as tk
import os.path
import cv2
from PIL import Image, ImageTk
import face_recognition
import pickle
import util
import tkinter.messagebox as msgbox


class RegisterUserApp:
    def __init__(self):
        self.register_window = tk.Tk()
        self.register_window.geometry("1200x520+370+120")
        self.register_window.wm_attributes('-topmost', 1)  # Always on top

        self.preview_label = util.get_img_label(self.register_window)
        self.preview_label.place(x=750, y=10, width=400, height=300)

        self.capture_label = util.get_img_label(self.register_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.capture_label)

        self.text_label_register_user = util.get_text_label(self.register_window, 'RFC (ID):')
        self.text_label_register_user.place(x=732, y=320)

        self.entry_text_register_user = tk.Entry(self.register_window, borderwidth=2)
        self.entry_text_register_user.place(x=732, y=355, width=410, height=30)

        self.accept_button_capture = util.get_button(self.register_window, 'Tomar Foto', 'green',
                                                                   self.accept_capture)
        self.accept_button_capture.place(x=775, y=390, width=330, height=50)

        self.accept_button_register_user_window = util.get_button(self.register_window, 'Guardar', 'blue',
                                                                   self.accept_register_user)
        self.accept_button_register_user_window.place(x=775, y=455, width=330, height=50)

                    
    def validar_rfc(self, rfc):
        """
        Función para validar un RFC (Registro Federal de Contribuyentes) en México.
        Retorna True si el RFC es válido, False si no lo es.
        """
        # Longitud válida de un RFC
        if len(rfc) != 13:
            return False
        
        # Patrón de caracteres permitidos en un RFC
        caracteres_validos = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        
        # Validación de los primeros 4 caracteres (Letras)
        for char in rfc[:4]:
            if char.upper() not in caracteres_validos:
                return False
        
        # Validación del dígito numérico (Año de nacimiento)
        if not rfc[4:6].isdigit():
            return False
        
        # Validación del mes de nacimiento
        if not rfc[6:8].isdigit():
            return False
        
        # Validación del día de nacimiento
        if not rfc[8:10].isdigit():
            return False
        
        # Validación del dígito verificador (homoclave)
        if not rfc[10:].isalnum():
            return False
        
        return True

    def add_webcam(self, label):
        self.cap = cv2.VideoCapture(0)
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def accept_capture(self):
        # Verificar si se detectaron caras
        face_locations = face_recognition.face_locations(self.most_recent_capture_arr)
        if not face_locations:
            util.msg_box('Error', 'No se detectó ninguna cara en la imagen. Por favor, mire.')
            return

        # Show preview of the captured image
        preview_imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self.preview_label.configure(image=preview_imgtk)
        self.preview_label.imgtk = preview_imgtk

    def accept_register_user(self):
        name = self.entry_text_register_user.get()

        if len(name) != 13:
            util.msg_box('Error', 'El RFC debe tener 13 caracteres.')
            return

        if not self.validar_rfc(name):
            util.msg_box('Error', 'El RFC ingresado no es válido.')
            return

        try:
            # Intentar capturar los embeddings faciales de la imagen más reciente
            embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
            
            # Verificar si se detectaron caras
            if not embeddings:
                # No se detectaron caras, informar al usuario
                util.msg_box('Error', 'No se detectó ninguna cara en la imagen. Por favor, mire.')
                return

            # Utiliza el primer embedding detectado para la lógica de guardado
            embedding = embeddings[0]
            
            # Check if RFC already exists
            if self.rfc_exists(name):
                # RFC exists, ask if user wants to update
                response = msgbox.askyesno("Actualizar", "Este RFC ya está registrado. ¿Desea actualizar las fotos?")
                if response:
                    self.save_user_data(name, embedding, update=True)
                    util.msg_box('Éxito!', 'Usuario actualizado exitosamente!')
                else:
                    util.msg_box('Información', 'Operación cancelada por el usuario.')
            else:
                self.save_user_data(name, embedding)
                util.msg_box('Éxito!', 'Usuario capturado exitosamente!')
    

        except Exception as e:
            util.msg_box('Error', f'Un error inesperado ocurrió: {str(e)}')
            if hasattr(e, 'message'):
                util.msg_box('Error', e.message)

    def save_user_data(self, name, embedding, update=False):
        # Guardar la imagen serializada en la carpeta local
        file_path = os.path.join('./db', f'{name}.pickle')
        with open(file_path, 'wb') as file:
            pickle.dump(embedding, file)
        
        # Guardar la imagen como foto normal en la subcarpeta 'imagenes'
        images_dir = './db/imagenes'
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        image_path = os.path.join(images_dir, f'{name}.jpg')
        self.most_recent_capture_pil.save(image_path)

    def rfc_exists(self, name):
        # Check if the pickle file exists for the given name (RFC)
        file_path = os.path.join('./db', f'{name}.pickle')
        return os.path.exists(file_path)


if __name__ == "__main__":
    app = RegisterUserApp()
    app.register_window.mainloop()
