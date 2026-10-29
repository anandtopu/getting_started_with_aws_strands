"""Optional Tier 2 CDK labs. Construction/synthesis never deploys resources."""

from aws_cdk import CfnOutput, RemovalPolicy, Stack, Tags
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_bedrockagentcore as agentcore
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3vectors as vectors
from constructs import Construct

from common.config import course_value

PROJECT = "getting-started-with-aws-strands"


def bucket(scope: Construct, name: str, *, retention_days: int | None = None):
    result = s3.CfnBucket(
        scope,
        name,
        public_access_block_configuration=s3.CfnBucket.PublicAccessBlockConfigurationProperty(
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
        ),
        bucket_encryption=s3.CfnBucket.BucketEncryptionProperty(
            server_side_encryption_configuration=[
                s3.CfnBucket.ServerSideEncryptionRuleProperty(
                    server_side_encryption_by_default=s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                        sse_algorithm="AES256"
                    )
                )
            ]
        ),
        lifecycle_configuration=s3.CfnBucket.LifecycleConfigurationProperty(
            rules=[
                s3.CfnBucket.RuleProperty(
                    id="ExpireDemoSessions", status="Enabled", expiration_in_days=retention_days
                )
            ]
        )
        if retention_days
        else None,
    )
    result.apply_removal_policy(RemovalPolicy.DESTROY)
    return result


class KnowledgeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add("project", PROJECT)
        documents = bucket(self, "PolicyDocuments")
        vector_bucket = vectors.CfnVectorBucket(self, "PolicyVectors")
        index = vectors.CfnIndex(
            self,
            "PolicyIndex",
            vector_bucket_arn=vector_bucket.attr_vector_bucket_arn,
            index_name="nimbus-policies",
            data_type="float32",
            dimension=256,
            distance_metric="cosine",
            metadata_configuration=vectors.CfnIndex.MetadataConfigurationProperty(
                non_filterable_metadata_keys=["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
            ),
        )
        role = iam.Role(
            self,
            "KnowledgeRole",
            assumed_by=iam.ServicePrincipal(
                "bedrock.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                    "ArnLike": {
                        "aws:SourceArn": (
                            f"arn:{self.partition}:bedrock:{self.region}:{self.account}:knowledge-base/*"
                        )
                    },
                },
            ),
        )
        embedding_arn = (
            f"arn:{self.partition}:bedrock:{self.region}::foundation-model/"
            + course_value("BEDROCK_EMBEDDING_MODEL_ID")
        )
        # Invoke only the selected embedding model when ingesting/querying this knowledge base.
        role.add_to_policy(
            iam.PolicyStatement(actions=["bedrock:InvokeModel"], resources=[embedding_arn])
        )
        # Discover source objects under the one policy prefix; never scan other buckets.
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:ListBucket"],
                resources=[documents.attr_arn],
                conditions={"StringLike": {"s3:prefix": ["policies/", "policies/*"]}},
            )
        )
        # Read only the committed synthetic policy copies and their metadata sidecars.
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"], resources=[documents.attr_arn + "/policies/*"]
            )
        )
        # Bedrock needs metadata, ingestion, removal and similarity retrieval on this index.
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3vectors:GetIndex",
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:DeleteVectors",
                    "s3vectors:QueryVectors",
                ],
                resources=[index.attr_index_arn],
            )
        )
        knowledge = bedrock.CfnKnowledgeBase(
            self,
            "KnowledgeBase",
            name="nimbus-policies",
            role_arn=role.role_arn,
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=embedding_arn,
                    embedding_model_configuration=bedrock.CfnKnowledgeBase.EmbeddingModelConfigurationProperty(
                        bedrock_embedding_model_configuration=bedrock.CfnKnowledgeBase.BedrockEmbeddingModelConfigurationProperty(
                            dimensions=256, embedding_data_type="FLOAT32"
                        )
                    ),
                ),
            ),
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="S3_VECTORS",
                s3_vectors_configuration=bedrock.CfnKnowledgeBase.S3VectorsConfigurationProperty(
                    index_arn=index.attr_index_arn
                ),
            ),
        )
        knowledge.node.add_dependency(role)
        source = bedrock.CfnDataSource(
            self,
            "PolicySource",
            name="nimbus-policy-source",
            knowledge_base_id=knowledge.attr_knowledge_base_id,
            data_deletion_policy="DELETE",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=documents.attr_arn, inclusion_prefixes=["policies/"]
                ),
            ),
        )
        for name, value in {
            "DocumentsBucket": documents.ref,
            "VectorBucketArn": vector_bucket.attr_vector_bucket_arn,
            "VectorIndexArn": index.attr_index_arn,
            "KnowledgeBaseId": knowledge.attr_knowledge_base_id,
            "DataSourceId": source.attr_data_source_id,
        }.items():
            CfnOutput(self, name, value=value)


class SessionStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add("project", PROJECT)
        storage = bucket(self, "SessionStorage", retention_days=90)
        # Attach this managed policy only to the authenticated demo role; not a public principal.
        policy = iam.ManagedPolicy(
            self,
            "SessionAccess",
            statements=[
                # List only this demo customer's prefix to restore/delete session objects.
                iam.PolicyStatement(
                    actions=["s3:ListBucket"],
                    resources=[storage.attr_arn],
                    conditions={"StringLike": {"s3:prefix": ["CUS-001/*"]}},
                ),
                # Read/write/delete only this customer's demo session objects.
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    resources=[storage.attr_arn + "/CUS-001/*"],
                ),
            ],
        )
        CfnOutput(self, "SessionBucket", value=storage.ref)
        CfnOutput(self, "SessionPolicyArn", value=policy.managed_policy_arn)


class MemoryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add("project", PROJECT)
        memory = agentcore.CfnMemory(
            self,
            "Preferences",
            name="NimbusPreferences",
            event_expiry_duration=90,
            memory_strategies=[
                agentcore.CfnMemory.MemoryStrategyProperty(
                    user_preference_memory_strategy=agentcore.CfnMemory.UserPreferenceMemoryStrategyProperty(
                        name="TravelerPreferences", namespaces=["/preferences/{actorId}/"]
                    )
                )
            ],
        )
        CfnOutput(self, "MemoryId", value=memory.attr_memory_id)
        CfnOutput(self, "MemoryArn", value=memory.attr_memory_arn)
        # Attach only to the demo caller: recall this memory without event writes or deletion.
        policy = iam.ManagedPolicy(
            self,
            "MemoryRecallAccess",
            statements=[
                iam.PolicyStatement(
                    actions=["bedrock-agentcore:RetrieveMemoryRecords"],
                    resources=[memory.attr_memory_arn],
                )
            ],
        )
        CfnOutput(self, "MemoryRecallPolicyArn", value=policy.managed_policy_arn)
