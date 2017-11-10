from django.db import models
from django.db.models.manager import BaseManager
from django.utils.version import get_complete_version

from django.contrib.contenttypes.models import ContentType

from shared_schema_tenants_custom_data.querysets import TenantSpecificFieldsQueryset
from shared_schema_tenants.managers import SingleTenantModelManager


class TenantSpecificFieldsModelBaseManager(BaseManager):
    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        import inspect
        from django.utils import six

        def create_method(name, method):
            def manager_method(self, *args, **kwargs):
                table_id = self.table_id
                kwargs['table_id'] = table_id
                return getattr(self.get_queryset(table_id=table_id), name)(*args, **kwargs)
            manager_method.__name__ = method.__name__
            manager_method.__doc__ = method.__doc__
            return manager_method

        new_methods = {}
        # Refs http://bugs.python.org/issue1785.
        predicate = inspect.isfunction if six.PY3 else inspect.ismethod
        for name, method in inspect.getmembers(queryset_class, predicate=predicate):
            # Only copy missing methods.
            if hasattr(cls, name):
                continue
            # Only copy public methods or methods with the attribute `queryset_only=False`.
            queryset_only = getattr(method, 'queryset_only', None)
            if queryset_only or (queryset_only is None and name.startswith('_')):
                continue
            # Copy the method onto the manager.
            new_methods[name] = create_method(name, method)
        return new_methods


class TenantSpecificFieldsModelManager(
        TenantSpecificFieldsModelBaseManager.from_queryset(TenantSpecificFieldsQueryset)):
    data_type_fields = {
        'integer': models.IntegerField(),
        'char': models.CharField(max_length=255),
        'text': models.TextField(),
        'float': models.FloatField(),
        'datetime': models.DateTimeField(),
        'date': models.DateField(),
    }

    def get_queryset(self, *args, **kwargs):
        from shared_schema_tenants_custom_data.models import TenantSpecificTableRow
        if not hasattr(self, 'table_id'):
            self.table_id = kwargs.get('table_id', -1)
        else:
            kwargs['table_id'] = self.table_id
        custom_fields_annotations = self._get_custom_fields_annotations()

        queryset = super(TenantSpecificFieldsModelManager, self).get_queryset(*args, **kwargs)

        if len(custom_fields_annotations.keys()) > 0:
            if self.model == TenantSpecificTableRow:
                return (
                    queryset
                    .annotate(**custom_fields_annotations)
                    .filter(table_id=self.table_id)
                )
            return queryset.annotate(**custom_fields_annotations)

        if self.model == TenantSpecificTableRow:
            return queryset.filter(table_id=self.table_id)
        return queryset

    def _get_custom_fields_annotations(self):
        from shared_schema_tenants_custom_data.models import (
            TenantSpecificFieldDefinition, TenantSpecificFieldChunk, TenantSpecificTable, TenantSpecificTableRow)

        if self.model == TenantSpecificTableRow:
            definitions = TenantSpecificFieldDefinition.objects.filter(
                table_content_type=ContentType.objects.get_for_model(TenantSpecificTable),
                table_id=self.table_id)
        else:
            definitions = TenantSpecificFieldDefinition.objects.filter(
                table_content_type=ContentType.objects.get_for_model(self.model))
        definitions_by_name = {d.name: d for d in definitions}

        custom_fields_annotations = {}

        for key in definitions_by_name.keys():
            if get_complete_version()[1] >= 11:
                from django.db.models import Subquery, OuterRef
                definitions_values = (
                    TenantSpecificFieldChunk.objects
                    .filter(definition_id=definitions_by_name[key].id, row_id=OuterRef('pk'))
                    .values(value=models.F('value_' + definitions_by_name[key].data_type))
                )

                custom_fields_annotations[key] = Subquery(
                    queryset=definitions_values,
                    output_field=self.data_type_fields[definitions_by_name[key].data_type]
                )
            else:
                from django.db.models.expressions import RawSQL
                model_content_type = ContentType.objects.get_for_model(self.model)
                model_table_name = (model_content_type.app_label + '_' + model_content_type.model)
                custom_fields_annotations[key] = RawSQL(
                    """
                        select c.value_""" + definitions_by_name[key].data_type + """
                        from shared_schema_tenants_custom_data_tenantspecificfieldchunk c
                        where definition_id = %s and
                            c.row_id = """ + '"' + model_table_name + '"."' + self.model._meta.pk.name + '"',
                    [definitions_by_name[key].id],
                    output_field=self.data_type_fields[definitions_by_name[key].data_type])

        return custom_fields_annotations


class ManagerPassesTableIdToQueryset(models.Manager):

    def get_queryset(self, table_id=-1):
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints, table_id=self.table_id)


class TenantSpecificTableRowManager(TenantSpecificFieldsModelManager, SingleTenantModelManager,
                                    ManagerPassesTableIdToQueryset):
    pass
