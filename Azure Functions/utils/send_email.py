from azure.communication.email import EmailClient
import os
import logging

def send_email(email,subject,body):
    try:
        connection_string = os.getenv("CONNECTION_STRING")
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": f"DoNotReply@{os.getenv('SENDER_DOMAIN')}",
            "recipients": {
                "to": [{"address": f"{email}"}]
            },
            "content": {
                "subject": f"{subject}",
                "plainText": f"{body}",
                "html": f"""
				<html>
					<body>
						<h1>Important Message </h1>
                        <p>{body}</p>
					</body>
				</html>"""
            },
            
        }

        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result.message_id)
        logging.warning("Email sent successfully")

    except Exception as e:
        logging.warning("Can't send email")

