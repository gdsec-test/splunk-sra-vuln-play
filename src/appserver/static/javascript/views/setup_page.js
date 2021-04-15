"use strict";

import * as Config from './setup_configuration.js'
import * as StoragePasswords from './storage_passwords.js'

const SECRET_REALM = 'splunk_sra_vuln_play_realm'

export async function perform(splunk_js_sdk, setup_options) {
    var app_name = "splunk_sra_vuln_play";

    var application_name_space = {
        owner: "nobody",
        app: app_name,
        sharing: "app",
    };

    try {
        // Create the Splunk JS SDK Service object
        const splunk_js_sdk_service = Config.create_splunk_js_sdk_service(
            splunk_js_sdk,
            application_name_space,
        );

        let { username, password } = setup_options;

        await StoragePasswords.write_secret(
            splunk_js_sdk_service,
            SECRET_REALM,
            "service_account", // SECRET_NAME
            `${username},${password}`
        )
        // Completes the setup, by access the app.conf's [install]
        // stanza and then setting the `is_configured` to true
        await Config.complete_setup(splunk_js_sdk_service);

        // Reloads the splunk app so that splunk is aware of the
        // updates made to the file system
        await Config.reload_splunk_app(splunk_js_sdk_service, app_name);

        // Redirect to the Splunk App's home page
        Config.redirect_to_splunk_app_homepage(app_name);
    } catch (error) {
        // This could be better error catching.
        // Usually, error output that is ONLY relevant to the user
        // should be displayed. This will return output that the
        // user does not understand, causing them to be confused.
        console.log('Error:', error);
        alert('Error:' + error);
    }
}