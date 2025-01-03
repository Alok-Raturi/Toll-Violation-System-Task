import azure.functions as func
import logging
from database.connection import vehicle_container,challan_container
from helper.send_email import send_email

periodic_alert = func.Blueprint()

ALERT_EMAIL_SUBJECT = "Pending Challans on your vehicle with vehicle number - {0}"
ALERT_EMAIL_BODY = """Hello Sir,<br>
        You have pending challans on your vehicle with vehicle number {0}.<br>
        Total Amount you have to pay is {1}.<br>
        Log in to our portal for detail description of your challans and to pay your challans.<br>
        If you won't pay your challans then your challans will be auto payed on your next toll visit.<br>
        If your fastag won't have enough balance,then your fastag will be blacklisted"""

PROD_CRON_JOB = "00 00 4 15 * *" 
TEST_CRON_JOB = "00 25 12 22 * *"


@periodic_alert.timer_trigger(schedule="", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def periodic_due_challan_alert(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    try:
        logging.warning("Started the timer")

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
        query = 'SELECT c.email,c.id from c where c.id IN @vid'
        email_to_vehicleIds = list(vehicle_container.query_items(query=query,parameters=[
            {"name":"@vid","value":vehicleIds}
        ], enable_cross_partition_query=True))

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