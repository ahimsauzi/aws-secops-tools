#!/usr/bin/env python3
"""
Generate Test IAM Users for IAM Inactive User Cleanup Testing

This script creates dummy IAM users with various scenarios to test the
IAM Inactive User Cleanup automation. Designed to run in AWS CloudShell
or any environment with boto3 and AWS credentials configured.

Usage:
    python3 generate_test_users.py --create       # Create test users
    python3 generate_test_users.py --list         # List test users
    python3 generate_test_users.py --cleanup      # Delete test users
    python3 generate_test_users.py --dry-run      # Preview what would be created
"""

import boto3
import argparse
import sys
from datetime import datetime, timezone
from typing import List, Dict

# Initialize AWS IAM client
iam = boto3.client('iam')

# Test user configuration
TEST_USER_PREFIX = "test-iam-cleanup-"
TEST_TAG_KEY = "TestUser"
TEST_TAG_VALUE = "IAMCleanup"

class TestUserGenerator:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.created_users = []
        self.errors = []
    
    def create_test_users(self):
        """Create all test users with different scenarios"""
        print("\n🚀 Generating Test IAM Users")
        print("=" * 70)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No users will actually be created\n")
        
        # Define test user scenarios
        test_scenarios = [
            {
                'users': 5,
                'name_pattern': 'inactive-no-creds',
                'description': 'Inactive users with no credentials (should be flagged)',
                'add_access_key': False,
                'add_console_password': False,
                'add_exclusion_tag': False
            },
            {
                'users': 2,
                'name_pattern': 'inactive-with-keys',
                'description': 'Inactive users with access keys (should be flagged, keys disabled)',
                'add_access_key': True,
                'add_console_password': False,
                'add_exclusion_tag': False
            },
            {
                'users': 2,
                'name_pattern': 'protected',
                'description': 'Protected users with exclusion tag (should NOT be flagged)',
                'add_access_key': False,
                'add_console_password': False,
                'add_exclusion_tag': True
            },
            {
                'users': 1,
                'name_pattern': 'active-recent',
                'description': 'Recently created user (simulates active user)',
                'add_access_key': False,
                'add_console_password': False,
                'add_exclusion_tag': False
            }
        ]
        
        total_users = 0
        
        for scenario in test_scenarios:
            print(f"\n📋 Scenario: {scenario['description']}")
            print("-" * 70)
            
            for i in range(1, scenario['users'] + 1):
                username = f"{TEST_USER_PREFIX}{scenario['name_pattern']}-{i}"
                
                try:
                    if self.dry_run:
                        print(f"  [DRY RUN] Would create: {username}")
                        if scenario['add_access_key']:
                            print(f"            - Would add access key")
                        if scenario['add_exclusion_tag']:
                            print(f"            - Would add exclusion tag")
                    else:
                        # Create the user
                        iam.create_user(UserName=username)
                        print(f"  ✅ Created: {username}")
                        
                        # Add test user identification tag
                        iam.tag_user(
                            UserName=username,
                            Tags=[
                                {'Key': TEST_TAG_KEY, 'Value': TEST_TAG_VALUE},
                                {'Key': 'Scenario', 'Value': scenario['name_pattern']}
                            ]
                        )
                        
                        # Add access key if specified
                        if scenario['add_access_key']:
                            key_response = iam.create_access_key(UserName=username)
                            print(f"     ├─ Added access key: {key_response['AccessKey']['AccessKeyId']}")
                        
                        # Add exclusion tag if specified
                        if scenario['add_exclusion_tag']:
                            iam.tag_user(
                                UserName=username,
                                Tags=[{'Key': 'IAMCleanupExclude', 'Value': 'true'}]
                            )
                            print(f"     └─ Added exclusion tag: IAMCleanupExclude=true")
                        
                        self.created_users.append(username)
                        total_users += 1
                
                except iam.exceptions.EntityAlreadyExistsException:
                    print(f"  ⚠️  Already exists: {username}")
                except Exception as e:
                    error_msg = f"Failed to create {username}: {str(e)}"
                    print(f"  ❌ {error_msg}")
                    self.errors.append(error_msg)
        
        # Print summary
        print("\n" + "=" * 70)
        if self.dry_run:
            print(f"🔍 DRY RUN COMPLETE - Would create {total_users} test users")
        else:
            print(f"✅ SUCCESS - Created {len(self.created_users)} test users")
            if self.errors:
                print(f"⚠️  {len(self.errors)} errors occurred")
        print("=" * 70)
        
        # Print what to expect
        if not self.dry_run and self.created_users:
            print("\n📊 Expected Behavior:")
            print("-" * 70)
            print("When you deploy the CloudFormation stack and run a scan:")
            print("  • 7 users should be FLAGGED for deletion")
            print("  • 2 users should be EXCLUDED (protected)")
            print("  • 1 user may not be flagged yet (recently created)")
            print("\nNext Steps:")
            print("  1. Tag your admin user (sec-admin) for exclusion")
            print("  2. Deploy the CloudFormation stack")
            print("  3. Trigger a manual scan to test")
            print("  4. Verify flagged users with: python3 test_iam_cleanup.py --list-flagged")
    
    def list_test_users(self):
        """List all test users"""
        print("\n📋 Test IAM Users")
        print("=" * 70)
        
        try:
            # Get all users
            paginator = iam.get_paginator('list_users')
            test_users = []
            
            for page in paginator.paginate():
                for user in page['Users']:
                    username = user['UserName']
                    
                    # Check if it's a test user
                    if username.startswith(TEST_USER_PREFIX):
                        # Get tags
                        tags_response = iam.list_user_tags(UserName=username)
                        tags = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}
                        
                        # Get access keys
                        keys_response = iam.list_access_keys(UserName=username)
                        access_keys = keys_response['AccessKeyMetadata']
                        
                        test_users.append({
                            'username': username,
                            'created': user['CreateDate'],
                            'tags': tags,
                            'access_keys': len(access_keys),
                            'has_exclusion_tag': tags.get('IAMCleanupExclude') == 'true'
                        })
            
            if not test_users:
                print("No test users found.")
                print(f"\nTest users are identified by prefix: {TEST_USER_PREFIX}")
                return
            
            # Sort by creation date
            test_users.sort(key=lambda x: x['created'])
            
            print(f"\nFound {len(test_users)} test user(s):\n")
            
            for user in test_users:
                username = user['username']
                created = user['created'].strftime('%Y-%m-%d %H:%M:%S UTC')
                scenario = user['tags'].get('Scenario', 'unknown')
                
                print(f"• {username}")
                print(f"  ├─ Created: {created}")
                print(f"  ├─ Scenario: {scenario}")
                print(f"  ├─ Access Keys: {user['access_keys']}")
                
                if user['has_exclusion_tag']:
                    print(f"  └─ Protected: ✅ (IAMCleanupExclude=true)")
                else:
                    print(f"  └─ Protected: ❌")
                print()
        
        except Exception as e:
            print(f"❌ Error listing test users: {str(e)}")
    
    def cleanup_test_users(self, confirm: bool = False):
        """Delete all test users"""
        print("\n🗑️  Cleanup Test IAM Users")
        print("=" * 70)
        
        try:
            # Get all test users
            paginator = iam.get_paginator('list_users')
            test_users = []
            
            for page in paginator.paginate():
                for user in page['Users']:
                    if user['UserName'].startswith(TEST_USER_PREFIX):
                        test_users.append(user['UserName'])
            
            if not test_users:
                print("No test users found to delete.")
                return
            
            print(f"\nFound {len(test_users)} test user(s) to delete:")
            for username in test_users:
                print(f"  • {username}")
            
            if not confirm:
                print("\n⚠️  This is a DRY RUN. Use --confirm to actually delete these users.")
                return
            
            print("\n🚨 PROCEEDING WITH DELETION...\n")
            
            deleted_count = 0
            
            for username in test_users:
                try:
                    # Delete access keys first
                    keys_response = iam.list_access_keys(UserName=username)
                    for key in keys_response['AccessKeyMetadata']:
                        iam.delete_access_key(
                            UserName=username,
                            AccessKeyId=key['AccessKeyId']
                        )
                        print(f"  ├─ Deleted access key for {username}")
                    
                    # Delete user
                    iam.delete_user(UserName=username)
                    print(f"  ✅ Deleted user: {username}")
                    deleted_count += 1
                
                except Exception as e:
                    print(f"  ❌ Failed to delete {username}: {str(e)}")
            
            print("\n" + "=" * 70)
            print(f"✅ Deleted {deleted_count} of {len(test_users)} test users")
            print("=" * 70)
        
        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate test IAM users for IAM Inactive User Cleanup testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be created
  python3 generate_test_users.py --dry-run
  
  # Create test users
  python3 generate_test_users.py --create
  
  # List all test users
  python3 generate_test_users.py --list
  
  # Preview cleanup
  python3 generate_test_users.py --cleanup
  
  # Actually delete test users
  python3 generate_test_users.py --cleanup --confirm
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--create', action='store_true', help='Create test users')
    group.add_argument('--list', action='store_true', help='List test users')
    group.add_argument('--cleanup', action='store_true', help='Delete test users')
    group.add_argument('--dry-run', action='store_true', help='Preview what would be created')
    
    parser.add_argument('--confirm', action='store_true', help='Confirm deletion (for --cleanup)')
    
    args = parser.parse_args()
    
    generator = TestUserGenerator(dry_run=args.dry_run)
    
    if args.create or args.dry_run:
        generator.create_test_users()
    elif args.list:
        generator.list_test_users()
    elif args.cleanup:
        generator.cleanup_test_users(confirm=args.confirm)


if __name__ == '__main__':
    main()