#!/usr/bin/env python3
"""
Test and Validation Script for IAM Inactive User Cleanup
This script helps validate the deployment and test the automation
"""

import boto3
import argparse
import json
from datetime import datetime, timezone
from typing import Dict, List

# Initialize AWS clients
iam = boto3.client('iam')
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
cloudformation = boto3.client('cloudformation')

class IAMCleanupValidator:
    def __init__(self, stack_name: str):
        self.stack_name = stack_name
        self.resources = self._get_stack_resources()
    
    def _get_stack_resources(self) -> Dict[str, str]:
        """Get resource names from CloudFormation stack"""
        try:
            response = cloudformation.describe_stacks(StackName=self.stack_name)
            outputs = response['Stacks'][0]['Outputs']
            
            resources = {}
            for output in outputs:
                resources[output['OutputKey']] = output['OutputValue']
            
            # Get additional resources
            stack_resources = cloudformation.list_stack_resources(StackName=self.stack_name)
            for resource in stack_resources['StackResourceSummaries']:
                if resource['ResourceType'] == 'AWS::DynamoDB::Table':
                    resources['TableName'] = resource['PhysicalResourceId']
            
            return resources
        except Exception as e:
            print(f"❌ Error getting stack resources: {str(e)}")
            return {}
    
    def validate_deployment(self) -> bool:
        """Validate that all resources are deployed correctly"""
        print("\n🔍 Validating CloudFormation Stack Deployment...")
        print("=" * 60)
        
        checks = {
            'Stack Exists': self._check_stack_exists(),
            'DynamoDB Table': self._check_dynamodb_table(),
            'Scanner Lambda': self._check_scanner_lambda(),
            'Cleanup Lambda': self._check_cleanup_lambda(),
            'SNS Topic': self._check_sns_topic(),
            'DynamoDB Streams': self._check_dynamodb_streams(),
            'CloudWatch Event Rule': self._check_event_rule(),
        }
        
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {check_name}")
        
        all_passed = all(checks.values())
        print("=" * 60)
        print(f"\n{'✅ All checks passed!' if all_passed else '❌ Some checks failed.'}\n")
        
        return all_passed
    
    def _check_stack_exists(self) -> bool:
        """Check if CloudFormation stack exists and is in good state"""
        try:
            response = cloudformation.describe_stacks(StackName=self.stack_name)
            status = response['Stacks'][0]['StackStatus']
            return status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']
        except:
            return False
    
    def _check_dynamodb_table(self) -> bool:
        """Check if DynamoDB table exists with correct configuration"""
        try:
            table_name = self.resources.get('TableName')
            if not table_name:
                return False
            
            table = dynamodb.Table(table_name)
            table.load()
            
            # Check TTL is enabled
            ttl_response = boto3.client('dynamodb').describe_time_to_live(
                TableName=table_name
            )
            ttl_enabled = ttl_response['TimeToLiveDescription']['TimeToLiveStatus'] == 'ENABLED'
            
            # Check Streams are enabled
            streams_enabled = table.stream_specification is not None
            
            return ttl_enabled and streams_enabled
        except Exception as e:
            print(f"    Error: {str(e)}")
            return False
    
    def _check_scanner_lambda(self) -> bool:
        """Check if Scanner Lambda exists and is configured correctly"""
        try:
            scanner_arn = self.resources.get('ScannerLambdaArn')
            if not scanner_arn:
                return False
            
            response = lambda_client.get_function(FunctionName=scanner_arn)
            return response['Configuration']['State'] == 'Active'
        except:
            return False
    
    def _check_cleanup_lambda(self) -> bool:
        """Check if Cleanup Lambda exists"""
        try:
            cleanup_arn = self.resources.get('CleanupLambdaArn')
            if not cleanup_arn:
                return False
            
            response = lambda_client.get_function(FunctionName=cleanup_arn)
            return response['Configuration']['State'] == 'Active'
        except:
            return False
    
    def _check_sns_topic(self) -> bool:
        """Check if SNS topic exists"""
        try:
            topic_arn = self.resources.get('SNSTopicArn')
            if not topic_arn:
                return False
            
            sns = boto3.client('sns')
            sns.get_topic_attributes(TopicArn=topic_arn)
            return True
        except:
            return False
    
    def _check_dynamodb_streams(self) -> bool:
        """Check if DynamoDB Streams is configured correctly"""
        try:
            table_name = self.resources.get('TableName')
            if not table_name:
                return False
            
            table = dynamodb.Table(table_name)
            table.load()
            
            if not table.stream_specification:
                return False
            
            # Check if Lambda event source mapping exists
            cleanup_arn = self.resources.get('CleanupLambdaArn')
            response = lambda_client.list_event_source_mappings(
                FunctionName=cleanup_arn
            )
            
            return len(response['EventSourceMappings']) > 0
        except:
            return False
    
    def _check_event_rule(self) -> bool:
        """Check if CloudWatch Event Rule exists"""
        try:
            events = boto3.client('events')
            rules = events.list_rules(NamePrefix=f"{self.stack_name}-DailyScan")
            return len(rules['Rules']) > 0
        except:
            return False
    
    def list_flagged_users(self):
        """List all currently flagged users in DynamoDB"""
        print("\n📋 Currently Flagged Users:")
        print("=" * 60)
        
        try:
            table_name = self.resources.get('TableName')
            if not table_name:
                print("❌ Could not find DynamoDB table")
                return
            
            table = dynamodb.Table(table_name)
            response = table.scan()
            
            if not response['Items']:
                print("✅ No users currently flagged")
                return
            
            for item in response['Items']:
                username = item['username']
                flagged_date = item.get('flagged_date', 'Unknown')
                ttl = item.get('ttl', 0)
                deletion_date = datetime.fromtimestamp(ttl, tz=timezone.utc) if ttl else None
                
                print(f"\nUser: {username}")
                print(f"  Flagged: {flagged_date}")
                print(f"  Deletion: {deletion_date.strftime('%Y-%m-%d %H:%M:%S UTC') if deletion_date else 'Unknown'}")
                print(f"  Last Activity: {item.get('last_activity', 'Unknown')}")
                print(f"  Keys Disabled: {item.get('access_keys_disabled', False)}")
        
        except Exception as e:
            print(f"❌ Error listing flagged users: {str(e)}")
    
    def trigger_manual_scan(self):
        """Manually trigger the scanner Lambda"""
        print("\n🚀 Triggering Manual Scan...")
        print("=" * 60)
        
        try:
            scanner_arn = self.resources.get('ScannerLambdaArn')
            if not scanner_arn:
                print("❌ Could not find Scanner Lambda")
                return
            
            response = lambda_client.invoke(
                FunctionName=scanner_arn,
                InvocationType='RequestResponse'
            )
            
            payload = json.loads(response['Payload'].read())
            
            if response['StatusCode'] == 200:
                print("✅ Scan completed successfully!")
                print("\nResults:")
                if 'body' in payload:
                    result = json.loads(payload['body'])
                    print(f"  Total Inactive Users: {result.get('total_inactive_users', 0)}")
                    print(f"  Newly Flagged: {result.get('newly_flagged_users', 0)}")
                    if result.get('users'):
                        print(f"  Users: {', '.join(result['users'])}")
            else:
                print(f"❌ Scan failed with status code: {response['StatusCode']}")
                
        except Exception as e:
            print(f"❌ Error triggering scan: {str(e)}")
    
    def check_iam_users_status(self):
        """Check the activity status of all IAM users"""
        print("\n👥 IAM Users Activity Status:")
        print("=" * 60)
        
        try:
            paginator = iam.get_paginator('list_users')
            total_users = 0
            inactive_users = []
            
            for page in paginator.paginate():
                for user in page['Users']:
                    total_users += 1
                    username = user['UserName']
                    
                    # Get password last used
                    password_last_used = user.get('PasswordLastUsed')
                    
                    # Get access key last used
                    access_keys = iam.list_access_keys(UserName=username)
                    key_last_used = None
                    
                    for key in access_keys['AccessKeyMetadata']:
                        try:
                            key_data = iam.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
                            if 'LastUsedDate' in key_data['AccessKeyLastUsed']:
                                last_used = key_data['AccessKeyLastUsed']['LastUsedDate']
                                if not key_last_used or last_used > key_last_used:
                                    key_last_used = last_used
                        except:
                            pass
                    
                    # Determine last activity
                    last_activity = None
                    if password_last_used and key_last_used:
                        last_activity = max(password_last_used, key_last_used)
                    elif password_last_used:
                        last_activity = password_last_used
                    elif key_last_used:
                        last_activity = key_last_used
                    
                    if last_activity:
                        days_inactive = (datetime.now(timezone.utc) - last_activity).days
                    else:
                        days_inactive = 9999  # Never used
                    
                    if days_inactive >= 90:  # Using default threshold
                        inactive_users.append((username, days_inactive, last_activity))
            
            print(f"\nTotal IAM Users: {total_users}")
            print(f"Inactive Users (>90 days): {len(inactive_users)}")
            
            if inactive_users:
                print("\nInactive Users:")
                for username, days, last_activity in sorted(inactive_users, key=lambda x: x[1], reverse=True):
                    last_activity_str = last_activity.strftime('%Y-%m-%d') if last_activity else 'Never'
                    print(f"  • {username} - {days} days ({last_activity_str})")
        
        except Exception as e:
            print(f"❌ Error checking IAM users: {str(e)}")
    
    def test_notification(self):
        """Send a test notification to SNS"""
        print("\n📧 Sending Test Notification...")
        print("=" * 60)
        
        try:
            topic_arn = self.resources.get('SNSTopicArn')
            if not topic_arn:
                print("❌ Could not find SNS Topic")
                return
            
            sns = boto3.client('sns')
            sns.publish(
                TopicArn=topic_arn,
                Subject='Test Notification - IAM Cleanup Automation',
                Message=f"""This is a test notification from the IAM Inactive User Cleanup automation.

Timestamp: {datetime.now(timezone.utc).isoformat()}
Stack: {self.stack_name}

If you received this email, your notifications are configured correctly.
"""
            )
            
            print("✅ Test notification sent successfully!")
            print("📬 Check your email inbox")
            
        except Exception as e:
            print(f"❌ Error sending test notification: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Test and validate IAM Inactive User Cleanup automation'
    )
    parser.add_argument(
        '--stack-name',
        default='iam-inactive-user-cleanup',
        help='CloudFormation stack name (default: iam-inactive-user-cleanup)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate deployment'
    )
    parser.add_argument(
        '--list-flagged',
        action='store_true',
        help='List currently flagged users'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Trigger manual scan'
    )
    parser.add_argument(
        '--check-users',
        action='store_true',
        help='Check IAM users activity status'
    )
    parser.add_argument(
        '--test-notification',
        action='store_true',
        help='Send test notification'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all checks'
    )
    
    args = parser.parse_args()
    
    validator = IAMCleanupValidator(args.stack_name)
    
    if args.all:
        validator.validate_deployment()
        validator.check_iam_users_status()
        validator.list_flagged_users()
        validator.test_notification()
    else:
        if args.validate or not any([args.list_flagged, args.scan, args.check_users, args.test_notification]):
            validator.validate_deployment()
        
        if args.check_users:
            validator.check_iam_users_status()
        
        if args.list_flagged:
            validator.list_flagged_users()
        
        if args.scan:
            validator.trigger_manual_scan()
        
        if args.test_notification:
            validator.test_notification()


if __name__ == '__main__':
    main()
