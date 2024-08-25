from bs4 import BeautifulSoup
from datetime import date
from email.message import EmailMessage
from utils.database import Database
from utils.image_generator import generate_image

import pandas as pd
import logging
import asyncio
import aiosmtplib
import aiofiles

logger = logging.getLogger(__name__)

class FormatInvoice:

    def __init__(self, file_path, customer_mail, order_number):
        self.file_path = file_path
        self.html = None
        self.customer_mail = customer_mail
        self.order_number = order_number

    async def format_invoice(self):
        async with aiofiles.open(self.file_path, mode='r', encoding='utf-8') as file:
            content = await file.read()
            self.html = BeautifulSoup(content, 'lxml')
        
        customer_mail = self.html.find(string='sisters@gmail.com')
        order_number = self.html.find(string='#number')
        invoice_date = self.html.find(string='invoice_date')

        customer_mail.replace_with(self.customer_mail)
        order_number.replace_with(self.order_number)
        invoice_date.replace_with(date.today().strftime("%B %d, %Y"))

        return self.html.prettify()

class Mail:

    def __init__(self, subject, sender, receiver, attachment, html, login_email='xx', login_password='xx') -> None:
        self.message = EmailMessage()
        self.subject = subject
        self.sender = sender
        self.receiver = receiver
        self.attachment = attachment
        self.html = html
        self.login_email = login_email
        self.login_password = login_password

    async def send(self):
        self.message['Subject'] = self.subject
        self.message['From'] = self.sender
        self.message['To'] = self.receiver
        self.message.set_content(self.html, subtype='html')

        async with aiofiles.open(self.attachment, mode='rb') as content_file:
            content = await content_file.read()
            self.message.add_attachment(content, maintype='image', subtype='jpg', filename='boarding-pass.jpg')

        async with aiosmtplib.SMTP(hostname='smtp.gmail.com', port=587) as smtp:
            await smtp.login(self.login_email, self.login_password)

            try:
                await smtp.send_message(self.message)
            except Exception as exc:
                print(exc)
            finally:
                return 'Success'

class Sheets:

    def __init__(self, sheets_id, database: Database=Database) -> None:
        self.sheets_id = sheets_id
        self.db = database

    async def insert_to_db(self):
        while True:
            try:
                sheets = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{self.sheets_id}/export?format=csv')

                for x in range(0, len(sheets['Email address'])):
                    attendance = sheets['Will you be able to attend?'][x]
                    email = sheets['Email address'][x]
                    name = sheets['What is your name?'][x]
                    age = sheets['What is your age?'][x]
                    hobby = sheets['What is your hobby?'][x]
                    zone = sheets['What zone are you from?'][x]
                    profile = sheets["Please upload a selfie of yourself!"][x]

                    check = await self.db.record("SELECT * FROM respondent WHERE email = ?", email)
                    
                    if check is None:
                        await self.db.autoexecute(
                            "INSERT INTO respondent(email, name, age, hobby, zone, profile, email_sent, attendance) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            email, name, int(age), hobby, zone, profile, 0, attendance
                        )
                        logger.info(f"Inserted {name} to database")

                await asyncio.sleep(1)
            except Exception as exc:
                logger.critical(exc)
                continue

        
class Checker:

    def __init__(self, database: Database=Database) -> None:
        self.db = database
        self.queue = []

    async def check_for_unsent(self):
        while True:
            database = await self.db.recordall('SELECT * FROM respondent')
            for index, respondent in enumerate(database, 1):
                if int(respondent[6]) == 0 and respondent[7] == "Yes":
                    logger.info(f'Task scheduled for {respondent[0]}')

                    await self.db.autoexecute(
                        "UPDATE respondent SET email_sent = ? WHERE email = ?", 1, 
                        respondent[0]
                    )
                    send_mail = asyncio.create_task(
                        self.send_mail(
                            email=respondent[0],
                            name=respondent[1],
                            hobbies=respondent[3],
                            zone=respondent[4],
                            image_url=respondent[5],
                            queue=str(index)
                        )
                    )
                    self.queue.append(send_mail)
        
            for q in reversed(range(len(self.queue))):
                coro = self.queue[q]
                try:
                    await coro
                    del self.queue[q]
                except Exception as exc:
                    logger.critical(exc)
                
            await asyncio.sleep(1)

    @staticmethod
    async def send_mail(email, name, hobbies, zone, image_url, queue):
        await generate_image(
            name=name,
            hobbies=hobbies,
            zone=zone,
            image_url=image_url,
            output_path=f'./assets/boarding_pass/{email}-boarding-pass.jpg'
            )
        
        invoice = FormatInvoice(
            file_path='./assets/templates/mail.html',
            customer_mail=email,
            order_number=f'#SAD{queue}'
        )

        formatted_invoice = await invoice.format_invoice()

        mail = Mail(
            subject='Sisters Airways Invoice',
            sender='SAD Airways',
            receiver=email,
            attachment=f'./assets/boarding_pass/{email}-boarding-pass.jpg',
            html=formatted_invoice
        )
        await mail.send()
        logger.info(f'Email sent for {email}')
