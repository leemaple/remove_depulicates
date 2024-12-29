import os
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import logging
from video_processor import VideoProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建必要的目录
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="视频处理服务")

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """渲染主页"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/upload")
async def upload_video(
    video: UploadFile = File(...),
    rotation_angle: float = Form(2.0),
    frame_interval: int = Form(10)
):
    """
    处理上传的视频文件
    
    Args:
        video: 上传的视频文件
        rotation_angle: 旋转角度
        frame_interval: 非关键帧删除间隔
    
    Returns:
        包含处理结果的JSON响应
    """
    try:
        # 生成唯一文件名
        input_filename = f"{uuid.uuid4()}{os.path.splitext(video.filename)[1]}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)
        
        # 保存上传的文件
        with open(input_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        # 设置输出路径
        output_filename = f"processed_{input_filename.rsplit('.', 1)[0]}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 处理视频
        processor = VideoProcessor(input_path)
        processor.process_video(
            output_path=output_path,
            rotation_angle=rotation_angle,
            frame_interval=frame_interval
        )
        
        # 获取处理后的视频信息
        video_info = VideoProcessor.get_video_info(output_path)
        
        # 清理上传的原始文件
        os.remove(input_path)
        
        return {
            "status": "success",
            "message": "视频处理完成",
            "output_filename": output_filename,
            "video_info": video_info
        }
        
    except Exception as e:
        logger.error(f"处理视频时发生错误：{str(e)}")
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_video(filename: str):
    """
    下载处理后的视频
    
    Args:
        filename: 视频文件名
    
    Returns:
        视频文件响应
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )

@app.delete("/cleanup/{filename}")
async def cleanup_file(filename: str):
    """
    清理处理后的视频文件
    
    Args:
        filename: 要删除的文件名
    
    Returns:
        操作结果
    """
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": "success", "message": "文件已删除"}
        return {"status": "success", "message": "文件不存在"}
    except Exception as e:
        logger.error(f"删除文件时发生错误：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 