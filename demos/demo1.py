from decimal import Decimal

from sepa.core import Account, SEPACreditTransfer, Amount

debtor = Account(iban='SI123456789',
                 bic='BAKOSI2X',
                 name='Demo d.o.o.',
                 country='SI',
                 city='Ljubljana',
                 street='Pot za Brdom 100',
                 postcode='1000',
                 use_ultimate=True)

creditor = Account(iban='SI54678645',
                   bic='LJBASI2X',
                   name='Demo 2 d.o.o.')

sepa_transfer = SEPACreditTransfer(debtor=debtor)

sepa_transfer.add_transaction(creditor, Amount(Decimal('100.10')), 'Purpose of the transfer', 'SI99', 'OTHR', cref='SI99123546787')


print(sepa_transfer.render_xml())