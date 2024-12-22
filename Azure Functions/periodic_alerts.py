import azure.functions as func
import logging
from utils.db_connection import client
from utils.send_email import send_email

periodic_alerts_for_due_challan = func.Blueprint()

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"

ALERT_EMAIL_SUBJECT = "Pending Challans on your vehicle with vehicle number - {0}"
ALERT_EMAIL_BODY = """Hello Sir,<br>
        You have pending challans on your vehicle with vehicle number {0}.<br>
        Total Amount you have to pay is {1}.<br>
        Log in to our portal for detail description of your challans and to pay your challans.<br>
        If you won't pay your challans then your challans will be auto payed on your next toll visit.<br>
        If your fastag won't have enough balance,then your fastag will be blacklisted"""

PROD_CRON_JOB = "00 00 4 15 * *" # 9:30 ist or 4:00 am utc 
TEST_CRON_JOB = "00 25 12 22 * *"


@periodic_alerts_for_due_challan.timer_trigger(schedule=PROD_CRON_JOB, arg_name="myTimer") 
def periodic_due_challan_alert(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    try:
        logging.warning("Started the timer")
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        query = 'SELECT c.vehicleId,c.amount FROM c WHERE c.status = "unsettled"'
        logging.error(query)
        query_results = list(challan_container.query_items(query=query,enable_cross_partition_query=True))
        logging.error(query_results)

        vehicle_to_challan = {}
        for result in query_results:
            try:
                vehicle_to_challan[result['vehicleId']]+=result['amount']
            except KeyError:
                vehicle_to_challan[result['vehicleId']]= result['amount']

        logging.warning(vehicle_to_challan)

        vehicleIds = tuple(vehicle_to_challan.keys())
        query = 'SELECT c.email,c.id from c where c.id IN {0}'.format(vehicleIds)
        email_to_vehicleIds = list(vehicle_container.query_items(query=query, enable_cross_partition_query=True))

        vehicle_to_email_map = {}
        for email_to_vehicle in email_to_vehicleIds:
            vehicle_to_email_map[email_to_vehicle['id']]= email_to_vehicle['email']
        logging.warning(vehicle_to_email_map)

        for vehicle in vehicle_to_challan.keys():
            email = vehicle_to_email_map[vehicle]
            amount = vehicle_to_challan[vehicle]
            vehicleId = vehicle

            new_subject = ALERT_EMAIL_SUBJECT.format(vehicleId)
            new_body = ALERT_EMAIL_BODY.format(vehicleId,amount)
            send_email(email,new_subject,new_body)
            logging.info(f"Email sent to email {email}")
        logging.warning("Done")
    except Exception as e:
        logging.error(e)