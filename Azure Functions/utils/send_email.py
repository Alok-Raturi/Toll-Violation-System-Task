from azure.communication.email import EmailClient

def send(email,subject,body):
    try:
        connection_string = "endpoint=https://toll-communication-service-for-email.unitedstates.communication.azure.com/;accesskey=5oK6ySgredGIxn7SdxIHKBfeg4gNzrj23iAq3Ntc0P7oMf1BDlkyJQQJ99ALACULyCptxpY3AAAAAZCSeJxb"
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "DoNotReply@da4951cc-4acd-446c-b9a6-faf9d6e53785.azurecomm.net",
            "recipients": {
                "to": [{"address": "<to_email>"}]
            },
            "content": {
                "subject": "Test Email",
                "plainText": "Hello world via email.",
                "html": """
				<html>
					<body>
						<h1>Hello world via email.</h1>
					</body>
				</html>"""
            },
            
        }

        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result.message_id)

    except Exception as ex:
        print(ex)


