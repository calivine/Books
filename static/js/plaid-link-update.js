// Initialize Link with the token parameter
// set to the generated public_token for the Item
let public_token = $('.plaid-public-token').attr('id');
let environment = $('.plaid-environment').attr('id');
let linkHandler = Plaid.create({
    env: environment,
    clientName: 'The Vault',
    key: '246a82fe1a27ee4ddaecc9090d145f',
    product: ['auth', 'transactions'],
    token: public_token,
    onSuccess: function (public_token, metadata) {
        // You do not need to repeat the /item/public_token/exchange
        // process when a user uses Link in update mode.
        // The Item's access_token has not changed.
    },
    onExit: function (err, metadata) {
        // The user exited the Link flow.
        if (err != null) {
            // The user encountered a Plaid API error prior
            // to exiting.
            console.log(err['error_type'], err['error_message'])
        }
        // metadata contains information about the institution
        // that the user selected and the most recent API request
        // IDs. Storing this information is helpful for support.
    },
});
// Trigger the authentication view
document.getElementById('linkButton').onclick = function () {
// Link will automatically detect the institution ID
// associated with the public token and present the
// credential view to your user.
    linkHandler.open();
};