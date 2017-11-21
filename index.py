import json
import boto3

# AWS Config resource
# Ref: http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html
APPLICABLE_RESOURCES = ['AWS::EC2::Instance']

def handler(event, context):

    # Gather event JSON and evaluate
    invoking_event      = json.loads(event['invokingEvent'])
    configuration_item  = invoking_event['configurationItem']
    rule_parameters     = json.loads(event['ruleParameters'])
    evaluation          = evaluate_compliance(configuration_item, rule_parameters)

    # Push evaluation to AWS Config
    config = boto3.client('config')
    config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType':   configuration_item['resourceType'],
                'ComplianceResourceId':     configuration_item['resourceId'],
                'ComplianceType':           evaluation['compliance_type'],
                'Annotation':               evaluation['annotation'],
                'OrderingTimestamp':        configuration_item['configurationItemCaptureTime'],
            },
        ],
        ResultToken=event['resultToken']
    )

def evaluate_compliance(configuration_item, rule_parameters):

    # Check resource type
    if configuration_item['resourceType'] not in APPLICABLE_RESOURCES:
        return {
            'compliance_type':  'NOT_APPLICABLE',
            'annotation':       'Not applicable to this resoure type',
        }

    # Check resource status
    if configuration_item['configurationItemStatus'] == 'ResourceDeleted':
        return {
            'compliance_type':  'NOT_APPLICABLE',
            'annotation':       'Configuration item no longer exists',
        }

    # Get raw configuration
    raw_regions      = rule_parameters.get('REGIONS', 'us-east-1')
    raw_fail_empty   = rule_parameters.get('FAIL_EMPTY', '1')

    # Transform configuration
    regions     = raw_regions.split(',')
    fail_empty  = False if raw_fail_empty.lower() in ('0', 'false', 'f') else True

    # Get name from this instance
    this_instance_name = configuration_item['tags'].get('Name', '')

    # If empty, return based on fail_empty
    if this_instance_name == '':
        return {
            'compliance_type':  'NON_COMPLIANT' if fail_empty else 'COMPLIANT',
            'annotation':       'Instance has empty \'Name\' tag'
        }

    # ASSERT: name tag not empty

    # Check if any other instance has this tag
    ec2 = boto3.client('ec2')
    describe_instances = ec2.describe_instances(
        Filters=[
            {
                'Name':     'tag:Name',
                'Values':   [this_instance_name,]
            },
        ]
    )

    # Count instances
    instance_count = 0
    for r in describe_instances.get('Reservations', []):
        instance_count += len(r['Instances'])

    # Handle non-complaint states first

    # If none, there's a fatal error
    if instance_count == 0:
        return {
            'compliance_type':  'NON_COMPLIANT',
            'annotation':       'No instance was found with \'Name\' tag of \'{}\''.format(this_instance_name)
        }

    # If more than 1, this is a duplicate
    if instance_count > 1:
        return {
            'compliance_type':  'NON_COMPLIANT',
            'annotation':       'Found {} instances with \'Name\' tag of \'{}\''.format(instance_count, this_instance_name)
        }

    # ASSERT: Only one instance returned
    return {
        'compliance_type':  'COMPLIANT',
        'annotation':       'Only one instance was found with \'Name\' tag of \'{}\''.format(this_instance_name)
    }
