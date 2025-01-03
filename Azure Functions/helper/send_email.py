from azure.communication.email import EmailClient
import os
import logging

# 
def send_email(email,subject,body):
    try:
        connection_string = "endpoint=https://communication-service-for-toll.unitedstates.communication.azure.com/;accesskey=9mWGXvskMFU2kHlSGMyPptDkuhftu3nILPhGYZWLx9fEOCKCRgagJQQJ99ALACULyCptxpY3AAAAAZCS38jF"
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": f"DoNotReply@64e7b640-b76a-4e00-8695-562d72a87429.azurecomm.net",
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
        logging.warning("Email sent successfully")

    except Exception as e:
        logging.warning(e)

