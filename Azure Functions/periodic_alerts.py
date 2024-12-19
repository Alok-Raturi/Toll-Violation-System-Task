import azure.functions as func
import logging

periodic_alerts_for_due_challan = func.Blueprint()


@periodic_alerts_for_due_challan.timer_trigger(schedule="* * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def periodic_due_challan_alert(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')