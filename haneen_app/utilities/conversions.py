from typing import Iterable, List, Set


def to_dict(
    obj: object,
    ignore_none_value: bool = True,
    ignore_blank_value: bool = False,
    ignored_fields: List[str] = None,
    picked_fields: List[str] = None,
    visited: Set[str] = None,
):
    if not visited:
        visited = set()

    obj_str = str(obj)
    if obj_str in visited:
        return obj

    visited.add(obj_str)

    kwargs = dict(
        ignore_none_value=ignore_none_value,
        ignore_blank_value=ignore_blank_value,
        ignored_fields=ignored_fields,
        picked_fields=picked_fields,
        visited=visited,
    )

    if obj is None:
        return {}
    elif isinstance(obj, Iterable):
        return _handle_iterable_to_dict(obj, **kwargs)
    elif not hasattr(obj, "__dict__"):
        return obj
    else:
        return _handle_dictionary_obj_to_dict(obj, **kwargs)


def _handle_iterable_to_dict(obj: object, **kwargs):
    if isinstance(obj, dict):
        return {k1: to_dict(v1, **kwargs) for k1, v1 in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(v1, **kwargs) for v1 in obj]
    elif isinstance(obj, set):
        return {to_dict(v1, **kwargs) for v1 in obj}
    elif isinstance(obj, tuple) or hasattr(obj, "_fields"):
        return tuple([to_dict(v1, **kwargs) for v1 in obj])
    else:
        return obj


def _handle_dictionary_obj_to_dict(
    obj: object,
    ignore_none_value: bool = True,
    ignore_blank_value: bool = False,
    ignored_fields: List[str] = None,
    picked_fields: List[str] = None,
    visited: Set[str] = None,
):
    _dict = {}

    for k, v in vars(obj).items():
        if k.startswith("_"):  # ignore private fields
            continue

        if ignore_none_value and v is None:
            continue

        if ignore_blank_value and v == "":
            continue

        if ignored_fields and k in ignored_fields:
            continue

        if picked_fields and k not in picked_fields:
            continue

        _dict[k] = to_dict(v, ignore_none_value, ignore_blank_value, ignored_fields, picked_fields, visited)

    return _dict