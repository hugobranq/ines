# -*- coding: utf-8 -*-

from colander import Boolean as BaseBoolean
from colander import drop as colander_drop
from colander import DateTime as BaseDateTime
from colander import MappingSchema
from colander import null
from colander import OneOf
from colander import SchemaNode as BaseSchemaNode
from colander import SequenceSchema
from colander import String
from colander import TupleSchema

from ines import FALSES
from ines import TRUES


class SchemaNode(BaseSchemaNode):
    def __init__(self, *arg, **kw):
        self.return_none_if_defined = kw.pop('return_none_if_defined', False)
        super(SchemaNode, self).__init__(*arg, **kw)

    def deserialize(self, cstruct=null):
        result = BaseSchemaNode.deserialize(self, cstruct)
        # Return None, only if request and cstruct is empty
        if (self.return_none_if_defined
                and (result is null or result is colander_drop)
                and cstruct is not null and not cstruct):
            return None
        else:
            return result

    def clone(self, **kwargs):
        cloned = BaseSchemaNode.clone(self)
        cloned.__dict__.update(kwargs)
        cloned._order = next(cloned._counter)
        return cloned


class OneOfWithDescription(OneOf):
    def __init__(self, choices):
        if isinstance(choices, dict):
            choices = choices.items()
        self.choices_with_descripton = choices
        super(OneOfWithDescription, self).__init__(dict(choices).keys())


class DateTime(BaseDateTime):
    def __init__(self, default_tzinfo=None):
        super(DateTime, self).__init__(default_tzinfo=default_tzinfo)


class Boolean(BaseBoolean):
    def __init__(self, **kwargs):
        if 'true_choices' not in kwargs:
            kwargs['true_choices'] = TRUES
        if 'false_choices' not in kwargs:
            kwargs['false_choices'] = FALSES
        super(Boolean, self).__init__(**kwargs)

    def deserialize(self, node, cstruct):
        if cstruct == '':
            return null
        else:
            return super(Boolean, self).deserialize(node, cstruct)


class InputField(SequenceSchema):
    field = SchemaNode(String(), missing=None)


class InputExcludeField(SequenceSchema):
    exclude_field = SchemaNode(String(), missing=None)


class InputFields(SequenceSchema):
    fields = SchemaNode(String(), missing=None)


class InputExcludeFields(SequenceSchema):
    exclude_field = SchemaNode(String(), missing=None)


def split_values(appstruct):
    result = set()
    for value in appstruct:
        result.update(value.split(u','))
    return list(result)


class SearchFields(MappingSchema):
    field = InputField()
    exclude_field = InputExcludeField()
    fields = InputFields(preparer=split_values)
    exclude_fields = InputExcludeFields(preparer=split_values)


def node_is_iterable(node):
    return isinstance(node, (TupleSchema, MappingSchema, SequenceSchema))
