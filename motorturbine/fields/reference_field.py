from .. import errors, document, updateset
from . import ObjectIdField
import bson


class ReferenceField(ObjectIdField):
    """__init__(reference_doc, *, allow_subclass=False, default=None, required=False, unique=False)

    This field allows another Document to be set as its value.
    A ReferenceField does not auto-insert other fields. Therefore make sure
    to insert them before you try to set them as a reference.

    :param BaseDocument reference_doc:
        Sets the document type that will be checked when setting the reference.
    :param bool allow_subclass: optional (*False*) –
        Controls whether or not it should be possible to set instances of a subclass of
        the specified document as a reference.
    """  # noqa
    def __init__(self, reference_doc, allow_subclass=False, **kwargs):
        super().__init__(**kwargs)
        if not issubclass(reference_doc, document.BaseDocument):
            raise errors.TypeMismatch(document.BaseDocument, reference_doc)
        self.reference_doc = reference_doc
        self.allow_subclass = allow_subclass

    def set_value(self, new_value):
        document = new_value
        if isinstance(new_value, updateset.UpdateOperator):
            document = new_value.update
        if document.id is None:
            raise errors.UnresolvableReference()
        self.validate_document(document)

        super().set_value(document.id)

    def validate_document(self, document):
        if isinstance(document, self.reference_doc):
            return

        if self.allow_subclass:
            if issubclass(document.__class__, self.reference_doc):
                return

        raise errors.TypeMismatch(self.reference_doc, document.__class__)
