import pytz

from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from lxml import etree

from sepa_generator.builder import build_xml
from sepa_generator.definitions import construct_document


class Amount:
    def __init__(self, amount):
        self._orig_amount = amount
        self.amount = self._convert_to_internal()

    def __add__(self, other):
        return Amount(self.amount + other.amount)

    def _convert_to_internal(self):
        if type(self._orig_amount) == Decimal:
            return self._orig_amount
        elif type(self._orig_amount) == float or type(self._orig_amount) == int:
            return Decimal(self._orig_amount)
        else:
            raise ValueError('Amount should be of type Decimal, Float or Integer')


class Account:
    def __init__(self, iban, bic, name, street=None, city=None, postcode=None, country=None, use_ultimate=True):
        self.iban = iban
        self.bic = bic
        self.name = name
        self.street = street
        self.city = city
        self.postcode = postcode
        self.country = country
        self.use_ultimate = use_ultimate

    def has_address(self):
        if self.street:
            return True
        if self.city:
            return True
        if self.postcode:
            return True
        if self.country:
            return True

        return False


class SEPATransaction:
    def __init__(self, creditor, amount, purpose, eref, ext_purpose, use_structured=True, cref=None):
        self.uuid = uuid4().hex.upper()
        self.creditor = creditor
        self.amount = amount
        self.purpose = purpose
        self.eref = eref
        self.ext_purpose = ext_purpose
        self.use_structured = use_structured
        self.cref = cref or self.eref

    def get_amount(self):
        return str(self.amount.amount)


class SEPACreditTransfer:
    def __init__(self, debtor, currency='EUR', batch=False):
        self.uuid = uuid4().hex.upper()
        self.payment_id = uuid4().hex.upper()
        self.debtor = debtor  # Account
        self.currency = currency
        self.batch = batch

        self._ctrl_sum = Amount(Decimal('0.00'))
        self.timestamp = datetime.now(tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.execution_time = datetime.now(tz=pytz.UTC).strftime("%Y-%m-%d")
        self.transactions = []

    def add_transaction(self, creditor, amount, purpose, eref, ext_purpose='OTHR', use_structured=True, cref=None):
        t = SEPATransaction(creditor, amount, purpose, eref, ext_purpose, use_structured, cref)
        self._ctrl_sum += t.amount

        self.transactions.append(t)

        return t

    def render_xml(self):
        return etree.tostring(build_xml(construct_document(self)), pretty_print=True, xml_declaration=True, encoding="utf-8")

    def get_num_of_transactions(self):
        return str(len(self.transactions))

    def get_control_sum(self):
        return str(self._ctrl_sum.amount)
