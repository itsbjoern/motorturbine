from .. import errors, document, updateset, utils
from . import base_field
import bson


class DocumentField(base_field.BaseField):
    """__init__(embed_doc, *, default=None, required=False, unique=False)

    This field allows another Document to be set as its value. Any document inserted
    as an embedded field will be treated like an object inside of its parent.
    It enables to create more complex document trees than by just using
    :class:`~motorturbine.fields.MapField`.

    Example usage::

        class Identifier(BaseDocument):
            serial = fields.StringField()
            stamp = fields.DateTimeField()
            location = fields.StringField()

        class Part(BaseDocument):
            name = fields.StringField()
            ident = fields.DocumentField(Identifier)

        now = datetime.utcnow()
        ident = Identifier(serial='9X1-33D-52A', stamp=now, location='US')
        part = Part(name='Xerxes', ident=ident)

        await part.save()

    In this example an Identifier is attached to each Part that is produced. It
    wouldn't have been easily possibly to create this structure by using a
    :class:`~motorturbine.fields.MapField` because the Identifier is built from
    more than one data types.

    :param BaseDocument embed_doc:
        Sets the document type that will be checked when embedding an instance.
    """  # noqa
    def __init__(self, embed_doc, allow_subclass=False, **kwargs):
        super().__init__(**kwargs)
        if not issubclass(embed_doc, document.BaseDocument):
            raise errors.TypeMismatch(document.BaseDocument, type(embed_doc))
        self.embed_doc = embed_doc

    def clone(self, *args, **kwargs):
        new_field = super().clone(self.embed_doc, **kwargs)
        return new_field

    def set_value(self, new_value):
        val = new_value
        if isinstance(new_value, updateset.UpdateOperator):
            val = new_value.update

        document = val
        if isinstance(val, dict):
            document = self.embed_doc(**val)

        if document._get_field('id') is not None:
            document._get_fields().__delitem__('id')

        def update_sync_wrapper(name):
            self.document.update_sync(self.name + '.' + name)

        object.__setattr__(document, 'update_sync', update_sync_wrapper)

        super().set_value(document)

    def __getattr__(self, attr):
        sub_path, cutoff = utils.get_sub_path(attr, 1)

        if sub_path == '':
            return self.__getattribute__(attr)

        return self.value[sub_path]

    def validate_field(self, document):
        if isinstance(document, self.embed_doc):
            return

        raise errors.TypeMismatch(self.embed_doc, document.__class__)

    def get_value(self):
        if self.value is None:
            return None
        return self.value.to_json()

    def get_updates(self, path):
        if path == '' or self.value is None:
            for update in self.updates:
                update['op'].update = update['op'].update.to_json()
            return self.updates

        sub_path, cutoff = utils.get_sub_path(path, 1)
        return self.value._get_field(cutoff[0]).get_updates(sub_path)
