# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# def send_email(subject, message):
#     sender_email = "your_email@gmail.com"  # Your email
#     receiver_email = "recipient_email@example.com"  # Receiver email
#     password = "your_password"  # Your email password

#     # Create message container
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = subject

#     # Add message body
#     msg.attach(MIMEText(message, 'plain'))

#     # Establish a secure session with the SMTP server
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()

#     # Login using your credentials
#     server.login(sender_email, password)

#     # Send the email
#     server.sendmail(sender_email, receiver_email, msg.as_string())

#     # Close the SMTP server connection
#     server.quit()

# # Example function that triggers email notification
# def check_event():
#     # Example condition, replace with your own condition
#     if some_condition:
#         subject = "Notification: Event Occurred"
#         message = "The event you are monitoring has occurred."
#         send_email(subject, message)

# # Your main code
# if __name__ == "__main__":
#     # Your main code logic here
#     # Check for events and call check_event() when necessary
