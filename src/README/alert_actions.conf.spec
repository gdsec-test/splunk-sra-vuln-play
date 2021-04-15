
[create_service_now_ticket]
param.service_username = <string>
* Username of the Service-Now user to create the ticket with.
* Required. 
* Set from the Set Up page for this app.

param.service_password = <string>
* Password of the Service-Now user to cerate the ticket with.
* Required. 
* Set from the Set Up page for this app.

param.environment = <string> 
* The service-now environment to send the ticket to.
* Required.
* Default = "dev"

param.ticket_urgency = <number>
* Urgency of the ticket.
* Required.
* Default = 3

param.ticket_impact = <number>
* Impact of the ticket.
* Required.
* Default = 3

param.ticket_title = <string>
* Title of the ticket.
* Required.

param.ticket_criticality = <string>
* Criticality of the ticket.

param.ticket_description = <string>
* Description of the ticket.
* Default = none

param.assign_to_manager = <string>
* Whether to default assign tickets to the manager of the assignment group.
* Required.
* Default = "No"

param.ticket_custom_tag = <string>
* Custom tag in the "Other Info" portion of the ticket.
* Default = none


