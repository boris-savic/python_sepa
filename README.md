# Python SEPA

Simple python library aimed to create SEPA Credit Transfer XML documents. 

Disclaimer:
Library API is heavily inspired by wonderful but closed source FinTech package from http://www.joonis.de/en/software/fintech

## 1. Installation

    $ pip install sepa-generator


## 2. Quick Start


### 2.1 Create simple transaction

```python
from decimal import Decimal
from sepa_generator.core import Account, SEPACreditTransfer, Amount


debtor = Account(iban='SI12345678910',
                 bic='BAKOSI2X',
                 name='Our company Ltd.',)

creditor = Account(iban='SI54678645',
                   bic='LJBASI2X',
                   name='Recipient Company Ltd.')

sepa_transfer = SEPACreditTransfer(debtor=debtor)

sepa_transfer.add_transaction(creditor=creditor, 
                              amount=Amount(Decimal('100.10')),
                              purpose='Invoice Payment',
                              eref='SI992017-15',
                              ext_purpose='OTHR',
                              cref='SI0020170504058')


xml_string = sepa_transfer.render_xml()
```

## 3. Contact

**Boris Savic**

 * Twitter: [@zitko](https://twitter.com/zitko)
 * Email: boris70@gmail.com