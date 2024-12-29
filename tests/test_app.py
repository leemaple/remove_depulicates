import os
import pytest
from fastapi.testclient import TestClient
from main import app
from video_processor import VideoProcessor

client = TestClient(app)

def test_read_root():
    """测试主页访问"""
    response = client.get("/")
    assert response.status_code == 200
    assert "视频处理服务" in response.text

def test_invalid_video_format():
    """测试上传无效格式的文件"""
    files = {
        "video": ("test.txt", b"test content", "text/plain")
    }
    data = {
        "rotation_angle": "2.0",
        "frame_interval": "10"
    }
    response = client.post("/upload", files=files, data=data)
    assert response.status_code == 500
    assert "不支持的文件格式" in response.json()["detail"]

def test_download_nonexistent_file():
    """测试下载不存在的文件"""
    response = client.get("/download/nonexistent.mp4")
    assert response.status_code == 404
    assert "文件不存在" in response.json()["detail"]

def test_cleanup_nonexistent_file():
    """测试清理不存在的文件"""
    response = client.delete("/cleanup/nonexistent.mp4")
    assert response.status_code == 200
    assert response.json()["message"] == "文件不存在"

def test_video_processor_validation():
    """测试VideoProcessor的输入验证"""
    with pytest.raises(ValueError, match="输入文件不存在"):
        VideoProcessor("nonexistent.mp4")

def test_video_info():
    """测试视频信息获取（需要提供测试视频文件）"""
    # 注意：这个测试需要一个实际的视频文件才能运行
    # test_video_path = "path/to/test/video.mp4"
    # if os.path.exists(test_video_path):
    #     info = VideoProcessor.get_video_info(test_video_path)
    #     assert isinstance(info, dict)
    #     assert "width" in info
    #     assert "height" in info
    #     assert "duration" in info
    pass  # 暂时跳过实际视频文件测试 