from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
import pytest
from unittest import mock


@pytest.fixture(autouse=True) # Automatically use in tests.
def mute_signals(request):
    # Skip applying, if marked with `enabled_signals`
    if 'enable_signals' in request.keywords:
        return

    signals = [
        pre_save,
        post_save,
        pre_delete,
        post_delete,
        m2m_changed
    ]
    restore = {}
    for signal in signals:
        # Temporally remove the signal's receivers (a.k.a attached functions)
        restore[signal] = signal.receivers
        signal.receivers = []

    def restore_signals():
        # When the test tears down, restore the signals.
        for signal, receivers in restore.items():
            signal.receivers = receivers

    # Called after a test has finished.
    request.addfinalizer(restore_signals)