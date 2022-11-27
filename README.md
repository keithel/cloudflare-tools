# Cloudflare Tools

## cf_update_ddns

`cf_update_ddns.py` uses Cloudflare APIs to update the IP address of a domain name.
Useful for updating routinely with a cron job when you do not have a static IP address.

To use:
 * Acquire a Cloudflare token that has permission to edit zone DNS information. ("Edit Zone DNS" template works well)
   * Log into your Cloudflare account
   * Bring up your profile (top right)
   * Choose API Tokens on the left.
   * Click Edit zone DNS "Use template" button.
   * Pick specific zones you wish to limit the editing to.
   * Filter IPs that can use this token if you wish.
   * Specify a time period when this token will be active.
   * Click "Continue to Summary"
   * Click "Create Token"
 * Provide your token to the script one of two ways:
   * `CF_TOKEN` environment variable
   * `cf.token` file. The file should have just the token, nothing else except optional whitespace.

## References

https://github.com/cloudflare/python-cloudflare was helpful for seeing how to use the API.
The examples contained therein were also useful.
