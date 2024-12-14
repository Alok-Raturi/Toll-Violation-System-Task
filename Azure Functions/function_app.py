import azure.functions as func
import rto_trigger
import user_trigger

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(rto_trigger.rto_triggers)
app.register_functions(user_trigger.user_trigger)