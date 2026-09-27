import os
import smtplib
from email.message import EmailMessage

msg = EmailMessage()

msg["Subject"] = "Weekly Swing Trading Report"

msg["From"] = os.environ["GMAIL_USER"]

msg["To"] = os.environ["EMAIL_TO"]

msg.set_content(
    "Attached is your Weekly Swing Trading Report."
)

with open(
    "weekly_watchlist.xlsx",
    "rb"
) as f:

    msg.add_attachment(
        f.read(),
        maintype="application",
        subtype="octet-stream",
        filename="weekly_watchlist.xlsx"
    )

server = smtplib.SMTP(
    "smtp.gmail.com",
    587
)

server.starttls()

server.login(
    os.environ["GMAIL_USER"],
    os.environ["GMAIL_PASSWORD"]
)

server.send_message(msg)

server.quit()

print("Email sent successfully")
