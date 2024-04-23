import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, receiver_email, subject, body, password):
    try:
        # Set up the SMTP server
        smtp_server = smtplib.SMTP('smtp.example.com', 587)  # Change this to your SMTP server and port
        smtp_server.starttls()
        
        # Login to the SMTP server
        smtp_server.login(sender_email, password)

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        smtp_server.send_message(msg)

        # Quit SMTP server
        smtp_server.quit()

        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email:", str(e))

# Example usage
sender_email = 'your_email@example.com'
receiver_email = 'recipient@example.com'
subject = 'Test email'
body = 'This is a test email sent using Python.'
password = 'your_email_password'

send_email(sender_email, receiver_email, subject, body, password)
