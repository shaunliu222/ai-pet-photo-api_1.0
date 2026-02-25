#!/usr/bin/env python3
"""
AI合照生图-智能体 主程序

让潜在领养者与流浪宠物生成温馨的亲密合照
"""
import os
import sys

from config import PETS_DIR, OUTPUT_DIR, INTERACTION_TEMPLATES
from utils import (
    ensure_dir, list_pet_images, print_banner, print_interaction_menu,
    generate_output_filename
)
from image_analyzer import analyze_images
from image_generator import generate_image


def get_user_photo() -> str:
    """获取用户照片路径"""
    print("\n📷 请提供您的照片：")
    print("   1. 输入本地图片路径")
    print("   2. 使用示例图片（测试用）")

    choice = input("\n请选择 [1/2]: ").strip()

    if choice == "1":
        path = input("请输入图片路径: ").strip()
        # 处理可能的引号
        path = path.strip('"').strip("'")

        if os.path.exists(path):
            return path
        else:
            print(f"❌ 文件不存在: {path}")
            return get_user_photo()
    elif choice == "2":
        # 返回一个示例路径（实际使用时需要准备示例图片）
        return "example_user.jpg"
    else:
        print("无效选择，请重试")
        return get_user_photo()


def get_pet_photo() -> str:
    """获取宠物照片路径"""
    ensure_dir(PETS_DIR)
    pet_images = list_pet_images(PETS_DIR)

    print("\n🐾 请选择宠物照片：")

    if pet_images:
        print("   1. 从宠物库中选择")
        print("   2. 输入本地图片路径")

        choice = input("\n请选择 [1/2]: ").strip()

        if choice == "1":
            print("\n宠物库中的图片：")
            for idx, img in enumerate(pet_images, 1):
                filename = os.path.basename(img)
                print(f"   {idx}. {filename}")

            sel = input("\n请选择编号: ").strip()
            try:
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(pet_images):
                    return pet_images[sel_idx]
            except ValueError:
                pass

            print("无效选择")
            return get_pet_photo()
        elif choice == "2":
            path = input("请输入图片路径: ").strip()
            path = path.strip('"').strip("'")

            if os.path.exists(path):
                return path
            else:
                print(f"❌ 文件不存在: {path}")
                return get_pet_photo()
    else:
        print("   (宠物库为空)")
        path = input("请输入宠物图片路径: ").strip()
        path = path.strip('"').strip("'")

        if os.path.exists(path):
            return path
        else:
            print(f"❌ 文件不存在: {path}")
            return get_pet_photo()


def get_interaction_scene() -> str:
    """获取互动场景选择"""
    print_interaction_menu()

    while True:
        choice = input("\n请选择场景 [1-5]: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(INTERACTION_TEMPLATES):
                selected = INTERACTION_TEMPLATES[idx]
                print(f"\n✓ 已选择: {selected['name']}")
                return selected["id"]
        except ValueError:
            pass

        print("无效选择，请重试")


def generate_intimate_photo(user_photo: str, pet_photo: str, interaction_id: str) -> str:
    """
    生成亲密合照的主流程

    Args:
        user_photo: 用户照片路径
        pet_photo: 宠物照片路径
        interaction_id: 互动场景ID

    Returns:
        生成图片的保存路径
    """
    print("\n" + "=" * 50)
    print("🎬 开始生成亲密合照")
    print("=" * 50)

    # Step 1: 分析图片，生成提示词
    print("\n📊 Step 1: 分析照片特征...")
    print(f"   用户照片: {os.path.basename(user_photo)}")
    print(f"   宠物照片: {os.path.basename(pet_photo)}")

    try:
        prompt = analyze_images(user_photo, pet_photo, interaction_id)
        print("\n✓ 提示词生成成功！")
        print("-" * 50)
        print(f"📝 生成的提示词:\n{prompt}")
        print("-" * 50)
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        raise

    # Step 2: 生成图像
    print("\n🎨 Step 2: 生成图像...")
    try:
        output_path = generate_image(prompt)
        print("\n" + "=" * 50)
        print("🎉 生成完成！")
        print("=" * 50)
        print(f"📁 图片已保存至: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        raise


def main():
    """主函数"""
    print_banner()

    # 确保目录存在
    ensure_dir(PETS_DIR)
    ensure_dir(OUTPUT_DIR)

    print("欢迎使用 AI合照生图-智能体！")
    print("这个工具帮助您与可爱的流浪宠物生成温馨的亲密合照，")
    print("让您提前感受未来领养生活的美好憧憬。\n")

    while True:
        try:
            # 获取用户照片
            user_photo = get_user_photo()

            # 获取宠物照片
            pet_photo = get_pet_photo()

            # 选择互动场景
            interaction_id = get_interaction_scene()

            # 生成合照
            output_path = generate_intimate_photo(user_photo, pet_photo, interaction_id)

            # 询问是否继续
            print("\n" + "-" * 50)
            continue_choice = input("是否继续生成其他合照？[y/N]: ").strip().lower()
            if continue_choice != 'y':
                print("\n感谢使用！愿每一只流浪宠物都能找到温暖的家 🏠")
                break

        except KeyboardInterrupt:
            print("\n\n已取消")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            retry = input("是否重试？[Y/n]: ").strip().lower()
            if retry == 'n':
                break


if __name__ == "__main__":
    main()
