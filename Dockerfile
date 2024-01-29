FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY *py ./
RUN apt update && apt install libgl1-mesa-glx ffmpeg -y

RUN python -c "from ultralytics import YOLO; YOLO('yolov8x.pt')"
RUN python -c "import whisper; whisper.load_model('small')"
RUN mkdir temp
CMD ["python","telegram_bot.py"]

