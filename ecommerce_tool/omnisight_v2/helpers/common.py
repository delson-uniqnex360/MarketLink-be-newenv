import requests
from mongoengine import DoesNotExist, Document, MultipleObjectsReturned


from mongoengine import DoesNotExist, MultipleObjectsReturned, ValidationError, Document


def get_or_create(
    model: type[Document], defaults: dict = None, **lookup
) -> tuple[Document, bool]:
    """
    Get a document matching the lookup fields, create it if it doesn't exist,
    or update it with defaults if it already exists.

    Returns:
        tuple: (document, created)
            document: the retrieved or newly created document
            created: True if a new document was created, False if retrieved/updated
    """
    defaults = defaults or {}
    try:
        # Try to get the document
        doc = model.objects.get(**lookup)
        created = False

        # Update the document with fields from defaults that aren't part of lookup
        update_fields = {k: v for k, v in defaults.items() if k not in lookup}
        if update_fields:
            for field, value in update_fields.items():
                setattr(doc, field, value)
            try:
                doc.save()
            except ValidationError as e:
                raise ValueError(f"Failed to update document: {e}")

        return doc, created

    except DoesNotExist:
        # Merge lookup and defaults for creation
        data = {**lookup, **defaults}
        doc = model(**data)
        try:
            doc.save()
        except ValidationError as e:
            raise ValueError(f"Failed to create document: {e}")
        return doc, True

    except MultipleObjectsReturned:
        # Pick the first document, then update it
        doc = model.objects.filter(**lookup).first()
        created = False
        update_fields = {k: v for k, v in defaults.items() if k not in lookup}
        if update_fields:
            for field, value in update_fields.items():
                setattr(doc, field, value)
            try:
                doc.save()
            except ValidationError as e:
                raise ValueError(f"Failed to update document: {e}")

        return doc, created


def get_or_create_embedded(parent_doc, field_name, embedded_cls, lookup, defaults=None):
    defaults = defaults or {}
    embedded = getattr(parent_doc, field_name)

    # if single embedded document
    if embedded is not None:
        if all(getattr(embedded, k, None) == v for k, v in lookup.items()):
            return embedded, False
    # create new
    data = {**lookup, **defaults}
    embedded = embedded_cls(**data)
    setattr(parent_doc, field_name, embedded)
    parent_doc.save()
    return embedded, True


def get_platform_access_token(
    platform_url: str, client_id: str, client_secret: str
) -> dict:
    """
    this function generate token every and return access token

    #TODO: handle saving the access token in redis and make use of refresh token

    """

    url = f"{platform_url}/auth/token/"
    payload = {"client_id": client_id, "client_secret": client_secret}
    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json()
