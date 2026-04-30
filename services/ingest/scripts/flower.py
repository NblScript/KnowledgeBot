#!/usr/bin/env python
"""Celery Flower 启动脚本（Web 监控界面）"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.celery_app import celery_app

if __name__ == "__main__":
    from flower.command import flower_command
    
    flower_command(celery_app, port=5555, address="0.0.0.0")