import smtplib
import os


class EmailNotification:

    def __init__(self, recipient, name, phone, customer_message):
        self.recipient = recipient
        self.name = name
        self.email = os.environ.get('EMAIL')
        self.password = os.environ.get('EMAIL_PASSWORD')
        self.phone = phone
        self.customer_message = customer_message

    def send_email(self):
        subject = "Shitty Blog Message"
        body = f"Name: {self.name}\nEmail: {self.email}\nPhone: {self.phone}\nMessage: {self.customer_message}"
        message = f"Subject: {subject}\n\n{body}"
        print(message)
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection = smtplib.SMTP('smtp.mail.ru', 587)
            connection.ehlo()
            connection.starttls()
            connection.login(self.email, self.password)
            connection.sendmail(self.email, self.recipient, message.encode('utf-8'))
            print('sent')
            connection.quit()

