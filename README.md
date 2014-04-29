#Metanoia Bitmessage Mining Server

## Description
Metanoia mining server is the first attempt to implement [Bitmessage](https://bitmessage.org) proof-of-work mining server (and protocol). I believe this codebase should solve some future POW related implementation issues on the Android platform. The server is implemented using queue mechanism and simplest possible JSON over the TCP protocol.

**WARNING:** Current version is only an academic proof of concept with a no expectation of an existing threat model. So no HMAC, SSL, zero-knowledge, protocol error codes, ...

## Motivation
[Reddit: How to provide work as a potential service?](https://pay.reddit.com/r/bitmessage/comments/1fbze6/how_to_provide_work_as_a_potential_service/)
[Reddit: An alternative to proof of work?](https://pay.reddit.com/r/bitmessage/comments/1q02qc/an_alternative_to_proof_of_work/)


##Requirements
*Metanoia* is built in Python 2.7.3 using the built-in modules only. It should work with other versions.

##Protocol overview by example
Client sends request (*initialHash* is Base64 encoded):
```
{
  u'method': u'do_pow',
  u'target': 3979158916983L,
  u'initialHash': u'vSJ95SFzpQ7NVIk/cd5SUR9isX+s8s5mcKJIn4G3Owqk7/yBuTX2KPxTg8RpkO1yJJ0bz7/8/5KMU5BEcjxehw=='
}
```
Miners periodically calls *get_work* which is implemented as long pooling:
```
{
  'method':'get_work'
}
```

Miners are awakened, one of them receives a message:
```
{
  "status": 200,
  "target": 3979158916983,
  u'initialHash': u'vSJ95SFzpQ7NVIk/cd5SUR9isX+s8s5mcKJIn4G3Owqk7/yBuTX2KPxTg8RpkO1yJJ0bz7/8/5KMU5BEcjxehw=='
}
```

After computation, miner returns completed work via *push_result* method:
```
{
  u'method': u'push_result',
  u'nonce': 1302572,
  u'trialValue': 799892720325L,
  u'initialHash': u'vSJ95SFzpQ7NVIk/cd5SUR9isX+s8s5mcKJIn4G3Owqk7/yBuTX2KPxTg8RpkO1yJJ0bz7/8/5KMU5BEcjxehw=='
}
```

The message received by client:
```
{
  "status": 200,
  "nonce": 1302572,
  "trialValue": 799892720325
}
```

##Download
Just `clone` this repository:
```
git clone https://github.com/viralpoetry/metanoia
```

##Usage
###Server
Edit configuration file `settings.py`. Content should be self-explanatory.
Run `python server.py`, you should see:
```
INFO:__main__:Starting Metanoia mining service...
INFO:__main__:Server started...
```
###Client
Backup and replace `proofofwork.py` file inside `PyBitmessage\src` directory with one from this repository. Change server address. Enjoy :)

##Contact
* BM-2cVD15UyXVELPakkKfYv2Y43QzUnryfmUj
* petergasper [uknowwhat] viralpoetry.org
