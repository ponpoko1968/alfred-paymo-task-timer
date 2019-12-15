# alfred-paymo-task-timer
This workflow displays all tasks in 'paymo' and starts a timer for the selected task.

At first,
You have to get API Key following URL:
https://app.paymoapp.com/#Paymo.module.myaccount/api-keys

and create JSON file and place your home directory named as '.paymoapi.secret.json'

```
{"secret" : "<<YOUR API KEY>>"}
```


[Download](https://github.com/ponpoko1968/alfred-paymo-task-timer/files/3934763/Start.Paymo.Timer.zip)


or

[Packal](http://www.packal.org/workflow/start-paymo-task-timer)


# trouble shooting
if you got following error:
```
(snip)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.7/lib/python3.7/ssl.py", line 1117, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1056)
```
see.
https://stackoverflow.com/questions/57630314/ssl-certificate-verify-failed-error-with-python3-on-macos-10-15
