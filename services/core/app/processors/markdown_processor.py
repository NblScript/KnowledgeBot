"""Markdown 文档处理器"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """Markdown 文档处理器
    
    解析 Markdown 文件，提取文本和结构信息。
    """
    
    # 标题正则
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    
    # 代码块正则
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    
    # 链接正则
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    
    # 图片正则
    IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    
    def __init__(
        self,
        extract_code_blocks: bool = True,
        extract_links: bool = True,
        extract_images: bool = False,
    ):
        """初始化 Markdown 处理器
        
        Args:
            extract_code_blocks: 是否提取代码块
            extract_links: 是否提取链接
            extract_images: 是否提取图片信息
        """
        self.extract_code_blocks = extract_code_blocks
        self.extract_links = extract_links
        self.extract_images = extract_images
    
    def parse(self, file_path: str) -> dict[str, Any]:
        """解析 Markdown 文件
        
        Args:
            file_path: Markdown 文件路径
            
        Returns:
            解析结果，包含：
            - text: 纯文本内容
            - sections: 章节列表
            - code_blocks: 代码块列表
            - links: 链接列表
            - metadata: 元数据
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取结构
            sections = self._extract_sections(content)
            code_blocks = self._extract_code_blocks(content) if self.extract_code_blocks else []
            links = self._extract_links(content) if self.extract_links else []
            images = self._extract_images(content) if self.extract_images else []
            
            # 转换为纯文本
            plain_text = self._to_plain_text(content)
            
            # 提取 frontmatter (YAML)
            metadata = self._extract_frontmatter(content)
            
            return {
                "text": plain_text,
                "raw_content": content,
                "sections": sections,
                "code_blocks": code_blocks,
                "links": links,
                "images": images,
                "metadata": metadata,
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Markdown {file_path}: {e}")
            raise
    
    def parse_to_chunks(self, file_path: str, chunk_by_section: bool = True) -> list[dict[str, Any]]:
        """解析 Markdown 文件并按章节分块
        
        Args:
            file_path: Markdown 文件路径
            chunk_by_section: 是否按章节分块
            
        Returns:
            分块列表
        """
        result = self.parse(file_path)
        
        if not chunk_by_section:
            # 返回整个文档作为一个块
            return [{
                "content": result["text"],
                "metadata": result["metadata"],
            }]
        
        chunks = []
        for section in result["sections"]:
            chunks.append({
                "content": section["content"],
                "metadata": {
                    "title": section["title"],
                    "level": section["level"],
                    **result["metadata"],
                },
            })
        
        return chunks
    
    def _extract_sections(self, content: str) -> list[dict[str, Any]]:
        """提取章节结构"""
        lines = content.split("\n")
        sections = []
        current_section = {
            "title": "文档开头",
            "level": 0,
            "content": [],
            "start_line": 0,
        }
        
        for i, line in enumerate(lines):
            heading_match = self.HEADING_PATTERN.match(line)
            
            if heading_match:
                # 保存当前 section
                sections.append({
                    "title": current_section["title"],
                    "level": current_section["level"],
                    "content": "\n".join(current_section["content"]).strip(),
                    "start_line": current_section["start_line"],
                    "end_line": i - 1,
                })
                
                # 开始新 section
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                current_section = {
                    "title": title,
                    "level": level,
                    "content": [],
                    "start_line": i,
                }
            else:
                current_section["content"].append(line)
        
        # 添加最后一个 section
        sections.append({
            "title": current_section["title"],
            "level": current_section["level"],
            "content": "\n".join(current_section["content"]).strip(),
            "start_line": current_section["start_line"],
            "end_line": len(lines) - 1,
        })
        
        # 过滤空章节
        sections = [s for s in sections if s["content"]]
        
        return sections
    
    def _extract_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """提取代码块"""
        code_blocks = []
        
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            block = match.group(0)
            # 提取语言
            lang_match = re.match(r"```(\w+)?", block)
            language = lang_match.group(1) if lang_match else "unknown"
            
            # 提取代码内容
            code = re.sub(r"^```\w*\n?", "", block)
            code = re.sub(r"\n?```$", "", code)
            
            code_blocks.append({
                "language": language,
                "code": code.strip(),
                "full_block": block,
            })
        
        return code_blocks
    
    def _extract_links(self, content: str) -> list[dict[str, Any]]:
        """提取链接"""
        links = []
        
        for match in self.LINK_PATTERN.finditer(content):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
            })
        
        return links
    
    def _extract_images(self, content: str) -> list[dict[str, Any]]:
        """提取图片"""
        images = []
        
        for match in self.IMAGE_PATTERN.finditer(content):
            images.append({
                "alt_text": match.group(1),
                "url": match.group(2),
            })
        
        return images
    
    def _to_plain_text(self, content: str) -> str:
        """转换为纯文本
        
        移除 Markdown 语法，保留文本内容。
        """
        text = content
        
        # 移除代码块
        text = self.CODE_BLOCK_PATTERN.sub("", text)
        
        # 移除图片
        text = self.IMAGE_PATTERN.sub("", text)
        
        # 转换链接为纯文本
        text = self.LINK_PATTERN.sub(r"\1", text)
        
        # 移除标题标记
        text = self.HEADING_PATTERN.sub(r"\2", text)
        
        # 移除粗体和斜体
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        
        # 移除删除线
        text = re.sub(r"~~([^~]+)~~", r"\1", text)
        
        # 移除行内代码
        text = re.sub(r"`([^`]+)`", r"\1", text)
        
        # 移除引用标记
        text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)
        
        # 移除列表标记
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        
        # 移除水平线
        text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
        
        # 清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text.strip()
    
    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """提取 YAML frontmatter"""
        metadata = {}
        
        # 检查是否有 frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                
                # 简单解析 YAML (仅支持键值对)
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
