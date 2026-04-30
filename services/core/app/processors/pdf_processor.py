"""PDF 文档处理器"""

import logging
from typing import Any

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF 文档处理器
    
    使用 PyMuPDF 解析 PDF 文档，提取文本内容。
    """
    
    def __init__(self, extract_images: bool = False, extract_tables: bool = False):
        """初始化 PDF 处理器
        
        Args:
            extract_images: 是否提取图片中的文本（OCR）
            extract_tables: 是否提取表格
        """
        self.extract_images = extract_images
        self.extract_tables = extract_tables
    
    def parse(self, file_path: str) -> dict[str, Any]:
        """解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            解析结果，包含：
            - text: 完整文本
            - pages: 页面列表
            - metadata: 文档元数据
        """
        try:
            doc = fitz.open(file_path)
            
            pages = []
            all_text = []
            
            for page_num, page in enumerate(doc):
                # 提取页面文本
                text = page.get_text("text")
                
                # 清理文本
                text = self._clean_text(text)
                
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                })
                
                all_text.append(text)
            
            # 提取元数据
            metadata = self._extract_metadata(doc)
            
            doc.close()
            
            return {
                "text": "\n\n".join(all_text),
                "pages": pages,
                "metadata": metadata,
                "total_pages": len(pages),
            }
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise
    
    def parse_with_layout(self, file_path: str) -> dict[str, Any]:
        """解析 PDF 文件并保留布局信息
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            解析结果，包含布局信息
        """
        try:
            doc = fitz.open(file_path)
            
            pages = []
            all_text = []
            
            for page_num, page in enumerate(doc):
                # 获取带布局的文本
                blocks = page.get_text("dict")["blocks"]
                
                page_content = []
                for block in blocks:
                    if block["type"] == 0:  # 文本块
                        block_text = ""
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                block_text += span.get("text", "")
                            block_text += "\n"
                        page_content.append(block_text.strip())
                
                text = "\n\n".join(page_content)
                text = self._clean_text(text)
                
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "blocks": blocks,
                })
                
                all_text.append(text)
            
            metadata = self._extract_metadata(doc)
            doc.close()
            
            return {
                "text": "\n\n".join(all_text),
                "pages": pages,
                "metadata": metadata,
                "total_pages": len(pages),
            }
            
        except Exception as e:
            logger.error(f"Failed to parse PDF with layout {file_path}: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def _extract_metadata(self, doc) -> dict[str, Any]:
        """提取 PDF 元数据
        
        Args:
            doc: PyMuPDF 文档对象
            
        Returns:
            元数据字典
        """
        metadata = doc.metadata
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": doc.page_count,
        }
    
    def extract_page_texts(self, file_path: str) -> list[str]:
        """提取每页的文本
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            每页文本列表
        """
        result = self.parse(file_path)
        return [page["text"] for page in result["pages"]]
