# Table of Contents

[ServiceNow Ticketing From Splunk](#servicenow-ticketing-from-splunk)

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Global Configuration](#global-configuration)
4. [Creating and Editing an Alert Action](#creating-and-editing-an-alert-action)
5. [Service-Now Configuration](#service-now-configuration)
    - [Options](#options)
    - [Field Injection](#field-injection)
    - [Rolling Up Alerts](#rolling-up-alerts)
6. [Directory Structure](#directory-structure)
7. [Modifying the App](#modifying-the-app)
8. [Testing](#testing)
9. [Manually Trigger an Alert Action](#manually-trigger-an-alert-action)
10. [Troubleshooting](#troubleshooting)
11. [Logs](#logs)
12. [App Inspect](#app-inspector)

# ServiceNow Ticketing From Splunk

This app (Splunk SRA Vuln Play) is designed for use within GoDaddy's Splunk Cloud instance. It contains a Splunk custom alert action that allows you to create ServiceNow tickets from events and populate various fields with data from that event.

## System Requirements

- Splunk version 6.3 or greater
- Windows, Linux or Mac OS operating system

## Installation

This requires that you have the app packaged into its .spl form. Refer to [Packaging the App](#Packaging-the-App) on how to package the app.

### Local

App installation require admin priveleges in Splunk. From you local instance:

- Log into the web portal
- Under Apps, navigate to "Manage apps" and click "Install app from file"
- Upload the app bundle (.spl)
- Choose "Set up now" to skip the steps below or you can do so later by following them. This is where you enter the username and password of the Service-Now service account. You can change these settings at any time.


### Splunk Cloud

Installation requires opening a support ticket with Splunk.

- Log into https://splunk.com
- Under "Support", click "Support Portal".
- "Submit a New Case".
- Select "Splunk Cloud" and fill in the relevant information for the deployment, keeping in mind this is installing / updating an app. In the description, note that you'd like the attached file deployed. Don't worry about attaching the .spl file yet.
- After you submit, navigate to the new case and click "Add File" at the top. Select the .spl file of the app and add it to the case.
- Monitor your email for emails from Splunk regarding the case.

Below is an example of what a case might look like once created.
![example](/README/example_case.png)


### Global Configuration

In order to use Splunk SRA Vuln Play, a Service-Now accessible service account's login credentials must be saved in the app's settings.

In order to setup the app, in the Splunk header nav navigate to "Settings" -> "Alert actions". Click on "Setup Splunk SRA Vuln Play".

On the setup screen, provide the username and password of the account that will be used to create the tickets. It is best practice to use a service account here.

You can change these settings at any time.


## Creating and Editing an Alert Action

To create a new alert, run the query you would like to create SNOW tickets on in the Splunk interface.

First make sure you are in the right Splunk App. The alert will be associated with that app and it's a pain to change the associated app. The most common app will be Search & Reporting. You can change apps in the top-left header menu.

After you have ran the query, click "Save As..." > Alert. Settings:

- Title: Splunk will force this to be unique. Use something short and description.
- Description: Should contain two lines for record-keeping:
  - Created by - (name or username)
  - Last Edited by - (name or username)
- Permissions: Shared in App
- Alert Type: "Scheduled" **(Do NOT use Real-time)**
  - Run on Cron Schedule
  - Timerange: Whatever the interval used in the cron below is, best to use "Relative" and check "Beginning of \<interval\>".
  - Cron Expression: Cron that determines when the alert check runs
- Expires: 30 days
- Trigger alert when: Per-Result
- Add a throttle if you'd like
- Trigger Actions > Add Actions > Service-Now
- Fill in the relevant Service-Now ticket configuration (explained below)
- Save

When filling in text fields in the Service-Now alert configuration, you can specify fields in the Splunk data by wrapping them in `{{}}` in addition to specifying nested fields with `.` in-between the fields `like.this.example`. You can also use `now` or `_time` for Detect Time and event Time fields, which will fill in the system time the alert was triggered and the time that the Splunk event was created respectively.

## Service-Now Configuration

Each of these items has a short description next to them in the UI.

### Options

- Environment: Whether to push to servicenow "Dev" instance or "Production". Use "Dev" for testing.
- Raw: "Yes" will parse fields out of the response. This only works for events that are 100% valid json. Can be useful in tmporary cases if the data is not yet extracted but an alert must be created.
- Table: Which ServiceNow table to publish the ticket to. Current only supports the `u_physical_security` table but is built to be expandable for new tables and fields.
- State: Initial state of the ticket. Useful in special cases like heartbeats where the ticket is better off closed on creation.
- Title: Ticket of the ticket. Supports field injection (explained below).
- Impact: 1-3 Impact value of the ticket.
- Urgency: 1-3 Urgency value of the ticket.
- Summary: Main body of text that will go into the "summary" or "description" fields of tickets. Supports field injection.
- Assignment Group: ServiceNow UID or **hard-coded** alias of the group assigned to the ticket. Supported aliases are found in `$splunk_sra_vuln_play_ROOT/bin/constants.py`.
- Category: Category of the ticket. Case-sensitive. Must be a drop-down from this table as show in Service-Now.
- Sub-Category: Sub-category of the ticket. Case-sensitive. Must be a drop-down from this table as show in Service-Now.
- Detection Method: (For `u_physical_security` table) Detection Method of the ticket. Case-sensitive. Must be a drop-down from this table as show in Service-Now.
- Detect Time: Event field that is an ISO 8601 timestamp, or `now`. `now` use the tickets time of creation as the value. 
- Event Time: Event field that is an ISO 8601 timestamp, or `now`. `now` use the tickets time of creation as the value. 
- DSR? (For `u_physical_security` table) Whether to check the DSR checkbox or not.
- Roll Up Duration: How long in seconds between events to aggregate. Leave empty to create a ticket for every alert trigger.
- Rolling? Whether or not to use the first event time, or most recent event time, combined with the duration to determine roll-up.
- Reopen? Whether or not to append events and reopen a closed ticket, or create a new one within the roll up time.
- Match Fields: Which event field(s), if any, to check for a match, only rolling up tickets with matching fields. Comma-separated value.


### Field Injection

Field injection works with extracted fields, and event fields when `Raw` is "`Yes`" with a valid json event. Fields are injected into supporting config options between a pair of double-curly braces like `{{foo}}`. To inject an extracted field, put the exact name as it shows in Splunk between the curly braces. To inject a raw field from json, separate nested values with dot notation.

Example, to insert "bar" from the following json:
```json
{ "foo": { "bar": 2 } }
```
use: `{{foo.bar}}`. In this example, "`1 {{foo.bar}} 3`" would become "`1 2 3`".

If the value is a json object, it will be a string representation of the json. Fromthe example json before, "`1 {{foo}} 3`" would become "`1 { "bar": 2 } 3`"

### Rolling Up Alerts

Splunk SRA Vuln Play offers the ability for an alert to append multiple events to a single ticket given a set of criteria. By specifying `Roll Up Duration`, tickets will begin to be aggregated. Leaving this blank will have the script ignore the following options of `Rolling?`, `Reopen?`, and `Match Fields`. 

When specified `Rolling?` will affect how `Rolled Up Duration` behaves. When `Rolling?` is "`Yes`", `Rolled Up Duration` will be from the **most recent rolled-up event time**. Otherwise, it will be from the **first event** (the one that caused the ticket to be created). These two values determine the timeframe, `Reopen?` then determines whether a closed ticket will be reopened if an event should be rolled up into it based on the earlier values and `Match Fields`. When `Reopen` is "`Yes"`, a closed ticket will be reopened. When "`No`", a new ticket will be created. Finally, `Match Fields` are extracted fields, or the `Raw` json fields, to that will cause only events with these matching fields to be aggregated. This is useful in cases like only rolling up alert triggers with the same hostname, but otherwise creating new tickets for each unique host.

## Directory Structure

[Splunk Docs Overview.](https://dev.splunk.com/enterprise/docs/developapps/createapps/createsplunkapp/) Some directories are omitted.

```
splunk_sra_vuln_play/
├── appserver/
│    └── static/
│       └── javascript/ # react app files, mounted to default/data/ui/views/setup.xml
│       └── styles/     # css styles for react app
│       └── snow.png
├── bin/    # script files, main logic of the app
├── lib/    # python packages used by the app
├── default/
│   ├── alert_actions.conf  # param initialization and defaults
│   ├── app.conf  # app meta data
│   ├── data/
│   │   └── ui
│   │       └── alerts
│   │           └── create_service_now_ticket.html  # alert creation/editing pane
│   │       └── views
│   │           └── setup.xml   # root of setup page
├── metadata
│   └── default.meta
├── README
│   └── alert_actions.conf.spec  # (optional) param definitions
├── README.md
└── static
    ├── appIcon_2x.png
    └── appIcon.png
```

## Modifying the App

**NOTE:** When testing a deployment of the app, Splunk Enterprise may add some additional files and populate fields in the `splunk_sra_vuln_play/local/` and `splunk_sra_vuln_play/metadata`. Delete the `/local` directory and the `metadata/local.meta` file before exporting. Not doing so should trigger an error on the `is_configured` field in `splunk_sra_vuln_play/local/app.conf` when running the app through the [Splunk's CLI app inspector](https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/). This should be your cue to set that back to 0 and delete the aforementioned files as well as look through the directory for any other possible settings that may have been saved.

Important files and what they do (also visible in short above [Directory Structure](#directory-structure)):

- **splunk_sra_vuln_play/bin/create_service_now_ticket.py**
  The python script that runs on a triggered alert.
- **splunk_sra_vuln_play/default/setup.xml**
  The UI of the app's setup page that currently contains the Username and Password settings. ([Splunk's Setup Page Docs](https://dev.splunk.com/enterprise/docs/developapps/setuppage))
- **splunk_sra_vuln_play/default/data/ui/alerts/create_service_now_ticket.html**
  The UI of the configuration pane that shows when creating/editing an alert.

When editing `setup.xml` or `create_service_now_ticket.html`, make sure that the UI changes that modify parameters are reflected in `splunk_sra_vuln_play/default/alert_actions.conf`.

When making changes to the `create_service_now_ticket.py` script, in cli `cd` into the `splunk_sra_vuln_play/bin` directory and run the unit testing file `python3 -B -m unittest test_create_service_now_ticket.py`. This will ensure that any changes made do not break current functionality. If a change does cause tests to fail, understand that this may adversly affect existing alerts and that the unit test file should be updated accordingly.

## Packaging the App

When deploying an update to the app to the production instance, increment the `version` and `build` in `splunk_sra_vuln_play/default/app.conf`.
[Package the app](https://docs.splunk.com/Documentation/Splunk/6.0/AdvancedDev/PackageApp) (just a renamed tarball. You can `tar` the file to any location you prefer. YMMV if you try to `tar` without first `cd`ing to the foler with splunk_sra_vuln_play):

- cd $SPLUNK_HOME$/etc/apps/
- tar cv splunk_sra_vuln_play/ > ~/splunk_sra_vuln_play.tar
- gzip ~/splunk_sra_vuln_play.tar
- mv ~/splunk_sra_vuln_play.tar.gz ~/splunk_sra_vuln_play.spl
  When you're done with your modifications, run [Splunk's CLI app inspector](https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/ - link may be outdated, they change their docs often) against the newly created `splunk_sra_vuln_play.spl` package (located in your home directory if you used the commands above). If you encounter any errors here, refer to the [troubleshoot information below](#app-inspector).

Included into this repo is `packager.sh` which exemplifies what one might do to package this and similar splunk apps. Most notably is the `chmod` command that will quell the permissions error from the app inspector.

## Testing

### Manually Trigger an Alert Action

Creating a mock event from the original source will always be the best way to test your alert; however if this is not viable, then you can try the method below.

You can manually trigger the alert action if you want to verify the configuration and/or preview different parameter combinations. You can create the event with a command similar to below, replacing the escaped JSON and index to match your alert trigger.

Command:

```
| makeresults | eval _raw = "{\"my\":\"json\"}" | collect index="main" sourcetype=json
```

This is will trigger other alerts it matches so be sure to be as specific as possible. You may have to edit the `eval` statement to more accurately reflect the data/fields you need.

## Troubleshooting

### Logs

In order to investigate problems with the Slack alert action, you can check the logs of the
alert action.

- Navigate to "Settings" -> "Alert actions"
- Click on "View log events" for the Splunk SRA Vuln Play alert action

Additionally, more information can likely be found in the `_internal` index looking for the `splunkd.log` file logs and strings containing `ERROR` and/or `splunk_sra_vuln_play`.

### App Inspector

When verifying the app with [Splunk's CLI app inspector](https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/) you may enounter some errors. Here is what you can do for some of them.

Permissions:

> Source code and binaries standards

    Check that files outside of the bin/ and appserver/controllers directory do not have execute permissions and are not .exe files. Splunk recommends 644 for all app files outside of the bin/ directory, 644 for scripts within the bin/ directory that are invoked using an interpreter (e.g. python my_script.py or sh my_script.sh), and 755 for scripts within the bin/ directory that are invoked directly (e.g. ./my_script.sh or ./my_script).

On the app directory in `$SPLUNK_HOME/etc/apps/splunk_sra_vuln_play`, run `chmod -R 644` and `find /$SPLUNK_HOME/etc/apps/splunk_sra_vuln_play -type d -exec chmod 755 {} +`. This will outfit all files with 644 and all directories with 755. Read the error message for steps on scripts that are directly executed.

Already Configured:

> App.conf standards The app.conf file located at default/app.conf provides key application information and branding. For more, see app.conf. Check that default/app.conf setting is_configured = False. FAILURE: The app.conf [install] stanza has the `is_configured` property set to true. This property indicates that a setup was already performed. File: default/app.conf Line Number: #

As mentioned under the [Modifying the App](#modifying-the-app), delete the `/local` directory and the `metadata/local.meta` file before exporting. This should be your cue to set that back to 0 and delete the aforementioned files as well as look through the directory for any other possible settings that may have been saved.
