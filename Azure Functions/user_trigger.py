import json
import azure.functions as func
from utils.db_connection import client, encode_token
from jose import JWTError

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"

user_trigger = func.Blueprint()


@user_trigger.route(route="user/login", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def user_triggers(req: func.HttpRequest) -> func.HttpResponse:
    print("User Login Trigger")
    try:
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)

        email = body['email']
        password = body['password']

        query = "SELECT * FROM c WHERE c.email = @email and c.password = @password"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name": "@email", "value": email},
                {"name": "@password", "value": password}
            ],
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            return func.HttpResponse(
                "Invalid Email or Password",
                status_code=404
            )
        else:
            token = encode_token({
                "email":email,
                "designation":items[0]['designation'],
                "id":items[0]['id']
            })
            return func.HttpResponse(
                token,
                status_code=200
            )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )