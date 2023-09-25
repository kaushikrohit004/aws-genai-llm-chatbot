import boto3
import openai
import genai_core.types
import genai_core.parameters

sts_client = boto3.client("sts")


def get_openai_client():
    api_key = genai_core.parameters.get_external_api_key("OPENAI_API_KEY")
    if not api_key:
        return None

    openai.api_key = api_key

    return openai


def get_sagemaker_client():
    client = boto3.client("sagemaker-runtime")

    return client


def get_bedrock_client():
    config = genai_core.parameters.get_config()
    bedrock_config = config.get("bedrock", {})
    bedrock_enabled = bedrock_config.get("enabled", False)
    if not bedrock_enabled:
        return None

    bedrock_config_data = {"service_name": "bedrock"}
    region_name = bedrock_config.get("region")
    endpoint_url = bedrock_config.get("endpointUrl")
    role_arn = bedrock_config.get("roleArn")

    if region_name:
        bedrock_config_data["region_name"] = region_name
    if endpoint_url:
        bedrock_config_data["endpoint_url"] = endpoint_url

    if role_arn:
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession",
        )

        credentials = assumed_role_object["Credentials"]
        bedrock_config_data["aws_access_key_id"] = credentials["AccessKeyId"]
        bedrock_config_data["aws_secret_access_key"] = credentials["SecretAccessKey"]
        bedrock_config_data["aws_session_token"] = credentials["SessionToken"]

    return boto3.client(**bedrock_config_data)
