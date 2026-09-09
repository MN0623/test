import sys
import cv2

# demo.py と tu.py から必要なモジュールをインポート
try:
    import demo
    import tu
except ImportError as e:
    print(f"モジュールのインポートエラー: {e}")
    print("app.py と同じディレクトリに demo.py と tu.py があるか確認してください。")
    sys.exit(1)


def main():
    print("==============================")
    print("  How to Fold an Origami Heart")
    print("==============================")

    # tu.py にある OrigamiTutor インスタンスを作成
    tutor = tu.OrigamiTutor(tu.STEPS)

    # 全ステップが完了するまでループ
    while not tutor.is_finished():
        # 1. 現在のステップの指示をターミナルに表示
        tutor.show_instruction()

        # 2. 現在のステップ番号を取得 (1, 2, 3...)
        current_step_num = tutor.get_current_step_number()

        if current_step_num is None:
            break

        print(f"\n[CV Check] Step {current_step_num} の画像認識を開始します...")

        try:
            # 3. demo.py の判定関数を呼び出す
            is_cleared = demo.check_Origami(current_step_num)
        except Exception as e:
            print(f"demo.check_Origami の実行中にエラーが発生しました: {e}")
            break

        # 4. CVの判定結果を OrigamiTutor に渡す
        #    (True なら自動的に次のステップへ進み、False なら同じステップに留まります)
        tutor.receive_cv_result(is_cleared)

        # 判定が失敗（または'q'キー等で中断）された場合の安全処理
        if not is_cleared:
            print("ユーザーにより中断されたか、判定をクリアできませんでした。")
            break

    print("\n=== アプリケーションを終了します ===")


if __name__ == "__main__":
    main()
