"""
Test suite for HttpPro core functionality.
"""

import unittest
import tempfile
import os
from core.database import IgnoreHostsDB

class TestIgnoreHostsDB(unittest.TestCase):
    """Test cases for IgnoreHostsDB class."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db = IgnoreHostsDB(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_add_domain(self):
        """Test adding a domain to the database."""
        result = self.db.add_domain("example.com", "test")
        self.assertTrue(result)
        
        # Adding the same domain should return False (already exists)
        result = self.db.add_domain("example.com", "test")
        self.assertFalse(result)
    
    def test_get_active_domains(self):
        """Test retrieving active domains."""
        self.db.add_domain("example.com", "test")
        self.db.add_domain("test.com", "test")
        
        domains = self.db.get_active_domains()
        self.assertIn("example.com", domains)
        self.assertIn("test.com", domains)
        self.assertEqual(len(domains), 2)
    
    def test_remove_domain(self):
        """Test removing (deactivating) a domain."""
        self.db.add_domain("example.com", "test")
        
        result = self.db.remove_domain("example.com")
        self.assertTrue(result)
        
        # Domain should no longer be in active list
        domains = self.db.get_active_domains()
        self.assertNotIn("example.com", domains)
    
    def test_get_stats(self):
        """Test getting database statistics."""
        self.db.add_domain("example.com", "test")
        self.db.add_domain("test.com", "manual")
        
        stats = self.db.get_stats()
        self.assertEqual(stats['total_domains'], 2)
        self.assertEqual(stats['active_domains'], 2)
        self.assertEqual(stats['origins']['test'], 1)
        self.assertEqual(stats['origins']['manual'], 1)

if __name__ == '__main__':
    unittest.main()
