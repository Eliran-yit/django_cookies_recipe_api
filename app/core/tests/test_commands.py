from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            # the call command name of the get item command above
            call_command('wait_for_db')
            # make sure that the command call just once
            self.assertEqual(gi.call_count, 1)
    
    
    
    @patch('time.sleep', return_value=True)
    # wait before try again connect to the db in case of operational error
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # if reached 6 Operational errors return True
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
            
            