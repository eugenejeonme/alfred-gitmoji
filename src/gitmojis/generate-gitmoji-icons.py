#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from PIL import Image, ImageDraw, ImageFont

def generate_emoji_icons(gitmojis, output_dir="./assets/icons"):
    print(f"Starting icon generation in {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # macOS의 이모지 폰트 사용
    potential_fonts = [
      "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
      "/System/Library/Fonts/AppleColorEmoji.ttf",    # 다른 macOS 버전
      "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
      "C:\\Windows\\Fonts\\seguiemj.ttf"              # Windows
    ]
    font_path = None
    for path in potential_fonts:
      if os.path.exists(path):
        font_path = path
        break

    if not font_path:
      print("Error: 이모지 폰트를 찾을 수 없습니다.")
      return 0

    font_size = 32

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Font loading error: {e}")
        return

    for gitmoji in gitmojis:
        emoji = gitmoji["emoji"]
        name = gitmoji["name"]
        output_path = os.path.join(output_dir, f"{name}.png")

        if os.path.exists(output_path):
            print(f"Skipping {output_path} - already exists")
            continue

        print(f"Generating icon at: {output_path}")
        # 이미지 크기 설정 (이모지가 잘리지 않도록 약간 여유 있게)
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 텍스트를 중앙에 배치
        draw.text((2, 0), emoji, font=font, embedded_color=True)
        img.save(output_path)
        print(f"Generated {output_path}")

def load_gitmojis(json_path="./assets/gitmojis.json"):
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def main():
    gitmojis = load_gitmojis()
    if gitmojis:
        generate_emoji_icons(gitmojis)
    else:
        print("No gitmojis loaded. Exiting.")

if __name__ == "__main__":
    main()
