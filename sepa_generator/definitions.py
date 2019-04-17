
def construct_tag_data(tag_name, attrs=None, value=None, sorting=None):
    data = {
        '_name': tag_name,
        '_attrs': attrs or [],
        '_value': value,
    }

    if sorting:
        data['_sorting'] = sorting

    return data


def add_simple_child(data, child_friendly_name, child_tag_name, child_attrs=None, child_value=None):
    data[child_friendly_name] = construct_tag_data(child_tag_name, child_attrs, child_value)

    return data


def construct_header(ctransfer):
    header = construct_tag_data('GrpHdr')

    header['_sorting'] = ['MsgId', 'CreDtTm', 'NbOfTxs', 'CtrlSum', 'InitgPty']

    header['message_id'] = construct_tag_data('MsgId', value=ctransfer.uuid)
    header['creation_date_time'] = construct_tag_data('CreDtTm', value=ctransfer.timestamp)
    header['num_transactions'] = construct_tag_data('NbOfTxs', value=ctransfer.get_num_of_transactions())
    header['control_sum'] = construct_tag_data('CtrlSum', value=ctransfer.get_control_sum())
    header['initiating_party'] = add_simple_child(construct_tag_data('InitgPty'), 'name', 'Nm', [],
                                                  ctransfer.debtor.name)

    return header


def construct_iban(account, tag_name):
    iban_data = construct_tag_data(tag_name)
    iban_data['id'] = add_simple_child(construct_tag_data('Id'), 'iban', 'IBAN', [], account.iban)

    return iban_data


def construct_bic(account, tag_name):
    bic_data = construct_tag_data(tag_name)
    bic_data['financial_instrument_id'] = add_simple_child(construct_tag_data('FinInstnId'), 'bic', 'BIC', [],
                                                           account.bic)

    return bic_data


def construct_address_data(account, tag_name):
    addr_data = construct_tag_data(tag_name)

    addr_data['name'] = construct_tag_data('Nm', value=account.name)

    if account.has_address():
        address = construct_tag_data('PstlAdr')
        if account.country:
            address['country'] = construct_tag_data('Ctry', value=account.country)
        if account.street:
            address['addr_line_1'] = construct_tag_data('AdrLine', value=account.street)
        if account.postcode and account.city:
            address['addr_line_2'] = construct_tag_data('AdrLine', value="%s %s" % (account.postcode, account.city))

        addr_data['address'] = address

    return addr_data


def construct_transaction_data(ctransfer, transaction):
    transaction_information = construct_tag_data('CdtTrfTxInf')

    transaction_information['_sorting'] = ['PmtId', 'Amt', 'ChrgBr', 'UltmtDbtr', 'CdtrAgt', 'Cdtr', 'CdtrAcct',
                                           'UltmtCdtr', 'Purp', 'RmtInf']

    transaction_information['payment_id'] = add_simple_child(
        data=add_simple_child(data=construct_tag_data('PmtId', sorting=['InstrId', 'EndToEndId']),
                              child_friendly_name='instruction',
                              child_tag_name='InstrId',
                              child_value=transaction.uuid),
        child_friendly_name='eref',
        child_tag_name='EndToEndId',
        child_value=transaction.eref)

    transaction_information['amount'] = add_simple_child(data=construct_tag_data('Amt'),
                                                         child_friendly_name='amount',
                                                         child_tag_name='InstdAmt',
                                                         child_attrs=[('Ccy', ctransfer.currency)],
                                                         child_value=transaction.get_amount())

    transaction_information['charge_bearer'] = construct_tag_data('ChrgBr', value='SLEV')

    if ctransfer.debtor.use_ultimate:
        transaction_information['ultimate_debtor'] = add_simple_child(data=construct_tag_data('UltmtDbtr'),
                                                                      child_friendly_name='name',
                                                                      child_tag_name='Nm',
                                                                      child_value=ctransfer.debtor.name)

    transaction_information['creditor_agent'] = construct_bic(transaction.creditor, 'CdtrAgt')
    transaction_information['creditor_data'] = construct_address_data(transaction.creditor, 'Cdtr')
    transaction_information['creditor_account'] = construct_iban(transaction.creditor, 'CdtrAcct')

    if transaction.creditor.use_ultimate:
        transaction_information['ultimate_creditor'] = add_simple_child(data=construct_tag_data('UltmtCdtr'),
                                                                        child_friendly_name='name',
                                                                        child_tag_name='Nm',
                                                                        child_value=transaction.creditor.name)

    transaction_information['purpose'] = add_simple_child(data=construct_tag_data('Purp'),
                                                          child_friendly_name='code',
                                                          child_tag_name='Cd',
                                                          child_value=transaction.ext_purpose)

    if not transaction.use_structured:
        transaction_information['remote_inf'] = add_simple_child(data=construct_tag_data('RmtInf'),
                                                                 child_friendly_name='unstructured',
                                                                 child_tag_name='Ustrd',
                                                                 child_value=transaction.purpose)
    else:
        rmt_inf = construct_tag_data('RmtInf')
        rmt_inf_strd = add_simple_child(data=construct_tag_data('Strd'),
                                        child_friendly_name='additional_info',
                                        child_tag_name='AddtlRmtInf',
                                        child_value=transaction.purpose)
        rmt_tp = construct_tag_data('Tp')
        rmt_tp['code_or_property'] = add_simple_child(data=construct_tag_data('CdOrPrtry'),
                                                      child_friendly_name='code',
                                                      child_tag_name='Cd',
                                                      child_value='SCOR')

        rmt_creditor_ref_inf = add_simple_child(data=construct_tag_data('CdtrRefInf'),
                                                child_friendly_name='reference',
                                                child_tag_name='Ref',
                                                child_value=transaction.cref)
        rmt_creditor_ref_inf['tp'] = rmt_tp
        rmt_creditor_ref_inf['_sorting'] = ['Tp', 'Ref']

        rmt_inf_strd['creditor_ref_information'] = rmt_creditor_ref_inf
        rmt_inf_strd['_sorting'] = ['CdtrRefInf', 'AddtlRmtInf']
        rmt_inf['structured'] = rmt_inf_strd

        transaction_information['remote_inf'] = rmt_inf

    return transaction_information


def construct_payment_information(ctransfer):
    payment_inf = construct_tag_data('PmtInf')

    payment_inf['_sorting'] = ['PmtInfId', 'PmtMtd', 'BtchBookg', 'NbOfTxs', 'CtrlSum', 'PmtTpInf', 'ReqdExctnDt',
                               'Dbtr', 'DbtrAcct', 'DbtrAgt', 'ChrgBr', 'CdtTrfTxInf']
    payment_inf['payment_id'] = construct_tag_data('PmtInfId', value=ctransfer.payment_id)
    payment_inf['payment_method'] = construct_tag_data('PmtMtd', value='TRF')
    payment_inf['batch'] = construct_tag_data('BtchBookg', value=str(ctransfer.batch).lower())
    payment_inf['num_transactions'] = construct_tag_data('NbOfTxs', value=ctransfer.get_num_of_transactions())
    payment_inf['control_sum'] = construct_tag_data('CtrlSum', value=ctransfer.get_control_sum())

    payment_instruction = construct_tag_data('PmtTpInf')
    payment_instruction['_sorting'] = ['InstrPrty', 'SvcLvl']
    payment_instruction['priority'] = construct_tag_data('InstrPrty', value='NORM')
    payment_instruction['service_level'] = add_simple_child(construct_tag_data('SvcLvl'), 'code', 'Cd', [], 'SEPA')

    payment_inf['instruction'] = payment_instruction
    payment_inf['requested_execution_time'] = construct_tag_data('ReqdExctnDt', value=ctransfer.execution_time)
    payment_inf['debtor'] = construct_address_data(ctransfer.debtor, 'Dbtr')
    payment_inf['debtor_account'] = construct_iban(ctransfer.debtor, 'DbtrAcct')
    payment_inf['debtor_agent'] = construct_bic(ctransfer.debtor, 'DbtrAgt')

    payment_inf['charge_bearer'] = construct_tag_data('ChrgBr', value='SLEV')

    for i, payment in enumerate(ctransfer.transactions):
        transfer_information = construct_transaction_data(ctransfer, payment)

        payment_inf['transfer_no_%s' % i] = transfer_information

    return payment_inf


def construct_document(ctransfer):
    root = construct_tag_data('Document', [('xmlns', 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03')])

    message = construct_tag_data('CstmrCdtTrfInitn')
    message['_sorting'] = ['GrpHdr', 'PmtInf']
    message['header'] = construct_header(ctransfer)
    message['payment_information'] = construct_payment_information(ctransfer)

    root['message'] = message

    return root
