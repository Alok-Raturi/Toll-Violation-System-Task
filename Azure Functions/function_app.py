import azure.functions as func
import rto_trigger
import user_trigger
import police_trigger
import toll_trigger


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(rto_trigger.rto_triggers)
app.register_functions(user_trigger.user_trigger)
app.register_functions(police_trigger.police_trigger)
app.register_functions(toll_trigger.toll_trigger)