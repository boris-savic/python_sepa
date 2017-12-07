from lxml import etree
from six import iteritems


def build_xml(data):
    tag = etree.Element(data['_name'])

    for attr, val in data['_attrs']:
        tag.attrib[attr] = val

    for child, child_data in iteritems(data):
        if not child.startswith('_'):
            child_tag = build_xml(child_data)
            tag.append(child_tag)

    if data['_value'] is not None:
        tag.text = data['_value']

    # Sort the child elements
    if '_sorting' in data:
        tag[:] = sorted(tag, key=lambda element: data['_sorting'].index(element.tag))

    return tag
