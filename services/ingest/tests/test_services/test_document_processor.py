"""测试文档处理器"""

import pytest
from app.services.document_processor import (
    ChunkData,
    DocumentParser,
    DocumentProcessor,
    ParsedDocument,
    TextParser,
    MarkdownParser,
    TextChunker,
    get_processor,
)


class TestTextParser:
    """测试文本解析器"""
    
    @pytest.mark.asyncio
    async def test_parse_plain_text(self):
        """测试解析纯文本"""
        parser = TextParser()
        content = b"Hello, World!\nThis is a test."
        
        result = await parser.parse(content, "test.txt")
        
        assert isinstance(result, ParsedDocument)
        assert result.content == "Hello, World!\nThis is a test."
        assert result.file_type == "txt"
        assert result.metadata.get("encoding") == "utf-8"


class TestMarkdownParser:
    """测试 Markdown 解析器"""
    
    @pytest.mark.asyncio
    async def test_parse_markdown(self):
        """测试解析 Markdown"""
        parser = MarkdownParser()
        content = b"# Title\n\n## Subtitle\n\nContent here"
        
        result = await parser.parse(content, "test.md")
        
        assert isinstance(result, ParsedDocument)
        assert result.file_type == "md"
        assert "Title" in result.metadata.get("headers", [])


class TestTextChunker:
    """测试文本分块器"""
    
    def test_chunk_empty_text(self):
        """测试空文本分块"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk("")
        
        assert len(chunks) == 0
    
    def test_chunk_short_text(self):
        """测试短文本分块"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        text = "This is a short text."
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text
        assert chunks[0].chunk_index == 0
    
    def test_chunk_long_text(self):
        """测试长文本分块"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert len(chunk.content) <= 50 or len(chunks) == 1  # 允许最后一个块略大
    
    def test_chunk_token_count(self):
        """测试 token 计数"""
        chunker = TextChunker()
        text = "这是一段中文文本。"
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].token_count > 0


class TestDocumentProcessor:
    """测试文档处理器"""
    
    @pytest.mark.asyncio
    async def test_process_text_document(self):
        """测试处理文本文档"""
        processor = DocumentProcessor()
        content = b"Hello, World!\n\nThis is a test document."
        
        parsed, chunks = await processor.process(
            content=content,
            file_name="test.txt",
            file_type="txt",
        )
        
        assert isinstance(parsed, ParsedDocument)
        assert len(chunks) >= 1
        assert parsed.file_type == "txt"
    
    @pytest.mark.asyncio
    async def test_process_markdown_document(self):
        """测试处理 Markdown 文档"""
        processor = DocumentProcessor()
        content = b"# Title\n\nContent here"
        
        parsed, chunks = await processor.process(
            content=content,
            file_name="test.md",
            file_type="md",
        )
        
        assert parsed.file_type == "md"
        assert len(chunks) >= 1


class TestDocumentParser:
    """测试文档解析器工厂"""
    
    def test_get_text_parser(self):
        """测试获取文本解析器"""
        parser = DocumentParser.get_parser("txt")
        assert isinstance(parser, TextParser)
    
    def test_get_markdown_parser(self):
        """测试获取 Markdown 解析器"""
        parser = DocumentParser.get_parser("md")
        assert isinstance(parser, MarkdownParser)
    
    def test_get_unsupported_parser(self):
        """测试获取不支持的解析器"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            DocumentParser.get_parser("xyz")