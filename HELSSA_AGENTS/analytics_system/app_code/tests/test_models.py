"""
{APP_NAME} Model Tests
Part of HELSSA Platform

Test cases for {APP_DESCRIPTION} models
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock

from ..models import {MainModel}

User = get_user_model()


class {MainModel}ModelTest(TestCase):
    """Test cases for {MainModel} model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Set user type if using UnifiedUser
        if hasattr(self.user, 'user_type'):
            self.user.user_type = 'patient'
            self.user.save()
    
    def test_create_valid_record(self):
        """Test creating a valid {MainModel} record"""
        record = {MainModel}.objects.create(
            title='Test Record',
            description='This is a test record',
            user=self.user,
            created_by=self.user
        )
        
        self.assertEqual(record.title, 'Test Record')
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.status, 'pending')  # Default status
        self.assertTrue(record.is_active)  # Default active
        self.assertIsNotNone(record.id)  # UUID generated
        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)
    
    def test_str_representation(self):
        """Test string representation of {MainModel}"""
        record = {MainModel}.objects.create(
            title='Test Record',
            user=self.user,
            created_by=self.user
        )
        
        expected_str = f"Test Record - {self.user.username}"
        self.assertEqual(str(record), expected_str)
    
    def test_status_display_persian(self):
        """Test Persian status display method"""
        record = {MainModel}.objects.create(
            title='Test Record',
            user=self.user,
            created_by=self.user,
            status='pending'
        )
        
        self.assertEqual(record.get_status_display_persian(), 'در انتظار')
        
        record.status = 'completed'
        self.assertEqual(record.get_status_display_persian(), 'تکمیل شده')
    
    def test_title_validation(self):
        """Test title field validation"""
        # Test minimum length validation
        with self.assertRaises(ValidationError):
            record = {MainModel}(
                title='ab',  # Too short
                user=self.user,
                created_by=self.user
            )
            record.full_clean()
    
    def test_required_fields(self):
        """Test that required fields are validated"""
        # Test missing title
        with self.assertRaises(ValidationError):
            record = {MainModel}(
                user=self.user,
                created_by=self.user
            )
            record.full_clean()
        
        # Test missing user
        with self.assertRaises(IntegrityError):
            {MainModel}.objects.create(
                title='Test Record',
                created_by=self.user
            )
    
    def test_default_values(self):
        """Test model default values"""
        record = {MainModel}.objects.create(
            title='Test Record',
            user=self.user,
            created_by=self.user
        )
        
        self.assertEqual(record.status, 'pending')
        self.assertTrue(record.is_active)
        self.assertEqual(record.description, '')
    
    def test_ordering(self):
        """Test model ordering (newest first)"""
        record1 = {MainModel}.objects.create(
            title='First Record',
            user=self.user,
            created_by=self.user
        )
        
        record2 = {MainModel}.objects.create(
            title='Second Record',
            user=self.user,
            created_by=self.user
        )
        
        records = list({MainModel}.objects.all())
        self.assertEqual(records[0], record2)  # Newest first
        self.assertEqual(records[1], record1)
    
    def test_user_relationship(self):
        """Test user foreign key relationship"""
        record = {MainModel}.objects.create(
            title='Test Record',
            user=self.user,
            created_by=self.user
        )
        
        # Test accessing user from record
        self.assertEqual(record.user.username, 'testuser')
        
        # Test accessing records from user
        user_records = getattr(self.user, f'{app_name}_{main_model_lower}s').all()
        self.assertIn(record, user_records)
    
    def test_created_by_nullable(self):
        """Test that created_by can be null (SET_NULL on delete)"""
        creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass'
        )
        
        record = {MainModel}.objects.create(
            title='Test Record',
            user=self.user,
            created_by=creator
        )
        
        # Delete creator
        creator.delete()
        
        # Refresh record from database
        record.refresh_from_db()
        
        # created_by should be null now
        self.assertIsNone(record.created_by)
        # But record should still exist
        self.assertEqual(record.title, 'Test Record')
    
    def test_status_choices(self):
        """Test status field choices"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        
        for status in valid_statuses:
            record = {MainModel}.objects.create(
                title=f'Test Record {status}',
                user=self.user,
                created_by=self.user,
                status=status
            )
            self.assertEqual(record.status, status)
    
    def test_database_indexes(self):
        """Test that database indexes are created properly"""
        # This is more of an integration test
        # Create multiple records to test index performance
        for i in range(10):
            {MainModel}.objects.create(
                title=f'Test Record {i}',
                user=self.user,
                created_by=self.user,
                status='pending' if i % 2 == 0 else 'completed'
            )
        
        # Test queries that should use indexes
        pending_records = {MainModel}.objects.filter(
            user=self.user,
            status='pending'
        )
        self.assertTrue(pending_records.exists())
        
        recent_records = {MainModel}.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(recent_records.exists())


class {MainModel}ManagerTest(TestCase):
    """Test custom manager methods if any"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_active_records(self):
        """Test filtering active records"""
        # Create active record
        active_record = {MainModel}.objects.create(
            title='Active Record',
            user=self.user,
            created_by=self.user,
            is_active=True
        )
        
        # Create inactive record
        inactive_record = {MainModel}.objects.create(
            title='Inactive Record',
            user=self.user,
            created_by=self.user,
            is_active=False
        )
        
        # Test filtering
        active_records = {MainModel}.objects.filter(is_active=True)
        self.assertIn(active_record, active_records)
        self.assertNotIn(inactive_record, active_records)


@pytest.mark.django_db
class Test{MainModel}Performance:
    """Performance tests for {MainModel}"""
    
    def test_bulk_create_performance(self):
        """Test bulk creation performance"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create records in bulk
        records = []
        for i in range(100):
            records.append({MainModel}(
                title=f'Record {i}',
                user=user,
                created_by=user
            ))
        
        # Bulk create should be faster than individual creates
        import time
        start_time = time.time()
        {MainModel}.objects.bulk_create(records)
        bulk_time = time.time() - start_time
        
        # Verify records were created
        assert {MainModel}.objects.count() == 100
        
        # Cleanup
        {MainModel}.objects.all().delete()
        
        # Individual creates (for comparison)
        start_time = time.time()
        for i in range(10):  # Just 10 for comparison
            {MainModel}.objects.create(
                title=f'Individual Record {i}',
                user=user,
                created_by=user
            )
        individual_time = time.time() - start_time
        
        # Bulk should be significantly faster per record
        bulk_per_record = bulk_time / 100
        individual_per_record = individual_time / 10
        
        assert bulk_per_record < individual_per_record