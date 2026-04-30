"""Initial tables migration

Revision ID: 001
Revises: 
Create Date: 2024-04-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 schema
    op.execute("CREATE SCHEMA IF NOT EXISTS knowledgebot_knowledge")
    
    # 创建知识库表
    op.create_table(
        'knowledge_bases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('embedding_model', sa.String(100), server_default='bge-m3'),
        sa.Column('llm_model', sa.String(100), server_default='glm-4'),
        sa.Column('embedding_dim', sa.Integer(), server_default='1024'),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='knowledgebot_knowledge',
    )
    
    # 创建文档表
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('kb_id', sa.String(36), sa.ForeignKey('knowledgebot_knowledge.knowledge_bases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('chunk_count', sa.Integer(), server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='knowledgebot_knowledge',
    )
    
    # 创建索引
    op.create_index('idx_documents_kb_id', 'documents', ['kb_id'], schema='knowledgebot_knowledge')
    op.create_index('idx_documents_status', 'documents', ['status'], schema='knowledgebot_knowledge')
    op.create_index('idx_documents_file_hash', 'documents', ['file_hash'], schema='knowledgebot_knowledge')
    
    # 创建分块表
    op.create_table(
        'chunks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doc_id', sa.String(36), sa.ForeignKey('knowledgebot_knowledge.documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kb_id', sa.String(36), sa.ForeignKey('knowledgebot_knowledge.knowledge_bases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('vector_id', sa.BigInteger(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        schema='knowledgebot_knowledge',
    )
    
    # 创建索引
    op.create_index('idx_chunks_doc_id', 'chunks', ['doc_id'], schema='knowledgebot_knowledge')
    op.create_index('idx_chunks_kb_id', 'chunks', ['kb_id'], schema='knowledgebot_knowledge')
    op.create_index('idx_chunks_content_hash', 'chunks', ['content_hash'], schema='knowledgebot_knowledge')
    op.create_index('idx_chunks_vector_id', 'chunks', ['vector_id'], schema='knowledgebot_knowledge')


def downgrade() -> None:
    op.drop_table('chunks', schema='knowledgebot_knowledge')
    op.drop_table('documents', schema='knowledgebot_knowledge')
    op.drop_table('knowledge_bases', schema='knowledgebot_knowledge')
    op.execute("DROP SCHEMA IF EXISTS knowledgebot_knowledge CASCADE")