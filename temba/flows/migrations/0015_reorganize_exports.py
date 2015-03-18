# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.files.storage import default_storage
from django.db import migrations
from temba.assets.models import AssetType


def migrate_results_exports(apps, schema_editor):
    ExportFlowResultsTask = apps.get_model('flows', 'ExportFlowResultsTask')

    store = AssetType.results_export.store

    num_copied = 0
    num_missing = 0
    num_failed = 0

    for task in ExportFlowResultsTask.objects.select_related('created_by').all():
        if not task.filename:
            num_missing += 1
            continue

        identifier = task.pk
        extension = os.path.splitext(task.filename)[1][1:]

        try:
            existing_file = default_storage.open(task.filename)
            new_path = store.derive_path(task.org, identifier, extension)
            default_storage.save(new_path, existing_file)
            num_copied += 1
        except Exception:
            print "Unable to open %s" % task.filename
            num_failed += 1

    print 'Copied %d flow results export files (%d tasks have no file, %d could not be opened)' % (num_copied, num_missing, num_failed)


class Migration(migrations.Migration):

    dependencies = [
        ('flows', '0014_auto_20150310_1806'),
    ]

    operations = [
        migrations.RunPython(migrate_results_exports)
    ]
