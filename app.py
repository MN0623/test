import sys
import cv2

# demo.py と tu.py から必要な関数/クラスをインポート
try:
    import demo
    import tu
except ImportError as e:
    print(f"モジュールのインポートエラー: {e}")
    print("app.py と同じディレクトリに demo.py と tu.py があるか確認してください。")
    sys.exit(1)


def main():
    print("=== Origami Recognition App Start ===")
    print("操作方法:")
    print(" - 'n': 次のステップへスキップ")
    print(" - 'q': アプリケーションを終了")
    print("-------------------------------------")

    # Step 1 から Step 4 まで順番に処理
    total_steps = 4
    
    for step_num in range(1, total_steps + 1):
        print(f"\n>>> [Step {step_num} / {total_steps}] を開始します...")
        
        # tu.py に初期化関数やガイド表示関数がある場合の呼び出し例
        if hasattr(tu, "show_instruction"):
            tu.show_instruction(step_num)

        # demo.py の判定関数を実行 (Trueが返ってきたらクリア)
        is_cleared = demo.check_Origami(step_num)

        if is_cleared:
            print(f"★ Step {step_num} クリア！")
            
            # tu.py にクリア演出等の処理がある場合の呼び出し例
            if hasattr(tu, "on_step_cleared"):
                tu.on_step_cleared(step_num)
        else:
            print(f"Step {step_num} が中断されたか、判定に失敗しました。")
            break

    print("\n=== すべてのステップが終了しました ===")


if __name__ == "__main__":
    main()
