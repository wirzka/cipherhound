![Cipherhound](/img/cipherhound.png)

## Update 16/02/22
***N.B. I'm currently working on a new version of this tool to overcome some challenges and issues, the new version is going to have a few more feautures as well.***

# Cipherhound
Cipherhound is a tool to automate and speed up the information gathering of SSL/TLS certificates’ details to compare them with the latest [AgID guidelines](https://www.agid.gov.it/it/sicurezza/tls-e-cipher-suite). For those who are not familiar with AgID, as you can find on its website, it is the technical agency for the Presidency of the Council of Ministers (Italy).

I know there is a plethora of well-written and stable applications that could do it, but I like to struggle a bit and I created mine.

That’s why Cipherhound’s been born.
## TOC
- [Prerequisites & dependecies](#prerequisites--dependecies)
- [Installation](#installation)
- [Usage](#usage)
- [Cipherhound's logic](#cipherhounds-logic)
- [Limits](#limits)
- [Meta](#meta)
- [Disclaimer](#disclaimer)

## Prerequisites & dependecies

* Written in Python 3.8.6
* [Nmap](https://nmap.org/)
* For python modules check `requirements.txt`
* Tested on:
   * Windows 10
   * Ubuntu on WSL 2

## Installation

1. git clone [https://github.com/wirzka/cipherhound](https://github.com/wirzka/cipherhound/)
2. cd cipherhound
3. activate your virtual environment (_optional_)
4. `pip3 install -r requirements.txt`
5. `python3 cipherhound.py -h`

## Usage
### Helper message
`python3 cipherhound.py -h`

![Usage](/img/usage.PNG)

`python3 cipherhound.py -np acme.com.txt`

![Scan](/img/scan.png)
## Cipherhound's logic

I've tried to make it simple af. I didn't want to reinvent the whole wheel so that's why I've used nmap's scripts and Python.

The logic is quite straightforward:

1. Grab the subdomains from the given file;
2. For each subdomain add to it the root domain
3. Save all the crafted subdomains into the file *root_domain_ValidHostnames.txt* (root_domain is automatically captured from the input txt file);
4. Run ssl-enum-ciphers by giving in input the valid hostnames file and output to an XML file automatically named *root_domain_Cipher.xml*;
5. Run ssl-cert by giving in input the valid hostnames file and output to an XML file automatically named *root_domain_Validity.xml*;
6. Parse both XML files:
   1. Check output from ssl-enum-ciphers, compare it against the AgID's guidelines, and populate dictionary with the resulting values:
      ```bash
      * name: acme.com
      * 80: YES/NO
      * 443: YES/NO
      * SSLv3: YES/NO
      * TLSv1.0: YES/NO
      * TLSv1.1: YES/NO
      * TLSv1.2: YES/NO
      * TLSv1.3: YES/NO
      * SECURE: YES/NO
      ```
   2. Check certificate's validity date and populate dictionary with the resulting values:
      ```bash
      * name: acme.com
      * valid: YES/NO
      ```
7. Merge the two lists of dictionaries on equal host names;
8. Write the resulting list of dictionaries to an excel file named (guess what?) *root_domain.xlsx*.

## Limits

Cipherhound is based upon the following Nmap's scripts:

* [ssl-enum-ciphers](https://nmap.org/nsedoc/scripts/ssl-enum-ciphers.html)
* [ssl-cert](https://nmap.org/nsedoc/scripts/ssl-cert.html)

### ssl-enum-ciphers

This script, written by Mak Kolybabi and Gabriel Lawrence, retrieves a lot of interesting information from the SSL/TLS certificate as shown on Nmap's website:

```bash
PORT    STATE SERVICE REASON
443/tcp open  https   syn-ack
| ssl-enum-ciphers:
|   TLSv1.0:
|     ciphers:
|       TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048) - A
|       TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA (secp256r1) - C
|       TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA (secp256r1) - C
|       TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) - C
|       TLS_ECDHE_ECDSA_WITH_RC4_128_SHA (secp256r1) - C
|       TLS_ECDHE_RSA_WITH_RC4_128_SHA (secp256r1) - C
|       TLS_RSA_WITH_RC4_128_SHA (rsa 2048) - C
|       TLS_RSA_WITH_RC4_128_MD5 (rsa 2048) - C
|     compressors:
|       NULL
|     cipher preference: server
|     warnings:
|       64-bit block cipher 3DES vulnerable to SWEET32 attack
|       Broken cipher RC4 is deprecated by RFC 7465
|       Ciphersuite uses MD5 for message integrity
|       Weak certificate signature: SHA1
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_RSA_WITH_AES_128_GCM_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_GCM_SHA384 (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048) - A
|       TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA (secp256r1) - C
|       TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA (secp256r1) - C
|       TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) - C
|       TLS_ECDHE_ECDSA_WITH_RC4_128_SHA (secp256r1) - C
|       TLS_ECDHE_RSA_WITH_RC4_128_SHA (secp256r1) - C
|       TLS_RSA_WITH_RC4_128_SHA (rsa 2048) - C
|       TLS_RSA_WITH_RC4_128_MD5 (rsa 2048) - C
|     compressors:
|       NULL
|     cipher preference: server
|     warnings:
|       64-bit block cipher 3DES vulnerable to SWEET32 attack
|       Broken cipher RC4 is deprecated by RFC 7465
|       Ciphersuite uses MD5 for message integrity
|_  least strength: C
```

From this juicy data, Cipherhound grabs only:

* Hostname;
* Ports' state (open/filtered/close);
* Protocols used (SSLv3/TLSv1.0-1.1-1.2);
* Ciphersuites used;

*The actual version does not support TLSv1.3.*

### ssl-cert

With this script, written by David Fifield, we can retrieve the "usual" certificate information:

```bash
443/tcp open  https
| ssl-cert: Subject: commonName=www.paypal.com/organizationName=PayPal, Inc.\
/stateOrProvinceName=California/countryName=US/1.3.6.1.4.1.311.60.2.1.2=Delaware\
/postalCode=95131-2021/localityName=San Jose/serialNumber=3014267\
/streetAddress=2211 N 1st St/1.3.6.1.4.1.311.60.2.1.3=US\
/organizationalUnitName=PayPal Production/businessCategory=Private Organization
| Issuer: commonName=VeriSign Class 3 Extended Validation SSL CA\
/organizationName=VeriSign, Inc./countryName=US\
/organizationalUnitName=Terms of use at https://www.verisign.com/rpa (c)06
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2011-03-23 00:00:00
| Not valid after:  2013-04-01 23:59:59
| MD5:   bf47 ceca d861 efa7 7d14 88ad 4a73 cb5b
| SHA-1: d846 5221 467a 0d15 3df0 9f2e af6d 4390 0213 9a68
| -----BEGIN CERTIFICATE-----
| MIIGSzCCBTOgAwIBAgIQLjOHT2/i1B7T//819qTJGDANBgkqhkiG9w0BAQUFADCB
...
| 9YDR12XLZeQjO1uiunCsJkDIf9/5Mqpu57pw8v1QNA==
|_-----END CERTIFICATE-----
```

Cipherhound is interested only on:

* Hostname;
* Not valid before date;
* Not valid after date;

## Future enhancement

* Add validity date to the final excel file

## Meta

Wirzka – wiirzka@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/wirzka/cipherhound](https://github.com/wirzka/cipherhound/)

## Disclaimer
I am not responsible for any damages (tangible or intangible) you could make because of using cipherhound.
You should have the permissions to use it in any kind of environment.

Stay safe.
