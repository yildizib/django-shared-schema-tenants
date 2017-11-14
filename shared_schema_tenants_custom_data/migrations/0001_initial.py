# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 05:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import model_utils.fields
import shared_schema_tenants.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared_schema_tenants', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantSpecificFieldChunk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_integer', models.IntegerField(blank=True, null=True)),
                ('value_char', models.CharField(blank=True, max_length=255, null=True)),
                ('value_text', models.TextField(blank=True, null=True)),
                ('value_float', models.FloatField(blank=True, null=True)),
                ('value_datetime', models.DateTimeField(blank=True, null=True)),
                ('value_date', models.DateField(blank=True, null=True)),
                ('row_id', models.PositiveIntegerField()),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('original_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TenantSpecificFieldDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('data_type', model_utils.fields.StatusField(choices=[('char', 'char'), ('text', 'text'), ('integer', 'integer'), ('float', 'float'), ('datetime', 'datetime'), ('date', 'date')], default='char', max_length=100, no_check_for_status=True)),
                ('is_required', models.BooleanField(default=False)),
                ('default_value', models.TextField()),
                ('table_id', models.PositiveIntegerField(blank=True, null=True)),
                ('table_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('tenant', models.ForeignKey(default=shared_schema_tenants.mixins.get_default_tenant, on_delete=django.db.models.deletion.CASCADE, to='shared_schema_tenants.Tenant')),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('original_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TenantSpecificFieldsValidator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_path', models.CharField(max_length=255)),
                ('tenants', models.ManyToManyField(related_name='validators_available', to='shared_schema_tenants.Tenant')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'original_manager',
                'default_manager_name': 'original_manager',
            },
            managers=[
                ('original_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TenantSpecificTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(default=shared_schema_tenants.mixins.get_default_tenant, on_delete=django.db.models.deletion.CASCADE, to='shared_schema_tenants.Tenant')),
            ],
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('original_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TenantSpecificTableRow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rows', to='shared_schema_tenants_custom_data.TenantSpecificTable')),
                ('tenant', models.ForeignKey(default=shared_schema_tenants.mixins.get_default_tenant, on_delete=django.db.models.deletion.CASCADE, to='shared_schema_tenants.Tenant')),
            ],
            options={
                'base_manager_name': 'original_manager',
                'default_manager_name': 'original_manager',
            },
            managers=[
                ('original_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='tenantspecificfielddefinition',
            name='validators',
            field=models.ManyToManyField(to='shared_schema_tenants_custom_data.TenantSpecificFieldsValidator', blank=True),
        ),
        migrations.AddField(
            model_name='tenantspecificfieldchunk',
            name='definition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='shared_schema_tenants_custom_data.TenantSpecificFieldDefinition'),
        ),
        migrations.AddField(
            model_name='tenantspecificfieldchunk',
            name='row_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='tenantspecificfieldchunk',
            name='tenant',
            field=models.ForeignKey(default=shared_schema_tenants.mixins.get_default_tenant, on_delete=django.db.models.deletion.CASCADE, to='shared_schema_tenants.Tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='tenantspecifictable',
            unique_together=set([('tenant', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='tenantspecificfielddefinition',
            unique_together=set([('tenant', 'table_id', 'table_content_type', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='tenantspecificfieldchunk',
            unique_together=set([('definition', 'row_id', 'row_content_type')]),
        ),
    ]
