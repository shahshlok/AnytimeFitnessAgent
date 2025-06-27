import os
from datetime import datetime, timezone
import hubspot
from pprint import pprint
from hubspot.crm.objects import SimplePublicObjectInputForCreate, ApiException


def create_lead(name: str, email: str, summary: str):
    client = hubspot.Client.create(access_token=os.getenv("HUBSPOT_PERSONAL_KEY"))
    
    hs_appointment_start = datetime.now(timezone.utc).isoformat()
    
    properties = {
        "hs_appointment_start": hs_appointment_start,
        "name": name,
        "email": email,
        "summary": summary
    }
    
    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(
        properties=properties
    )
    
    try:
        api_response= client.crm.objects.basic_api.create(
            object_type= '0-421',
            simple_public_object_input_for_create=simple_public_object_input_for_create
        )
        
        pprint(api_response)
        
    except ApiException as e:
        print("Exception when calling BasicApi->create: %s\n" % e)
    