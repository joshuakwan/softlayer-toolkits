# SoftLayer Watcher

This tool is designed to poll updates of SoftLayer tickets/events against a configured
SoftLayer accounts and publish to somewhere.

# Features

* Polling events/tickets updates from SoftLayer.
* Only 1 single SoftLayer account is supported for 1 instance of this tool, which means you have to launch multiple processes in order to watch on a bunch of SoftLayer accounts.
* Serialize current states of events/tickets into disk and rebuild them when the tool is restarted.
* Only **unplannned** events are supported now.
* Support graceful ctrl+c shutdown.

# TODOs

* Handle exceptions.
* Support **planned** events.
* Implement a watch dog to watch on the watchers.

# Usage

Basic usage from the command line:

```
usage: softlayer_watcher.py [-h] [--sl-user <sl user account>]
                            [--sl-apikey <sl api key>]
                            [--notify <notification channel>]
                            [--slack-token <slack token>]
                            [--slack-channel <slack channel>]
                            [--interval <interval in minute>]

optional arguments:
  -h, --help            show this help message and exit
  --sl-user <sl user account>
                        SoftLayer Account Username
  --sl-apikey <sl api key>
                        SoftLayer Account API key
  --notify <notification channel>
                        Set notification channel, default is slack
  --slack-token <slack token>
                        Slack Token
  --slack-channel <slack channel>
                        Slack Channel
  --interval <interval in minute>
                        Polling interval in minute, default is 1 min
```

There are two ways to configure the things you need to run the watcher, one is to
specify them in the command line which is shown above, here is a quick sample:

```
> python softlayer_watcher.py --sl-user SOFTLAYER_USER --sl-apikey 12435abcde --notify slack --slack-token abcde12345 --slack-channel '#test' --interval 3
```

The other way (also preferred) is to configure the settings into the environment, but please notice

* The command line options will always override the environment variables.
* `interval` and `notify` can only be set via command line options

Here comes the sample of configuring environment variables:

```
export SLACK_TOKEN=abcde12345
export SLACK_CHANNEL='#random'
export SL_USER=SOFTLAYER_USER
export SL_APIKEY='12345abcde'
```
