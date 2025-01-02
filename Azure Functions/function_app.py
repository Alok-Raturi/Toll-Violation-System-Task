import azure.functions as func
from controllers.rto_controller import rto_triggers
from controllers.entities_controller import entities_triggers
from controllers.periodic_alerts import periodic_alerts_for_due_challan

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(rto_triggers)
app.register_functions(entities_triggers)
app.register_functions(periodic_alerts_for_due_challan)