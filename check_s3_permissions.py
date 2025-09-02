# --- IMPORTS ---
import boto3
from botocore.exceptions import ClientError

# --- AUTHOR ---
# Author: Daniel Chisasura

# --- FUNCTION DEFINITION ---
def check_s3_permissions():
    """
    Scans all S3 buckets in the AWS account and identifies those with public access
    granted via Access Control Lists (ACLs). It then prints a summary of the findings.
    """
    # --- INITIALIZATION ---
    print("🔍 Starting scan for public S3 buckets...")

    # --- MODIFICATION FOR MOTO ---
    # Point the S3 client to the local Moto server endpoint.
    # Dummy credentials are provided as a best practice for local testing.
    s3_client = boto3.client(
        's3',
        endpoint_url='http://127.0.0.1:5000',
        aws_access_key_id='testing',      # Dummy Access Key
        aws_secret_access_key='testing',  # Dummy Secret Key
        region_name='us-east-1'           # Dummy Region
    )
    # --- END MODIFICATION ---

    public_buckets = []

    # --- LIST BUCKETS ---
    try:
        response = s3_client.list_buckets()
    except ClientError as e:
        print(f"🚫 Error listing buckets: {e}")
        return

    # --- BUCKET ITERATION AND ACL CHECKING ---
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        print(f"Checking bucket: {bucket_name}...")

        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)

            for grant in acl['Grants']:
                grantee = grant.get('Grantee', {})
                grantee_uri = grantee.get('URI', '')

                if 'http://acs.amazonaws.com/groups/global/AllUsers' in grantee_uri:
                    public_buckets.append(bucket_name)
                    break

        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print(f"⚠️  Access Denied for bucket: {bucket_name}. Cannot assess its permissions.")
            else:
                print(f"🚫 An unexpected error occurred for bucket {bucket_name}: {e}")

    # --- REPORTING RESULTS ---
    print("\n-------------------------------------------------")
    print("✅ Scan complete.")

    if public_buckets:
        print("🚨 The following S3 buckets are PUBLICLY ACCESSIBLE:")
        for bucket_name in sorted(public_buckets):
            print(f"  - {bucket_name}")
    else:
        print("✅ No publicly accessible S3 buckets were found.")
    print("-------------------------------------------------")


# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    check_s3_permissions()