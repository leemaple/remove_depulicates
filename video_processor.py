import os
import logging
from typing import Optional
import ffmpeg

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """视频处理类，提供各种视频处理功能"""
    
    SUPPORTED_FORMATS = {'.mp4', '.mov', '.avi', '.mkv'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    def __init__(self, input_path: str):
        """
        初始化视频处理器
        
        Args:
            input_path: 输入视频文件路径
        """
        self.input_path = input_path
        self.validate_input()
        
    def validate_input(self) -> None:
        """验证输入文件的有效性"""
        if not os.path.exists(self.input_path):
            raise ValueError("输入文件不存在")
            
        file_size = os.path.getsize(self.input_path)
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制：{file_size} > {self.MAX_FILE_SIZE} bytes")
            
        ext = os.path.splitext(self.input_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的文件格式：{ext}")
    
    def process_video(
        self,
        output_path: str,
        rotation_angle: float = 2.0,
        frame_interval: int = 10,
        scale_factor: float = 1.03
    ) -> None:
        """
        处理视频：水平翻转、放大裁剪、旋转、删除非关键帧
        
        Args:
            output_path: 输出文件路径
            rotation_angle: 旋转角度（度）
            frame_interval: 非关键帧删除间隔
            scale_factor: 放大比例
        """
        try:
            # 获取输入视频信息
            probe = ffmpeg.probe(self.input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            fps = eval(video_info.get('r_frame_rate', '30/1'))
            
            # 计算放大后需要的裁剪区域
            scaled_width = int(width * scale_factor)
            scaled_height = int(height * scale_factor)
            crop_x = (scaled_width - width) // 2
            crop_y = (scaled_height - height) // 2
            
            # 构建滤镜链
            video_stream = ffmpeg.input(self.input_path)
            
            # 视频处理流程
            video_processed = (
                video_stream
                # 1. 水平翻转
                .filter('hflip')
                # 2. 放大
                .filter('scale', w=scaled_width, h=scaled_height)
                # 3. 裁剪回原始大小
                .filter('crop', w=width, h=height, x=crop_x, y=crop_y)
                # 4. 旋转
                .filter('rotate', angle=rotation_angle * 3.14159 / 180, fillcolor='black')
            )
            
            # 5. 删除每秒开始的一小段时间
            if frame_interval > 0:
                video_processed = (
                    video_processed
                    # 使用select过滤帧，每frame_interval帧保留frame_interval-1帧
                    .filter('select', expr=f'mod(n,{frame_interval})')
                    # 重新计算时间戳，保持原视频速度
                    .filter('setpts', 'N/FRAME_RATE/TB')
                )
            
            # 设置输出参数
            output_stream = ffmpeg.output(
                video_processed,
                output_path,
                vcodec='libx264',
                preset='medium',
                crf=23,
                r=fps,  # 保持原始帧率
                g=int(fps),  # GOP大小
                keyint_min=int(fps/2),  # 最小关键帧间隔
                an=None,  # 移除音频
                **{
                    'movflags': '+faststart',
                    'vsync': '1'  # 使用CFR模式
                }
            )
            
            # 执行处理
            logger.info(f"开始处理视频：{self.input_path}")
            logger.info(f"处理参数：rotation_angle={rotation_angle}, frame_interval={frame_interval}, scale_factor={scale_factor}")
            
            ffmpeg.run(output_stream, overwrite_output=True)
            logger.info(f"视频处理完成：{output_path}")
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
            logger.error(f"FFmpeg处理错误：{error_message}")
            if os.path.exists(output_path):
                os.remove(output_path)
                logger.info(f"已删除失败的输出文件：{output_path}")
            raise
        except Exception as e:
            logger.error(f"处理视频时发生错误：{str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
                logger.info(f"已删除失败的输出文件：{output_path}")
            raise
            
    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """
        获取视频文件信息
        
        Args:
            file_path: 视频文件路径
            
        Returns:
            包含视频信息的字典
        """
        try:
            probe = ffmpeg.probe(file_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                'width': int(video_info.get('width', 0)),
                'height': int(video_info.get('height', 0)),
                'duration': float(probe.get('format', {}).get('duration', 0)),
                'format': probe.get('format', {}).get('format_name', ''),
                'size': int(probe.get('format', {}).get('size', 0))
            }
        except Exception as e:
            logger.error(f"获取视频信息时发生错误：{str(e)}")
            raise 