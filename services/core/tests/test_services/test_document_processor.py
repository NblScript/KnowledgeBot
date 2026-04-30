"""文档处理服务测试"""

import pytest

from app.services.document_processor import (
    ChunkData,
    DocumentParser,
    DocumentProcessor,
    MarkdownParser,
    ParsedDocument,
    TextChunker,
    TextParser,
)


@pytest.mark.asyncio
async def test_text_parser():
    """测试纯文本解析"""
    parser = TextParser()
    content = b"Hello, world!\nThis is a test document."
    
    result = await parser.parse(content, "test.txt")
    
    assert result.file_type == "txt"
    assert result.file_name == "test.txt"
    assert "Hello" in result.content
    assert result.metadata["encoding"] == "utf-8"


@pytest.mark.asyncio
async def test_markdown_parser():
    """测试 Markdown 解析"""
    parser = MarkdownParser()
    content = b"# Title\n\n## Subtitle\n\nSome content here."
    
    result = await parser.parse(content, "test.md")
    
    assert result.file_type == "md"
    assert "Title" in result.content
    assert result.metadata["headers"] == ["Title", "Subtitle"]


@pytest.mark.asyncio
async def test_markdown_parser_no_headers():
    """测试无标题的 Markdown"""
    parser = MarkdownParser()
    content = b"Just some plain text without headers."
    
    result = await parser.parse(content, "plain.md")
    
    assert result.file_type == "md"
    assert "plain text" in result.content
    assert result.metadata["headers"] == []


def test_text_chunker_basic():
    """测试基本分块"""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "This is sentence one.\n\nThis is sentence two.\n\nThis is sentence three."
    
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 0
    assert all(isinstance(c, ChunkData) for c in chunks)
    assert all(c.content.strip() for c in chunks)
    
    # 检查分块索引
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_text_chunker_empty():
    """测试空文本"""
    chunker = TextChunker()
    
    chunks = chunker.chunk("")
    assert chunks == []
    
    chunks = chunker.chunk("   \n\n  ")
    assert chunks == []


def test_text_chunker_long_paragraph():
    """测试长段落分块"""
    chunker = TextChunker(chunk_size=50)
    # 创建带句子分隔符的长文本（分块器按句子分割）
    text = "First sentence here. " * 10 + "\n\n" + "Second sentence here. " * 10
    
    chunks = chunker.chunk(text)
    
    # 应该被分成多个块
    assert len(chunks) >= 2


def test_text_chunker_token_count():
    """测试 token 估算"""
    chunker = TextChunker()
    
    # 中文文本
    chinese_text = "这是一个测试文档，用于验证中文分块功能。"
    chunks = chunker.chunk(chinese_text)
    
    if chunks:
        # 中文 token 数应该约为字符数的 2/3
        assert chunks[0].token_count > 0
    
    # 英文文本
    english_text = "This is an English test document for chunking verification."
    chunks = chunker.chunk(english_text)
    
    if chunks:
        assert chunks[0].token_count > 0


@pytest.mark.asyncio
async def test_document_processor_text():
    """测试文档处理器处理纯文本"""
    processor = DocumentProcessor()
    
    content = b"Line one.\n\nLine two.\n\nLine three."
    result, chunks = await processor.process(content, "test.txt", "txt")
    
    assert result.file_type == "txt"
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_document_processor_markdown():
    """测试文档处理器处理 Markdown"""
    processor = DocumentProcessor()
    
    content = b"# Main Title\n\nContent paragraph one.\n\nContent paragraph two."
    result, chunks = await processor.process(content, "doc.md", "md")
    
    assert result.file_type == "md"
    assert "Main Title" in result.content


def test_get_parser():
    """测试获取解析器"""
    parser = DocumentParser.get_parser("txt")
    assert isinstance(parser, TextParser)
    
    parser = DocumentParser.get_parser("md")
    assert isinstance(parser, MarkdownParser)
    
    # 不支持的类型
    with pytest.raises(ValueError):
        DocumentParser.get_parser("xyz")


def test_chunk_data_creation():
    """测试 ChunkData 创建"""
    chunk = ChunkData(
        content="Test content",
        chunk_index=0,
        token_count=10,
    )
    
    assert chunk.content == "Test content"
    assert chunk.chunk_index == 0
    assert chunk.token_count == 10
    assert chunk.metadata == {}  # 默认空字典
    
    # 带元数据
    chunk = ChunkData(
        content="Test",
        chunk_index=1,
        token_count=5,
        metadata={"page": 1},
    )
    
    assert chunk.metadata == {"page": 1}


def test_parsed_document_creation():
    """测试 ParsedDocument 创建"""
    doc = ParsedDocument(
        content="Document content",
        file_name="test.txt",
        file_type="txt",
    )
    
    assert doc.content == "Document content"
    assert doc.metadata == {}
    
    doc = ParsedDocument(
        content="Content",
        file_name="doc.md",
        file_type="md",
        metadata={"headers": ["Title"]},
    )
    
    assert doc.metadata == {"headers": ["Title"]}