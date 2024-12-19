from azure.communication.email import EmailClient

def send_email(email,subject,body):
    try:
        connection_string = "endpoint=https://communication-service-for-toll.unitedstates.communication.azure.com/;accesskey=ENJ48K6twmU2MZmxeVf5u65viQg82qSKahBcegYiwKaFu861DCc8JQQJ99ALACULyCptxpY3AAAAAZCSFST3"
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "DoNotReply@c3a20657-8e72-4349-a98c-be7b948ea113.azurecomm.net",
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

    except Exception as ex:
        print(ex)

