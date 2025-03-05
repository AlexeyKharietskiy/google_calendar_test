import os
import datetime
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'


class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Calendar Manager")

        self.creds = None
        self.service = None

        self.create_widgets()

        self.check_existing_token()

    def create_widgets(self):
        tk.Label(self.root, text="Название события:").grid(row=0, column=0, padx=10, pady=5)
        self.event_name = tk.Entry(self.root, width=30)
        self.event_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=10, pady=5)
        self.event_date = tk.Entry(self.root, width=30)
        self.event_date.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Время (ЧЧ:ММ):").grid(row=2, column=0, padx=10, pady=5)
        self.event_time = tk.Entry(self.root, width=30)
        self.event_time.grid(row=2, column=1, padx=10, pady=5)

        self.auth_button = tk.Button(self.root, text="Авторизация", command=self.start_auth_thread)
        self.auth_button.grid(row=3, column=0, padx=10, pady=10)

        self.add_button = tk.Button(self.root, text="Добавить событие", command=self.add_event)
        self.add_button.grid(row=3, column=1, padx=10, pady=10)

    def check_existing_token(self):
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if not self.creds.valid:
                if self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    self.creds = None
            if self.creds:
                self.service = build('calendar', 'v3', credentials=self.creds)
                messagebox.showinfo("Информация", "Авторизация выполнена автоматически!")

    def start_auth_thread(self):
        Thread(target=self.authenticate).start()

    def authenticate(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
                redirect_uri='http://localhost:8080/'
            )
            self.creds = flow.run_local_server(port=8080)
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
            self.service = build('calendar', 'v3', credentials=self.creds)
            messagebox.showinfo("Успех", "Авторизация прошла успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка авторизации: {str(e)}")

    def add_event(self):
        if not self.service:
            messagebox.showerror("Ошибка", "Сначала выполните авторизацию!")
            return

        try:
            event_name = self.event_name.get()
            date_str = self.event_date.get()
            time_str = self.event_time.get()

            # Преобразование даты и времени
            start_time = datetime.datetime.strptime(f"{date_str}T{time_str}:00", "%Y-%m-%dT%H:%M:%S")
            end_time = start_time + datetime.timedelta(hours=1)

            event = {
                'summary': event_name,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Moscow',
                },
            }

            self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            messagebox.showinfo("Успех", "Событие успешно добавлено в календарь!")
            self.clear_fields()

        except ValueError:
            messagebox.showerror("Ошибка", "Неправильный формат даты или времени!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении события: {str(e)}")

    def clear_fields(self):
        self.event_name.delete(0, tk.END)
        self.event_date.delete(0, tk.END)
        self.event_time.delete(0, tk.END)


if __name__ == '__main__':
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()